const BASE = '/api'

async function request(method, path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Error del servidor')
  }
  return res.json()
}

export const api = {
  register: (data) => request('POST', '/users/', data),
  login: (data) => request('POST', '/users/login', data),
  getUser: (id) => request('GET', `/users/${id}`),
  getUserAnalyses: (userId) => request('GET', `/analysis/user/${userId}`),
  getAnalysis: (id) => request('GET', `/analysis/${id}`),
  deleteAnalysis: (id) => request('DELETE', `/analysis/${id}`),
}

export async function streamAnalysis(body, onEvent) {
  const res = await fetch(`${BASE}/analysis/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Error del servidor')
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const parts = buffer.split('\n\n')
    buffer = parts.pop()
    for (const part of parts) {
      const line = part.trim()
      if (line.startsWith('data: ')) {
        try {
          const event = JSON.parse(line.slice(6))
          onEvent(event)
        } catch {
          // ignore
        }
      }
    }
  }
}
