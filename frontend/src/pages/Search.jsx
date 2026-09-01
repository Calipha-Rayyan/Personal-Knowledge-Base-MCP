import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Nav from '../components/Nav.jsx'
import '../styles/search.css'

function Search() {
  const [query, setQuery] = useState('')
  const navigate = useNavigate()

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!query.trim()) return
    navigate(`/search-results?q=${encodeURIComponent(query)}`)
  }

  return (
    <div className="search-page">
      <Nav />
      <div className="search-hero">
        <div className="search-hero-glow" />
        <div className="search-hero-content animate-in">
          <div className="search-hero-eyebrow">Semantic Search</div>
          <h1>Search your knowledge</h1>
          <p className="subtitle">
            Ask a question in plain language — we'll find the most relevant passages
            across everything you've uploaded, ranked by meaning, not keywords.
          </p>

          <form onSubmit={handleSubmit} className="search-form">
            <span className="search-icon">⌕</span>
            <input
              type="text"
              placeholder="Ask anything about your documents…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              autoFocus
            />
            {query && (
              <button
                type="button"
                className="search-clear"
                onClick={() => setQuery('')}
                aria-label="Clear search"
              >
                ✕
              </button>
            )}
            <button type="submit" className="btn-gradient search-submit" disabled={!query.trim()}>
              Search
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

export default Search