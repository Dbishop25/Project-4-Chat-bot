import { useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from 'react'
import { ArrowUp, BookOpen, Check, ChevronDown, Dice5, Menu, Plus, Search, Sparkles, UserRound, X } from 'lucide-react'
import { askQuestion, clearChatSession } from './services/api'
import type { ChatMessage, Source } from './types/chat'

const examples = [
  { game: 'Monopoly', icon: '💸', text: 'What happens when I land on Free Parking?' },
  { game: 'Clue', icon: '🕵️', text: 'How do I make a suggestion in Clue?' },
  { game: 'Chess', icon: '♟️', text: 'How does castling work in chess?' },
  { game: 'Yahtzee', icon: '🎲', text: 'Can I reroll the same dice more than once?' },
]

function SourceCard({ source, index }: { source: Source; index: number }) {
  const [open, setOpen] = useState(false)
  return <div className={`source-card ${open ? 'source-open' : ''}`}><button className="source-toggle" onClick={() => setOpen(!open)} aria-expanded={open}>
    <span className="source-number">{String(index + 1).padStart(2, '0')}</span><BookOpen size={15} /><span className="source-info"><small>REFERENCE{source.page ? ` · PAGE ${source.page}` : ''}</small><b>{source.title}</b></span><ChevronDown size={15} className="source-chevron" />
  </button>{open && <p className="source-content">{source.content}</p>}</div>
}

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [question, setQuestion] = useState('')
  const [sessionId, setSessionId] = useState(() => crypto.randomUUID())
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [menuOpen, setMenuOpen] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages, loading])

  async function sendQuestion(text: string) {
    const clean = text.trim()
    if (!clean || loading) return
    setError('')
    setQuestion('')
    setMessages(current => [...current, { id: crypto.randomUUID(), role: 'user', content: clean }])
    setLoading(true)
    try {
      const result = await askQuestion(clean, sessionId)
      setMessages(current => [...current, { id: crypto.randomUUID(), role: 'assistant', content: result.answer, sources: result.sources }])
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Could not reach the chatbot API.')
    } finally { setLoading(false) }
  }
  function submit(event?: FormEvent) { event?.preventDefault(); void sendQuestion(question) }
  function onInputKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); submit() }
  }
  function newChat() {
    void clearChatSession(sessionId)
    setSessionId(crypto.randomUUID())
    setMessages([])
    setQuestion('')
    setError('')
  }

  return <div className="app-shell">
    <aside className={`sidebar ${menuOpen ? 'sidebar-open' : ''}`}>
      <a className="app-brand" href="#home"><span className="brand-icon"><Dice5 size={21} /></span><span>tabletop<span className="brand-accent"> guide</span><small>DOCUMENTATION DIGESTER</small></span></a>
      <button className="new-chat" onClick={newChat}><Plus size={17} /> New conversation</button>
      <div className="side-label">TRY A QUESTION</div>
      <div className="example-list">{examples.map(item => <button key={item.game} className="example-link" onClick={() => { void sendQuestion(item.text); setMenuOpen(false) }}><span className="example-icon">{item.icon}</span><span><b>{item.game}</b><small>{item.text}</small></span></button>)}</div>
      <div className="side-spacer" />
      <div className="library-note"><span className="library-note-icon"><BookOpen size={16} /></span><div><b>Your game shelf</b><p>Answers grounded in your team's game guides.</p></div><span className="library-indicator" /></div>
      <div className="side-status"><i /> READY TO SEARCH <span>BETA</span></div>
    </aside>
    <main className="main-panel" id="home">
      <header className="topbar"><button className="menu-button" aria-label="Toggle menu" onClick={() => setMenuOpen(!menuOpen)}><Menu size={20} /></button><div className="breadcrumb"><b>Tabletop Guide</b><span>/</span><small>{messages.length ? 'Conversation' : 'New conversation'}</small></div><div className="top-status"><span><i /> DOCUMENT SEARCH</span><div className="avatar">TG</div></div></header>
      <section className={`chat-area ${messages.length ? 'has-messages' : ''}`}>
        {!messages.length ? <div className="welcome"><div className="welcome-mark"><Sparkles size={18} /></div><div className="welcome-label">YOUR TABLETOP SIDEKICK</div><h1>Let's get you<br /><em>playing.</em></h1><p className="welcome-copy">Ask a question about the games on your shelf. I’ll search your guides and point you to the source.</p><div className="ideas-label">A FEW IDEAS TO GET STARTED</div><div className="suggestion-grid">{examples.map(item => <button key={item.game} className="suggestion" onClick={() => void sendQuestion(item.text)}><span className="suggestion-icon">{item.icon}</span><span><small>{item.game}</small><b>{item.text}</b></span><span className="suggestion-arrow">↗</span></button>)}</div><div className="grounded-note"><span>✳</span> Answers are based on your team's uploaded game documentation.</div></div> : <div className="conversation"><div className="conversation-title"><i /> YOUR CONVERSATION <i /></div>{messages.map(message => <article key={message.id} className={`message ${message.role}`}><div className={`message-avatar ${message.role}`}>{message.role === 'assistant' ? <Dice5 size={17} /> : <UserRound size={16} />}</div><div className="message-body"><div className="message-name"><b>{message.role === 'assistant' ? 'Tabletop Guide' : 'You'}</b><small>{message.role === 'assistant' ? 'DOCUMENT ASSISTANT' : 'YOUR QUESTION'}</small></div><p className="message-text">{message.content}</p>{message.role === 'assistant' && message.sources?.length ? <div className="sources"><div className="sources-title"><BookOpen size={14} /><b>Sources from your game guides</b><span>{message.sources.length}</span></div>{message.sources.map((source, index) => <SourceCard key={`${source.title}-${index}`} source={source} index={index} />)}</div> : message.role === 'assistant' ? <div className="no-sources"><BookOpen size={13} /> No supporting sources were returned.</div> : null}</div></article>)}{loading && <div className="loading-row"><div className="message-avatar assistant"><Dice5 size={17} /></div><span className="loader" /><b>Searching your game guides…</b></div>}<div ref={bottomRef} />
        </div>}
        {error && <div className="error-box" role="alert"><span>!</span><div><b>Couldn't reach the answer service</b><p>{error}</p><small>Check that FastAPI is running and the frontend API URL is correct.</small></div></div>}
      </section>
      <div className="composer-wrap"><form className="composer" onSubmit={submit}><textarea value={question} onChange={event => setQuestion(event.target.value)} onKeyDown={onInputKeyDown} placeholder="Ask about a rule, setup, or strategy…" rows={2} aria-label="Your question" disabled={loading} /><div className="composer-bottom"><span><BookOpen size={14} /> Grounded in your uploaded docs</span><small>ENTER TO SEND</small><button type="submit" disabled={!question.trim() || loading} aria-label="Send question"><ArrowUp size={18} /></button></div></form><p className="disclaimer">Tabletop Guide answers from connected game documents. Check the cited rules for the final word.</p></div>
    </main>
  </div>
}

export default App
