import { useState, useEffect } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { searchDocuments } from '../services/api'
import '../styles/results.css'

function SearchResults() {
  const [searchParams] = useSearchParams()
  const query = searchParams.get('q') || ''
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!query) {
      setLoading(false)
      return
    }
    setLoading(true)
    searchDocuments(query)
      .then((res) => setResults(res))
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

      {loading ? (
        <div className="results-empty">Searching...</div>
      ) : results.length === 0 ? (
        <div className="results-empty">
          No results found. <Link to="/search">Try another search</Link>.
        </div>
      ) : (
        <div className="results-list">
          {results.map((result) => (
            <div key={result.id} className="result-card">
              <div className="result-source">{result.source}</div>
              <p className="result-snippet">{result.snippet}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default SearchResults