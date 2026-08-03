import { Menu, Zap, Settings } from 'lucide-react';
import ModelPicker from './ModelPicker';

export default function Header({ 
  toggleSidebar, 
  selectedProvider, 
  selectedModel, 
  onModelChange,
  onOpenSettings,
  isConnected
}) {
  return (
    <header className="header">
      <div className="header-left">
        <button className="menu-btn" onClick={toggleSidebar}>
          <Menu size={20} />
        </button>
        <div className="header-title">
          <Zap className="icon" size={20} />
          <span>OpenGravity</span>
          <div 
            style={{ 
              width: 8, height: 8, borderRadius: '50%', 
              background: isConnected ? 'var(--success)' : 'var(--error)',
              marginLeft: 8
            }} 
            title={isConnected ? 'Connected' : 'Disconnected'}
          />
        </div>
      </div>
      
      <ModelPicker 
        selectedProvider={selectedProvider}
        selectedModel={selectedModel}
        onChange={onModelChange}
      />

      <button className="menu-btn" onClick={onOpenSettings} title="Settings">
        <Settings size={20} />
      </button>
    </header>
  );
}
