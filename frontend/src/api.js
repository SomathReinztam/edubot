const BASE_URL = 'http://localhost:8000'

export async function register(name, email, password) {
  const res = await fetch(`${BASE_URL}/users/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password }),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Error al registrar usuario')
  }
  return res.json()
}

export async function login(email, password) {
  const res = await fetch(`${BASE_URL}/users/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Email o contraseña incorrectos')
  }
  return res.json()
}

export async function getUserAnalyses(userId) {
  const res = await fetch(`${BASE_URL}/edubot/analyze/user/${userId}`)
  if (!res.ok) throw new Error('Error al obtener análisis')
  return res.json()
}

export async function getAnalysis(analysisId) {
  const res = await fetch(`${BASE_URL}/edubot/analyze/${analysisId}`)
  if (!res.ok) throw new Error('Error al obtener análisis')
  return res.json()
}

export async function streamAnalysis(payload, onChunk, onFinal, onError) {
  let response
  try {
    response = await fetch(`${BASE_URL}/edubot/analyze/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
  } catch (err) {
    onError('No se pudo conectar con el servidor')
    return
  }

  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    onError(err.detail || 'Error al iniciar el análisis')
    return
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop()

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6))
          if (data.type === 'reasoning') {
            onChunk(data)
          } else if (data.type === 'final_analysis') {
            onFinal(data.content)
          }
        } catch {
          // ignore malformed chunks
        }
      }
    }
  }
}
