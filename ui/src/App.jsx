import { useState, useEffect } from 'react';
import { useSessions } from './hooks/useSessions';
import { useChat } from './hooks/useChat';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import ChatView from './components/ChatView';
import MessageInput from './components/MessageInput';
import SettingsModal from './components/SettingsModal';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(window.innerWidth > 768);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState(null);
  const [selectedModel, setSelectedModel] = useState(null);


  const {
    sessions,
    activeSessionId,
    activeSession,
    setActiveSessionId,
    createSession,
    deleteSession
  } = useSessions();

  const {
    messages,
    sendMessage,
    sendConfig,
    isStreaming,
    isConnected,
    clearMessages
  } = useChat(activeSessionId);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > 768) {
        setSidebarOpen(true);
      } else {
        setSidebarOpen(false);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleNewChat = async () => {
    const provider = selectedProvider || 'auto';
    const model = selectedModel || null;
    await createSession(provider, model);
    if (window.innerWidth <= 768) setSidebarOpen(false);
  };

  const handleSendMessage = async (text) => {
    // Auto-create a session if none exists
    if (!activeSessionId) {
      const provider = selectedProvider || 'auto';
      const model = selectedModel || null;
      await createSession(provider, model);
    }
    sendMessage(text);
  };

  const handleModelChange = (provider, model) => {
    setSelectedProvider(provider);
    setSelectedModel(model);
    sendConfig({ provider, model });
  };

  return (
    <div className="app-layout">
      {/* Mobile Overlay */}
      {sidebarOpen && window.innerWidth <= 768 && (
        <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)}></div>
      )}

      <Sidebar 
        isOpen={sidebarOpen} 
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={(id) => {
          setActiveSessionId(id);
          if (window.innerWidth <= 768) setSidebarOpen(false);
        }}
        onNewChat={handleNewChat}
        onDeleteSession={deleteSession}
        onOpenSettings={() => setSettingsOpen(true)}
      />

      <main className="main-content">
        <Header 
          toggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          selectedProvider={selectedProvider}
          selectedModel={selectedModel}
          onModelChange={handleModelChange}
          onOpenSettings={() => setSettingsOpen(true)}
          isConnected={isConnected}
        />

        <ChatView messages={messages} isStreaming={isStreaming} />

        <MessageInput 
          onSend={handleSendMessage}
          isStreaming={isStreaming}
          onStop={() => sendConfig({ action: 'stop' })}
        />
      </main>

      {settingsOpen && (
        <SettingsModal onClose={() => setSettingsOpen(false)} />
      )}
    </div>
  );
}

export default App;
