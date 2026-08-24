import { useEffect, useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import '../styles/results.css'
import { search, ApiError } from '../api/client'

function SearchResults() {
  const [searchParams] = useSearchParams()
  const query = searchParams.get('q') || ''

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
      <div className="results-header">
        <h1>Search Results</h1>
        <div className="query-echo">
          Showing results for <strong>"{query}"</strong>
        </div>
      </div>

      {error && <div className="results-error">{error}</div>}

      {loading ? (
        <div className="results-empty">Searching your documents…</div>
      ) : results.length === 0 ? (
        <div className="results-empty">
          {message || 'No results found.'} <Link to="/search">Try another search</Link>.
        </div>
      ) : (
        <div className="results-list">
          {results.map((result, idx) => (
            <div key={`${result.document_id}-${idx}`} className="result-card">
              <div className="result-source">
                {result.filename}
                {result.page != null ? ` · Page ${result.page}` : ''}
                {' · '}
                <span className="result-score">
                  Similarity {(result.score * 100).toFixed(0)}%
                </span>
              </div>
              <p className="result-snippet">{result.chunk_text}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default SearchResults
