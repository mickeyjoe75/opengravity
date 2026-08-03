import { Plus, Trash2, Settings } from 'lucide-react';

export default function Sidebar({ 
  isOpen, 
  sessions, 
  activeSessionId, 
  onSelectSession, 
  onNewChat, 
  onDeleteSession,
  onOpenSettings
}) {
  const formatTime = (isoString) => {
    if (!isoString) return '';
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHrs = Math.floor(diffMins / 60);
    if (diffHrs < 24) return `${diffHrs}h ago`;
    return `${Math.floor(diffHrs / 24)}d ago`;
  };

  return (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-header">
        <button className="new-chat-btn" onClick={onNewChat}>
          <Plus size={16} /> New Chat
        </button>
      </div>
      
      <div className="session-list">
        {sessions.map(session => (
          <div 
            key={session.id} 
            className={`session-item ${session.id === activeSessionId ? 'active' : ''}`}
            onClick={() => onSelectSession(session.id)}
          >
            <div className="session-title" title={session.title || 'New Chat'}>
              {session.title || 'New Chat'}
            </div>
            <div className="session-time">
              {formatTime(session.updated_at || session.created_at)}
            </div>
            <button 
              className="session-delete" 
              onClick={(e) => {
                e.stopPropagation();
                onDeleteSession(session.id);
              }}
            >
              <Trash2 size={14} />
            </button>
          </div>
        ))}
      </div>

      <div style={{ padding: 16, borderTop: '1px solid var(--border)' }}>
        <button 
          className="session-item" 
          style={{ width: '100%', justifyContent: 'flex-start', gap: 12, background: 'none' }}
          onClick={onOpenSettings}
        >
          <Settings size={16} color="var(--text-muted)" />
          <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Settings</span>
        </button>
      </div>
    </aside>
  );
}
