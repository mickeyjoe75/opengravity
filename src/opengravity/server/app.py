import json
import asyncio
import os as _os
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from opengravity.server.session import SessionManager
from opengravity.providers.configs import PROVIDERS, get_provider_config
from opengravity.providers.registry import ProviderRegistry
from opengravity.core.agent import Agent
from opengravity.core.types import StreamChunk

app = FastAPI(title="OpenGravity", version="0.1.0")

# CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_manager = SessionManager()

# === API Key Persistence (Google Cloud Storage) ===
_GCS_BUCKET = _os.environ.get("OPENGRAVITY_CONFIG_BUCKET", "opengravity-config")
_GCS_KEY_FILE = "api_keys.json"

def _get_gcs_client():
    """Get GCS client, returns None if not available."""
    try:
        from google.cloud import storage
        return storage.Client()
    except Exception:
        return None

def _load_saved_keys():
    """Load saved API keys from GCS and inject into environment."""
    try:
        client = _get_gcs_client()
        if client:
            bucket = client.bucket(_GCS_BUCKET)
            blob = bucket.blob(_GCS_KEY_FILE)
            if blob.exists():
                keys = json.loads(blob.download_as_text())
                for env_var, value in keys.items():
                    if value and not _os.environ.get(env_var):
                        _os.environ[env_var] = value
                return
    except Exception:
        pass
    # Fallback: try local file
    local_file = Path.home() / ".opengravity" / "api_keys.json"
    if local_file.exists():
        try:
            keys = json.loads(local_file.read_text())
            for env_var, value in keys.items():
                if value and not _os.environ.get(env_var):
                    _os.environ[env_var] = value
        except Exception:
            pass

def _save_keys(keys: dict[str, str]):
    """Save API keys to GCS (persistent across restarts)."""
    # Load existing keys
    existing = {}
    try:
        client = _get_gcs_client()
        if client:
            bucket = client.bucket(_GCS_BUCKET)
            blob = bucket.blob(_GCS_KEY_FILE)
            if blob.exists():
                existing = json.loads(blob.download_as_text())
    except Exception:
        pass

    # Merge updates
    existing.update({k: v for k, v in keys.items() if v})
    for k, v in keys.items():
        if v == "" and k in existing:
            del existing[k]

    # Save to GCS
    try:
        client = _get_gcs_client()
        if client:
            bucket = client.bucket(_GCS_BUCKET)
            blob = bucket.blob(_GCS_KEY_FILE)
            blob.upload_from_string(json.dumps(existing, indent=2), content_type="application/json")
            return
    except Exception:
        pass

    # Fallback: save locally
    local_dir = Path.home() / ".opengravity"
    local_dir.mkdir(parents=True, exist_ok=True)
    (local_dir / "api_keys.json").write_text(json.dumps(existing, indent=2))

# Load saved keys on startup
_load_saved_keys()

# === REST Endpoints ===

class CreateSessionRequest(BaseModel):
    provider: str = "auto"
    model: str | None = None

@app.get("/api/providers")
async def list_providers():
    """List all providers with their configuration status."""
    result = []
    available = ProviderRegistry.list_available()
    for key, config, is_configured in available:
        result.append({
            "key": key,
            "name": config.name,
            "default_model": config.default_model,
            "models": config.models,
            "supports_tool_calling": config.supports_tool_calling,
            "supports_reasoning": config.supports_reasoning,
            "is_configured": is_configured,
            "notes": config.notes,
        })
    return result

# --- API Key Management ---

class UpdateKeysRequest(BaseModel):
    keys: dict[str, str]  # {"KIMI_API_KEY": "sk-...", "DEEPSEEK_API_KEY": "sk-..."}

@app.get("/api/config/keys")
async def get_configured_keys():
    """Return which provider API keys are set (masked for security)."""
    result = {}
    for key, config in PROVIDERS.items():
        env_var = config.api_key_env
        if not env_var:
            # Providers like ollama don't need a key
            result[key] = {"env_var": None, "is_set": True, "masked": "(no key needed)"}
            continue
        value = _os.environ.get(env_var, "")
        if value:
            # Mask the key: show first 4 and last 4 chars
            if len(value) > 10:
                masked = value[:4] + "•" * (len(value) - 8) + value[-4:]
            else:
                masked = "••••••••"
            result[key] = {"env_var": env_var, "is_set": True, "masked": masked}
        else:
            result[key] = {"env_var": env_var, "is_set": False, "masked": ""}
    return result

@app.post("/api/config/keys")
async def update_keys(req: UpdateKeysRequest):
    """Update API keys. Keys are injected into env and persisted to disk."""
    for env_var, value in req.keys.items():
        if value:
            _os.environ[env_var] = value
        elif env_var in _os.environ:
            del _os.environ[env_var]
    _save_keys(req.keys)
    return {"status": "updated", "count": len(req.keys)}

@app.post("/api/sessions")
async def create_session(req: CreateSessionRequest):
    session = session_manager.create(provider=req.provider, model=req.model)
    return {
        "id": session.id,
        "title": session.title,
        "provider": session.provider,
        "model": session.model,
        "created_at": session.created_at.isoformat(),
    }

@app.get("/api/sessions")
async def list_sessions():
    sessions = session_manager.list_all()
    return [{
        "id": s.id,
        "title": s.title,
        "provider": s.provider,
        "model": s.model,
        "created_at": s.created_at.isoformat(),
        "message_count": len(s.messages),
    } for s in sessions]

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    if session_manager.delete(session_id):
        return {"status": "deleted"}
    return {"error": "Session not found"}

@app.patch("/api/sessions/{session_id}")
async def update_session(session_id: str, title: str):
    if session_manager.update_title(session_id, title):
        return {"status": "updated"}
    return {"error": "Session not found"}

# === WebSocket Endpoint ===

@app.websocket("/ws/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    session = session_manager.get(session_id)
    if not session:
        await websocket.send_json({"type": "error", "message": "Session not found"})
        await websocket.close()
        return
    
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            
            if msg_type == "chat":
                user_message = data.get("message", "")
                if not user_message.strip():
                    continue
                
                # Add user message to session history
                session.messages.append({"role": "user", "content": user_message})
                
                # Auto-title from first message
                if session.title == "New Chat" and len(session.messages) == 1:
                    session.title = user_message[:50] + ("..." if len(user_message) > 50 else "")
                
                # IMPORTANT: The Agent's on_stream expects a sync callback,
                # but we need to send over websocket (async).
                # We need to use an asyncio.Queue to bridge sync->async.
                queue = asyncio.Queue()
                
                def sync_stream_callback(chunk: StreamChunk):
                    queue.put_nowait(chunk)
                
                session.agent.on_stream(sync_stream_callback)
                
                # Run agent and stream results concurrently
                async def run_agent():
                    return await session.agent.run(user_message)
                
                async def stream_from_queue():
                    while True:
                        try:
                            chunk = queue.get_nowait()
                            msg = {"type": chunk.type, "content": chunk.content}
                            if chunk.tool_call:
                                msg["tool_call"] = {
                                    "id": chunk.tool_call.id,
                                    "name": chunk.tool_call.name,
                                    "arguments": chunk.tool_call.arguments,
                                }
                            if chunk.tool_result:
                                msg["tool_result"] = {
                                    "name": chunk.tool_result.name,
                                    "result": chunk.tool_result.result,
                                    "is_error": chunk.tool_result.is_error,
                                }
                            await websocket.send_json(msg)
                        except asyncio.QueueEmpty:
                            await asyncio.sleep(0.01)
                
                # Run agent task
                agent_task = asyncio.create_task(run_agent())
                
                # Stream chunks while agent is running
                while not agent_task.done():
                    await stream_from_queue()
                    await asyncio.sleep(0.01)
                
                # Drain remaining chunks
                await stream_from_queue()
                
                result = await agent_task
                
                # Add assistant message to session history
                session.messages.append({"role": "assistant", "content": result.content})
                
                # Send done message
                await websocket.send_json({
                    "type": "done",
                    "content": result.content,
                    "turns": result.turns,
                    "tool_calls": result.tool_calls_made,
                    "elapsed": result.elapsed_seconds,
                })
            
            elif msg_type == "config":
                # Reconfigure session with new provider/model
                provider = data.get("provider", "auto")
                model = data.get("model")
                try:
                    session.agent = Agent(
                        provider=provider,
                        model=model,
                        enable_default_tools=True,
                    )
                    session.provider = session.agent.provider
                    session.model = session.agent.model
                    await websocket.send_json({
                        "type": "config_updated",
                        "provider": session.provider,
                        "model": session.model,
                    })
                except Exception as e:
                    await websocket.send_json({"type": "error", "message": str(e)})
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass


# === Static File Serving (built frontend) ===
# Serve the React build from ui/dist if it exists
# Check multiple possible locations:
#  1. Relative to source (local dev: src/opengravity/server/app.py -> ../../../../ui/dist)
#  2. Docker container path (/app/ui/dist)
#  3. Environment variable override
_ui_dist = None
_candidates = [
    Path(__file__).resolve().parent.parent.parent.parent / "ui" / "dist",  # local dev
    Path("/app/ui/dist"),  # Docker container
]
if _os.environ.get("UI_DIST_DIR"):
    _candidates.insert(0, Path(_os.environ["UI_DIST_DIR"]))
for _candidate in _candidates:
    if _candidate.is_dir():
        _ui_dist = _candidate
        break

if _ui_dist is not None:
    # Serve static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=_ui_dist / "assets"), name="assets")

    # Serve other static files (manifest, sw, icons)
    @app.get("/manifest.json")
    async def manifest():
        return FileResponse(_ui_dist / "manifest.json")

    @app.get("/sw.js")
    async def service_worker():
        return FileResponse(_ui_dist / "sw.js", media_type="application/javascript")

    # SPA catch-all: serve index.html for any non-API route
    @app.get("/{full_path:path}")
    async def spa_catchall(full_path: str):
        # Don't catch API or WebSocket routes
        if full_path.startswith("api/") or full_path.startswith("ws/"):
            return {"error": "Not found"}
        file_path = _ui_dist / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(_ui_dist / "index.html")
