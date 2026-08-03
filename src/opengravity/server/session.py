import uuid
from dataclasses import dataclass, field
from datetime import datetime
from opengravity.core.agent import Agent

@dataclass
class Session:
    id: str
    title: str
    provider: str
    model: str
    created_at: datetime
    agent: Agent
    messages: list[dict] = field(default_factory=list)  # For UI display history

class SessionManager:
    def __init__(self):
        self._sessions: dict[str, Session] = {}
    
    def create(self, provider: str = "auto", model: str | None = None, 
               api_key: str | None = None, base_url: str | None = None) -> Session:
        """Create a new chat session with its own Agent."""
        session_id = str(uuid.uuid4())[:8]
        agent = Agent(
            provider=provider,
            model=model,
            api_key=api_key,
            base_url=base_url,
            enable_default_tools=True,
        )
        session = Session(
            id=session_id,
            title="New Chat",
            provider=agent.provider,
            model=agent.model,
            created_at=datetime.now(),
            agent=agent,
        )
        self._sessions[session_id] = session
        return session
    
    def get(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)
        
    def list_all(self) -> list[Session]:
        return list(self._sessions.values())
        
    def delete(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
        
    def update_title(self, session_id: str, title: str) -> bool:
        if session_id in self._sessions:
            self._sessions[session_id].title = title
            return True
        return False
