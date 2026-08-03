const API_BASE = '/api';

export async function fetchProviders() {
  const res = await fetch(`${API_BASE}/providers`);
  if (!res.ok) throw new Error('Failed to fetch providers');
  return res.json();
}

export async function createSession(provider, model) {
  const res = await fetch(`${API_BASE}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ provider, model }),
  });
  if (!res.ok) throw new Error('Failed to create session');
  return res.json();
}

export async function fetchSessions() {
  const res = await fetch(`${API_BASE}/sessions`);
  if (!res.ok) throw new Error('Failed to fetch sessions');
  return res.json();
}

export async function deleteSession(id) {
  const res = await fetch(`${API_BASE}/sessions/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete session');
  return res.json();
}

export async function fetchSessionHistory(id) {
  const res = await fetch(`${API_BASE}/sessions/${id}/history`);
  if (!res.ok) throw new Error('Failed to fetch session history');
  return res.json();
}

export async function fetchConfigKeys() {
  const res = await fetch(`${API_BASE}/config/keys`);
  if (!res.ok) throw new Error('Failed to fetch config');
  return res.json();
}

export async function updateConfigKeys(keys) {
  const res = await fetch(`${API_BASE}/config/keys`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ keys }),
  });
  if (!res.ok) throw new Error('Failed to update keys');
  return res.json();
}
