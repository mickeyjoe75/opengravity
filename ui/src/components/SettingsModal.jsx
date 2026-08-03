import { useState, useEffect } from 'react';
import { X, Eye, EyeOff, Check, Loader2, Key, ExternalLink } from 'lucide-react';
import { fetchConfigKeys, updateConfigKeys } from '../utils/api';

const PROVIDER_INFO = {
  kimi:       { label: 'Kimi (Moonshot)', url: 'https://platform.moonshot.ai', placeholder: 'sk-...' },
  glm:        { label: 'GLM (Zhipu AI)', url: 'https://open.bigmodel.cn', placeholder: 'your-api-key' },
  deepseek:   { label: 'DeepSeek', url: 'https://platform.deepseek.com', placeholder: 'sk-...' },
  qwen:       { label: 'Qwen (DashScope)', url: 'https://dashscope.aliyun.com', placeholder: 'sk-...' },
  openai:     { label: 'OpenAI', url: 'https://platform.openai.com', placeholder: 'sk-...' },
  gemini:     { label: 'Google Gemini', url: 'https://aistudio.google.com', placeholder: 'AIza...' },
  mistral:    { label: 'Mistral', url: 'https://console.mistral.ai', placeholder: 'your-api-key' },
  groq:       { label: 'Groq', url: 'https://console.groq.com', placeholder: 'gsk_...' },
  together:   { label: 'Together AI', url: 'https://api.together.xyz', placeholder: 'your-api-key' },
  openrouter: { label: 'OpenRouter', url: 'https://openrouter.ai', placeholder: 'sk-or-...' },
  ollama:     { label: 'Ollama (Local)', url: 'https://ollama.com', placeholder: null },
};

export default function SettingsModal({ onClose }) {
  const [keys, setKeys] = useState({});       // { provider: { env_var, is_set, masked } }
  const [edits, setEdits] = useState({});      // { env_var: new_value }
  const [visible, setVisible] = useState({});  // { env_var: true/false }
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchConfigKeys()
      .then(data => { setKeys(data); setLoading(false); })
      .catch(err => { setError(err.message); setLoading(false); });
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setSaved(false);
    setError(null);
    try {
      const keysToSend = {};
      for (const [envVar, value] of Object.entries(edits)) {
        if (value !== undefined) keysToSend[envVar] = value;
      }
      if (Object.keys(keysToSend).length > 0) {
        await updateConfigKeys(keysToSend);
        // Refresh status from server
        const updated = await fetchConfigKeys();
        setKeys(updated);
        setEdits({});
      }
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err) {
      setError(err.message);
    }
    setSaving(false);
  };

  const hasEdits = Object.keys(edits).length > 0;

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div
        style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)' }}
        onClick={onClose}
      />
      <div className="settings-dialog" style={{
        position: 'relative', zIndex: 101,
        maxHeight: '85vh', overflowY: 'auto',
        width: '560px', maxWidth: '95vw',
      }}>
        <button
          onClick={onClose}
          style={{ position: 'absolute', top: 16, right: 16, background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
        >
          <X size={20} />
        </button>

        <h2 style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Key size={22} style={{ color: 'var(--accent)' }} />
          Settings
        </h2>

        <div className="settings-group">
          <div className="settings-label" style={{ fontSize: 15, marginBottom: 4 }}>API Keys</div>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 16 }}>
            Keys are saved on the cloud and available from any device.
          </div>

          {loading ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '16px 0', color: 'var(--text-muted)' }}>
              <Loader2 size={16} className="spin" /> Loading configuration...
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {Object.entries(PROVIDER_INFO).map(([providerKey, info]) => {
                const keyData = keys[providerKey];
                const envVar = keyData?.env_var;

                if (!envVar) {
                  return (
                    <div key={providerKey} className="key-row">
                      <div className="key-row-header">
                        <span className="key-provider-name">{info.label}</span>
                        <span className="key-status key-status-ok">● Local</span>
                      </div>
                      <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>No API key required</div>
                    </div>
                  );
                }

                const isEditing = envVar in edits;
                const currentValue = isEditing ? edits[envVar] : '';
                const isVisible = visible[envVar];

                return (
                  <div key={providerKey} className="key-row">
                    <div className="key-row-header">
                      <span className="key-provider-name">{info.label}</span>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        {keyData.is_set ? (
                          <span className="key-status key-status-ok">● Connected</span>
                        ) : (
                          <span className="key-status key-status-missing">○ Not set</span>
                        )}
                        <a
                          href={info.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{ color: 'var(--text-muted)', display: 'flex' }}
                          title="Get API key"
                        >
                          <ExternalLink size={14} />
                        </a>
                      </div>
                    </div>

                    {keyData.is_set && !isEditing ? (
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <code style={{
                          fontSize: 12, color: 'var(--text-muted)',
                          background: 'var(--bg-tertiary)', padding: '4px 8px',
                          borderRadius: 4, flex: 1, fontFamily: 'monospace',
                        }}>
                          {keyData.masked}
                        </code>
                        <button
                          className="key-edit-btn"
                          onClick={() => setEdits(prev => ({ ...prev, [envVar]: '' }))}
                        >
                          Change
                        </button>
                      </div>
                    ) : (
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <div style={{ position: 'relative', flex: 1 }}>
                          <input
                            type={isVisible ? 'text' : 'password'}
                            placeholder={info.placeholder || `Enter ${envVar}`}
                            value={currentValue}
                            onChange={(e) => setEdits(prev => ({ ...prev, [envVar]: e.target.value }))}
                            className="key-input"
                            autoComplete="off"
                          />
                          <button
                            onClick={() => setVisible(prev => ({ ...prev, [envVar]: !prev[envVar] }))}
                            style={{
                              position: 'absolute', right: 8, top: '50%', transform: 'translateY(-50%)',
                              background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer',
                              padding: 2,
                            }}
                          >
                            {isVisible ? <EyeOff size={14} /> : <Eye size={14} />}
                          </button>
                        </div>
                        {isEditing && (
                          <button
                            className="key-edit-btn"
                            onClick={() => {
                              setEdits(prev => {
                                const next = { ...prev };
                                delete next[envVar];
                                return next;
                              });
                            }}
                          >
                            Cancel
                          </button>
                        )}
                      </div>
                    )}

                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                      {envVar}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {error && (
          <div style={{ color: '#ef4444', fontSize: 13, padding: '8px 0' }}>
            Error: {error}
          </div>
        )}

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 16 }}>
          <button className="key-cancel-btn" onClick={onClose}>Close</button>
          <button
            className="key-save-btn"
            onClick={handleSave}
            disabled={!hasEdits || saving}
          >
            {saving ? (
              <><Loader2 size={14} className="spin" /> Saving...</>
            ) : saved ? (
              <><Check size={14} /> Saved!</>
            ) : (
              'Save Keys'
            )}
          </button>
        </div>

        <div className="settings-group" style={{ marginTop: 24 }}>
          <div className="settings-label">About</div>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
            OpenGravity v0.1.0 — Open-source, model-agnostic agentic AI framework.
          </div>
        </div>
      </div>
    </div>
  );
}
