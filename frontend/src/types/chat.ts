export type Source = { title: string; content: string; page?: string | number }
export type ChatMessage = { id: string; role: 'user' | 'assistant'; content: string; sources?: Source[] }
export type AskResponse = { answer: string; sources: Source[] }
