import { useSearchParams, Link } from 'react-router-dom'
import '../styles/results.css'

const mockResults = [
  { id: 1, source: 'OOP_Course_Breakup.pdf', snippet: 'Object-Oriented Programming is built on four key concepts: encapsulation, abstraction, inheritance, and polymorphism.' },
  { id: 2, source: 'Data_Structures_Notes.docx', snippet: 'Classes act as blueprints for objects, bundling data and behavior together through encapsulation.' },
]

function SearchResults() {
  const [searchParams] = useSearchParams()
  const query = searchParams.get('q') || ''
  const results = query ? mockResults : []

  return (
    <div className="results-page">
      <div className="results-header">
        <h1>Search Results</h1>
        <div className="query-echo">
          Showing results for <strong>"{query}"</strong>
        </div>
      </div>

      {results.length === 0 ? (
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