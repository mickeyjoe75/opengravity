import { useState, useRef, useEffect } from 'react';
import { Send, Square } from 'lucide-react';

export default function MessageInput({ onSend, isStreaming, onStop }) {
  const [text, setText] = useState('');
  const textareaRef = useRef(null);

  const autoResize = () => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
    }
  };

  useEffect(() => {
    autoResize();
  }, [text]);

  useEffect(() => {
    if (textareaRef.current) textareaRef.current.focus();
  }, []);

  const handleSend = () => {
    if (text.trim() && !isStreaming) {
      onSend(text.trim());
      setText('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="input-container">
      <div className="input-wrapper">
        <textarea
          ref={textareaRef}
          className="input-textarea"
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Message OpenGravity..."
          rows={1}
          disabled={isStreaming}
        />
        {isStreaming ? (
          <button className="send-btn stop-btn" onClick={onStop} title="Stop generation">
            <Square size={16} fill="currentColor" />
          </button>
        ) : (
          <button 
            className="send-btn" 
            onClick={handleSend} 
            disabled={!text.trim()}
          >
            <Send size={16} />
          </button>
        )}
      </div>
    </div>
  );
}
