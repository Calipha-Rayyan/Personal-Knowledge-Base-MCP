import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
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
      <div className="search-header">
        <h1>Search</h1>
        <div className="subtitle">Ask a question and search across your documents.</div>
      </div>

      <form onSubmit={handleSubmit} className="search-form">
        <input
          type="text"
          placeholder="e.g. What are the key OOP concepts?"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" disabled={!query.trim()}>
          Search
        </button>
      </form>
    </div>
  )
}

export default Search
