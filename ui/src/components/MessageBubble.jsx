import { Zap, Copy, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import { useState } from 'react';
import ToolCallPanel from './ToolCallPanel';

function CodeBlock({ node, inline, className, children, ...props }) {
  const [copied, setCopied] = useState(false);
  const match = /language-(\w+)/.exec(className || '');
  const lang = match ? match[1] : '';

  const handleCopy = () => {
    navigator.clipboard.writeText(String(children).replace(/\n$/, ''));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!inline && match) {
    return (
      <>
        <div className="code-header">
          <span className="code-lang">{lang}</span>
          <button className={`copy-btn ${copied ? 'copied' : ''}`} onClick={handleCopy}>
            {copied ? <Check size={14} /> : <Copy size={14} />}
            {copied ? 'Copied' : 'Copy'}
          </button>
        </div>
        <pre className={className} {...props}>
          <code>{children}</code>
        </pre>
      </>
    );
  }
  return <code className={className} {...props}>{children}</code>;
}

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';
  
  return (
    <div className={`message ${isUser ? 'message-user' : 'message-assistant'}`}>
      <div className="message-avatar">
        {isUser ? 'U' : <Zap size={16} />}
      </div>
      <div className="message-content">
        {message.content && (
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]} 
            rehypePlugins={[rehypeHighlight]}
            components={{ code: CodeBlock }}
          >
            {message.content}
          </ReactMarkdown>
        )}
        
        {message.toolCalls && message.toolCalls.map((tc, i) => (
          <ToolCallPanel key={tc.id || i} toolCall={tc} />
        ))}
      </div>
    </div>
  );
}
