import type { AskResponse } from '../types/chat'

// Override in frontend/.env with VITE_API_URL=http://localhost:8000/api/chat if needed.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/chat'
const CHAT_URL = API_URL.replace(/\/$/, '')

export async function askQuestion(question: string, sessionId: string): Promise<AskResponse> {
  let response: Response
  try {
    response = await fetch(CHAT_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, session_id: sessionId }),
    })
  } catch {
    throw new Error(`The API at ${API_URL} is unavailable.`)
  }
  if (!response.ok) throw new Error(`The API returned ${response.status}.`)
  const data = await response.json()
  // Expected API response: { answer: string, sources: [{ title, content, page? }] }
  if (typeof data.answer !== 'string') throw new Error('The API response is missing an answer.')
  return { answer: data.answer, sources: Array.isArray(data.sources) ? data.sources : [] }
}

export async function clearChatSession(sessionId: string): Promise<void> {
  try {
    await fetch(`${CHAT_URL}/${encodeURIComponent(sessionId)}`, { method: 'DELETE' })
  } catch {
    // A new session ID still starts a clean conversation if cleanup is unavailable.
  }
}
