import { useEffect, useState } from 'react'
import { useSearchParams, Link, useNavigate } from 'react-router-dom'
import Nav from '../components/Nav.jsx'
import '../styles/results.css'
import { search, ApiError } from '../api/client'

function SearchResults() {
  const [searchParams] = useSearchParams()
  const query = searchParams.get('q') || ''
  const navigate = useNavigate()

  const [results, setResults] = useState([])
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!query) {
      setLoading(false)
      return
    }
    setLoading(true)
    setError('')
    search(query, 5)
      .then((data) => {
        setResults(data.results || [])
        setMessage(data.message || '')
      })
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : 'Search failed. Please try again.')
      )
      .finally(() => setLoading(false))
  }, [query])

  return (
    <div className="results-page">
      <Nav />
      <div className="results-content">
        <div className="results-toolbar animate-in">
          <button className="results-back" onClick={() => navigate('/dashboard')}>
            ← Back to Dashboard
          </button>
          <Link to="/search" className="btn-outline results-new-search">
            + New search
          </Link>
        </div>

        <div className="results-header animate-in" style={{ animationDelay: '30ms' }}>
          <h1>Search Results</h1>
          <div className="query-echo">
            Showing results for <strong>"{query}"</strong>
            {!loading && results.length > 0 && (
              <span className="result-count">· {results.length} result{results.length === 1 ? '' : 's'}</span>
            )}
          </div>
        </div>

        {error && (
          <div className="results-error animate-in">
            {error}
            <button className="results-retry" onClick={() => navigate(0)}>Retry</button>
          </div>
        )}

        {loading ? (
          <div className="results-skeleton-list">
            {[0, 1, 2].map((i) => (
              <div key={i} className="result-skeleton">
                <div className="skeleton" style={{ width: '30%', height: 12, marginBottom: 12 }} />
                <div className="skeleton" style={{ width: '100%', height: 14, marginBottom: 8 }} />
                <div className="skeleton" style={{ width: '80%', height: 14 }} />
              </div>
            ))}
          </div>
        ) : results.length === 0 ? (
          <div className="results-empty animate-in">
            <div className="results-empty-icon">◎</div>
            <h2>No confident match found</h2>
            <p>We couldn't find sufficiently relevant information in your knowledge base for that question.</p>
            <div className="results-empty-actions">
              <Link to="/search" className="btn-gradient results-empty-btn">Try another search</Link>
              <Link to="/dashboard" className="btn-outline results-empty-btn">Back to Dashboard</Link>
            </div>
          </div>
        ) : (
          <div className="results-list">
            {results.map((result, idx) => (
              <div
                key={`${result.document_id}-${idx}`}
                className="result-card animate-in"
                style={{ animationDelay: `${idx * 60}ms` }}
              >
                <div className="result-card-top">
                  <div className="result-source">
                    <span className="result-file-icon">▤</span>
                    {result.filename}
                    {result.page != null ? ` · Page ${result.page}` : ''}
                  </div>
                  <div className="result-score-badge">
                    {(result.score * 100).toFixed(0)}% match
                  </div>
                </div>
                <p className="result-snippet">{result.chunk_text}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default SearchResults