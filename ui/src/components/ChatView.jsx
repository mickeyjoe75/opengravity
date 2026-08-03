import { useEffect, useRef } from 'react';
import { Zap } from 'lucide-react';
import MessageBubble from './MessageBubble';

export default function ChatView({ messages, isStreaming }) {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isStreaming]);

  if (!messages || messages.length === 0) {
    return (
      <div className="chat-view">
        <div className="empty-state">
          <Zap className="icon" />
          <h2>OpenGravity</h2>
          <p>Start a conversation. The AI assistant can use tools to help you.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-view" ref={scrollRef}>
      <div className="chat-messages">
        {messages.map(msg => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {isStreaming && (
          <div className="message message-assistant" style={{ opacity: 0.7 }}>
             <div className="message-avatar"><Zap size={16} /></div>
             <div className="message-content">
               <div className="streaming-dot">
                 <span /> <span /> <span />
               </div>
             </div>
          </div>
        )}
      </div>
    </div>
  );
}
