import { useState, useEffect } from 'react';
import './style.css';
import { API_BASE_URL } from './config';

// Default types with their icons
const DEFAULT_TYPES = [
  { value: 'article', label: '📄 Article' },
  { value: 'youtube', label: '🎬 YouTube' },
  { value: 'tool', label: '🔧 Tool' },
];

interface TabInfo {
  title: string;
  url: string;
}

type Status = 'idle' | 'loading' | 'success' | 'error';

// Styles object for consistent styling
const styles = {
  container: {
    width: '400px',
    height: '500px',
    background: 'linear-gradient(to bottom right, #0f172a, #1e293b)',
    padding: '20px',
    fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
    overflow: 'auto',
  },
  header: {
    textAlign: 'center' as const,
    marginBottom: '24px',
  },
  title: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: 'white',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
  },
  subtitle: {
    color: '#94a3b8',
    fontSize: '14px',
    marginTop: '4px',
  },
  card: {
    backgroundColor: 'rgba(30, 41, 59, 0.5)',
    borderRadius: '12px',
    padding: '16px',
    border: '1px solid #334155',
    boxShadow: '0 10px 25px rgba(0,0,0,0.3)',
  },
  fieldGroup: {
    marginBottom: '16px',
  },
  label: {
    display: 'block',
    color: '#cbd5e1',
    fontSize: '14px',
    fontWeight: '500',
    marginBottom: '8px',
  },
  input: {
    width: '100%',
    padding: '10px 12px',
    backgroundColor: 'rgba(51, 65, 85, 0.5)',
    border: '1px solid #475569',
    borderRadius: '8px',
    color: 'white',
    fontSize: '14px',
    outline: 'none',
    boxSizing: 'border-box' as const,
  },
  select: {
    width: '100%',
    padding: '10px 12px',
    backgroundColor: 'rgba(51, 65, 85, 0.5)',
    border: '1px solid #475569',
    borderRadius: '8px',
    color: 'white',
    fontSize: '14px',
    outline: 'none',
    cursor: 'pointer',
    boxSizing: 'border-box' as const,
    appearance: 'none' as const,
    backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='white'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E")`,
    backgroundRepeat: 'no-repeat',
    backgroundPosition: 'right 12px center',
    backgroundSize: '16px',
  },
  button: {
    width: '100%',
    padding: '12px 16px',
    backgroundColor: '#2563eb',
    border: 'none',
    borderRadius: '8px',
    color: 'white',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    transition: 'background-color 0.2s',
    marginTop: '8px',
  },
  buttonDisabled: {
    backgroundColor: 'rgba(37, 99, 235, 0.5)',
    cursor: 'not-allowed',
  },
  successMessage: {
    marginTop: '16px',
    padding: '12px',
    borderRadius: '8px',
    fontSize: '14px',
    textAlign: 'center' as const,
    fontWeight: '500',
    backgroundColor: 'rgba(34, 197, 94, 0.2)',
    color: '#4ade80',
    border: '1px solid rgba(34, 197, 94, 0.3)',
  },
  errorMessage: {
    marginTop: '16px',
    padding: '12px',
    borderRadius: '8px',
    fontSize: '14px',
    textAlign: 'center' as const,
    fontWeight: '500',
    backgroundColor: 'rgba(239, 68, 68, 0.2)',
    color: '#f87171',
    border: '1px solid rgba(239, 68, 68, 0.3)',
  },
  footer: {
    textAlign: 'center' as const,
    color: '#64748b',
    fontSize: '12px',
    marginTop: '16px',
  },
  addTypeRow: {
    display: 'flex',
    gap: '8px',
    marginTop: '8px',
  },
  smallInput: {
    flex: 1,
    padding: '8px 10px',
    backgroundColor: 'rgba(51, 65, 85, 0.5)',
    border: '1px solid #475569',
    borderRadius: '6px',
    color: 'white',
    fontSize: '13px',
    outline: 'none',
    boxSizing: 'border-box' as const,
  },
  addButton: {
    padding: '8px 12px',
    backgroundColor: '#10b981',
    border: 'none',
    borderRadius: '6px',
    color: 'white',
    fontSize: '13px',
    fontWeight: '500',
    cursor: 'pointer',
    whiteSpace: 'nowrap' as const,
  },
};

// Load custom types from localStorage
const loadCustomTypes = (): { value: string; label: string }[] => {
  try {
    const saved = localStorage.getItem('customTypes');
    return saved ? JSON.parse(saved) : [];
  } catch {
    return [];
  }
};

// Save custom types to localStorage
const saveCustomTypes = (types: { value: string; label: string }[]) => {
  localStorage.setItem('customTypes', JSON.stringify(types));
};

function App() {
  const [tabInfo, setTabInfo] = useState<TabInfo>({ title: '', url: '' });
  const [resourceType, setResourceType] = useState<string>('article');
  const [status, setStatus] = useState<Status>('idle');
  const [message, setMessage] = useState<string>('');
  const [customTypes, setCustomTypes] = useState<{ value: string; label: string }[]>([]);
  const [newTypeName, setNewTypeName] = useState<string>('');
  const [showAddType, setShowAddType] = useState<boolean>(false);

  // Load custom types on mount
  useEffect(() => {
    setCustomTypes(loadCustomTypes());
  }, []);
  // Fetch current tab info on mount
  useEffect(() => {
    const fetchTabInfo = async () => {
      try {
        const [tab] = await browser.tabs.query({ active: true, currentWindow: true });
        if (tab?.title && tab?.url) {
          setTabInfo({
            title: tab.title,
            url: tab.url,
          });
          // Auto-detect YouTube
          if (tab.url.includes('youtube.com') || tab.url.includes('youtu.be')) {
            setResourceType('youtube');
          }
        }
      } catch (error) {
        console.error('Error fetching tab info:', error);
      }
    };

    fetchTabInfo();
  }, []);

  const handleSave = async () => {
    if (!tabInfo.url || !tabInfo.title) {
      setStatus('error');
      setMessage('Missing title or URL');
      return;
    }

    setStatus('loading');
    setMessage('');

    try {
      const response = await fetch(`${API_BASE_URL}/save`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: tabInfo.title,
          url: tabInfo.url,
          type: resourceType,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to save resource');
      }

      setStatus('success');
      setMessage('Resource saved successfully!');

      // Auto-hide success message after 2 seconds
      setTimeout(() => {
        setStatus('idle');
        setMessage('');
      }, 2000);
    } catch (error) {
      setStatus('error');
      setMessage(error instanceof Error ? error.message : 'Failed to save');
    }
  };

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <h1 style={styles.title}>
          <span style={{ fontSize: '28px' }}>📚</span>
          Resource Saver
        </h1>
        <p style={styles.subtitle}>Save resources to your database</p>
      </div>

      {/* Card */}
      <div style={styles.card}>
        {/* Title Input */}
        <div style={styles.fieldGroup}>
          <label style={styles.label}>Title</label>
          <input
            type="text"
            value={tabInfo.title}
            onChange={(e) => setTabInfo({ ...tabInfo, title: e.target.value })}
            style={styles.input}
            placeholder="Enter title..."
          />
        </div>

        {/* URL Input */}
        <div style={styles.fieldGroup}>
          <label style={styles.label}>URL</label>
          <input
            type="url"
            value={tabInfo.url}
            onChange={(e) => setTabInfo({ ...tabInfo, url: e.target.value })}
            style={styles.input}
            placeholder="https://..."
          />
        </div>

        {/* Type Dropdown */}
        <div style={{ ...styles.fieldGroup, marginBottom: '16px' }}>
          <label style={styles.label}>Type</label>
          <select
            value={resourceType}
            onChange={(e) => {
              if (e.target.value === '__add_new__') {
                setShowAddType(true);
              } else {
                setResourceType(e.target.value);
              }
            }}
            style={styles.select}
          >
            {DEFAULT_TYPES.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
            {customTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
            <option value="__add_new__">➕ Add New Type...</option>
          </select>

          {/* Add New Type Input */}
          {showAddType && (
            <div style={styles.addTypeRow}>
              <input
                type="text"
                value={newTypeName}
                onChange={(e) => setNewTypeName(e.target.value)}
                placeholder="Enter new type name..."
                style={styles.smallInput}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && newTypeName.trim()) {
                    const newType = {
                      value: newTypeName.toLowerCase().replace(/\s+/g, '-'),
                      label: `🏷️ ${newTypeName.trim()}`,
                    };
                    const updatedTypes = [...customTypes, newType];
                    setCustomTypes(updatedTypes);
                    saveCustomTypes(updatedTypes);
                    setResourceType(newType.value);
                    setNewTypeName('');
                    setShowAddType(false);
                  }
                }}
              />
              <button
                style={styles.addButton}
                onClick={() => {
                  if (newTypeName.trim()) {
                    const newType = {
                      value: newTypeName.toLowerCase().replace(/\s+/g, '-'),
                      label: `🏷️ ${newTypeName.trim()}`,
                    };
                    const updatedTypes = [...customTypes, newType];
                    setCustomTypes(updatedTypes);
                    saveCustomTypes(updatedTypes);
                    setResourceType(newType.value);
                    setNewTypeName('');
                    setShowAddType(false);
                  }
                }}
              >
                Add
              </button>
            </div>
          )}
        </div>

        {/* Save Button */}
        <button
          onClick={handleSave}
          disabled={status === 'loading'}
          style={{
            ...styles.button,
            ...(status === 'loading' ? styles.buttonDisabled : {}),
          }}
          onMouseOver={(e) => {
            if (status !== 'loading') {
              e.currentTarget.style.backgroundColor = '#3b82f6';
            }
          }}
          onMouseOut={(e) => {
            if (status !== 'loading') {
              e.currentTarget.style.backgroundColor = '#2563eb';
            }
          }}
        >
          {status === 'loading' ? (
            <>⏳ Saving...</>
          ) : (
            <>💾 Save Resource</>
          )}
        </button>

        {/* Status Messages */}
        {message && (
          <div style={status === 'success' ? styles.successMessage : styles.errorMessage}>
            {status === 'success' ? '✅ ' : '❌ '}
            {message}
          </div>
        )}
      </div>

      {/* Footer */}
      <p style={styles.footer}>
        Resources are saved to {API_BASE_URL.replace('http://', '').replace('https://', '')}
      </p>
    </div>
  );
}

export default App;
