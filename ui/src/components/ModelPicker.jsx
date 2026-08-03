import { useState, useEffect, useRef } from 'react';
import { ChevronDown } from 'lucide-react';
import { fetchProviders } from '../utils/api';

export default function ModelPicker({ selectedProvider, selectedModel, onChange }) {
  const [open, setOpen] = useState(false);
  const [providersData, setProvidersData] = useState([]);
  const wrapperRef = useRef(null);

  useEffect(() => {
    fetchProviders()
      .then(data => setProvidersData(data || []))
      .catch(console.error);
  }, []);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (providerKey, modelId) => {
    if (onChange) onChange(providerKey, modelId);
    setOpen(false);
  };

  const currentDisplay = selectedModel || 'Select Model';

  return (
    <div className="model-picker" ref={wrapperRef}>
      <button className="model-picker-btn" onClick={() => setOpen(!open)}>
        <span>{currentDisplay}</span>
        <ChevronDown size={14} style={{ opacity: 0.5 }} />
      </button>

      {open && (
        <div className="model-picker-dropdown">
          {providersData.length === 0 && (
            <div style={{ padding: '12px 16px', color: 'var(--text-muted)', fontSize: 13 }}>
              Loading providers...
            </div>
          )}
          {providersData.map(provider => (
            <div key={provider.key} className="provider-group">
              <div className="provider-label">
                <div className={`provider-dot ${provider.is_configured ? 'configured' : 'unconfigured'}`} />
                {provider.name}
              </div>
              {(provider.models && provider.models.length > 0) ? (
                provider.models.map(model => (
                  <div
                    key={model}
                    className={`model-option ${selectedModel === model ? 'selected' : ''} ${!provider.is_configured ? 'disabled' : ''}`}
                    onClick={() => provider.is_configured && handleSelect(provider.key, model)}
                  >
                    {model}
                  </div>
                ))
              ) : (
                provider.default_model && (
                  <div
                    className={`model-option ${selectedModel === provider.default_model ? 'selected' : ''} ${!provider.is_configured ? 'disabled' : ''}`}
                    onClick={() => provider.is_configured && handleSelect(provider.key, provider.default_model)}
                  >
                    {provider.default_model}
                  </div>
                )
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
