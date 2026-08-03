import { useState, useEffect, useCallback } from 'react';
import { useWebSocket } from './useWebSocket';
import { fetchSessionHistory } from '../utils/api';

export function useChat(sessionId) {
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const { sendMessage: wsSendMessage, sendConfig, isConnected, lastMessage } = useWebSocket(sessionId);

  // Load history on mount
  useEffect(() => {
    if (!sessionId) {
      setMessages([]);
      return;
    }
    fetchSessionHistory(sessionId)
      .then(history => {
        // Assume history is an array of messages compatible with our state
        setMessages(history || []);
      })
      .catch(console.error);
  }, [sessionId]);

  useEffect(() => {
    if (!lastMessage) return;

    setMessages(prev => {
      const newMessages = [...prev];
      const lastIdx = newMessages.length - 1;
      
      switch (lastMessage.type) {
        case 'text': {
          if (lastIdx >= 0 && newMessages[lastIdx].role === 'assistant' && newMessages[lastIdx].isStreaming) {
            newMessages[lastIdx].content += lastMessage.content;
          } else {
            newMessages.push({
              id: Date.now().toString(),
              role: 'assistant',
              content: lastMessage.content,
              toolCalls: [],
              isStreaming: true
            });
          }
          setIsStreaming(true);
          break;
        }
        case 'tool_call': {
          if (lastIdx >= 0 && newMessages[lastIdx].role === 'assistant' && newMessages[lastIdx].isStreaming) {
            const tcIdx = newMessages[lastIdx].toolCalls.findIndex(tc => tc.id === lastMessage.tool_call_id);
            if (tcIdx >= 0) {
              // Append arguments to existing tool call chunk
              newMessages[lastIdx].toolCalls[tcIdx].arguments += (lastMessage.arguments || '');
            } else {
              newMessages[lastIdx].toolCalls.push({
                id: lastMessage.tool_call_id,
                name: lastMessage.name,
                arguments: lastMessage.arguments || '',
                result: null,
                status: 'running'
              });
            }
          } else {
             newMessages.push({
              id: Date.now().toString(),
              role: 'assistant',
              content: '',
              toolCalls: [{
                id: lastMessage.tool_call_id,
                name: lastMessage.name,
                arguments: lastMessage.arguments || '',
                result: null,
                status: 'running'
              }],
              isStreaming: true
            });
          }
          setIsStreaming(true);
          break;
        }
        case 'tool_result': {
          if (lastIdx >= 0) {
             const tcIdx = newMessages[lastIdx].toolCalls.findIndex(tc => tc.id === lastMessage.tool_call_id);
             if (tcIdx >= 0) {
               newMessages[lastIdx].toolCalls[tcIdx].result = lastMessage.result;
               newMessages[lastIdx].toolCalls[tcIdx].status = lastMessage.isError ? 'error' : 'success';
             }
          }
          break;
        }
        case 'done': {
          if (lastIdx >= 0 && newMessages[lastIdx].isStreaming) {
            newMessages[lastIdx].isStreaming = false;
          }
          setIsStreaming(false);
          break;
        }
      }
      return newMessages;
    });
  }, [lastMessage]);

  const sendMessage = useCallback((content) => {
    // Add user message optimistically
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      role: 'user',
      content,
      toolCalls: [],
      isStreaming: false
    }]);
    wsSendMessage(content);
  }, [wsSendMessage]);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return { messages, sendMessage, sendConfig, isStreaming, isConnected, clearMessages };
}
