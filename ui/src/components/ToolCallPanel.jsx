import { useState } from 'react';
import { Wrench, ChevronDown, CheckCircle2, XCircle } from 'lucide-react';

export default function ToolCallPanel({ toolCall }) {
  const [isOpen, setIsOpen] = useState(false);
  const isSuccess = toolCall.status === 'success';
  const isError = toolCall.status === 'error';

  let statusClass = '';
  if (isSuccess) statusClass = 'success';
  if (isError) statusClass = 'error';

  const truncate = (str, len = 500) => {
    if (!str) return '';
    if (str.length > len) return str.substring(0, len) + '...\n\n(Truncated. Show more to see full output)';
    return str;
  };

  const getStatusIcon = () => {
    if (isSuccess) return <CheckCircle2 size={14} />;
    if (isError) return <XCircle size={14} />;
    return <Wrench size={14} />;
  };

  return (
    <div className={`tool-panel ${statusClass}`}>
      <div className="tool-panel-header" onClick={() => setIsOpen(!isOpen)}>
        <span className="tool-icon">{getStatusIcon()}</span>
        <span className="tool-name">{toolCall.name}</span>
        <ChevronDown size={16} className={`chevron ${isOpen ? 'open' : ''}`} />
      </div>
      
      {isOpen && (
        <div className="tool-panel-body">
          <div className="tool-result-label">Arguments</div>
          <pre>{toolCall.arguments}</pre>
          
          {toolCall.result && (
            <>
              <div className="tool-result-label" style={{ marginTop: 12 }}>Result</div>
              <pre>{truncate(toolCall.result)}</pre>
            </>
          )}
        </div>
      )}
    </div>
  );
}
