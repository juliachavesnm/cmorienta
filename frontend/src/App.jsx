import { useState } from 'react';
import './App.css';

const API_URL = 'http://localhost:3000';

function AdvisorCard({ advisor }) {
  return (
    <article className="advisor-card">
      <div className="advisor-header">
        <div className="avatar">
          {advisor.name?.charAt(0).toUpperCase()}
        </div>

        <div>
          <h2>{advisor.name}</h2>
          <p className="university">{advisor.university}</p>
        </div>
      </div>

      {advisor.department && (
        <p className="department">{advisor.department}</p>
      )}

      {advisor.description && (
        <p className="description">{advisor.description}</p>
      )}

      {advisor.keywords?.length > 0 && (
        <div className="keywords">
          {advisor.keywords.map((keyword) => (
            <span className="keyword" key={keyword}>
              {keyword}
            </span>
          ))}
        </div>
      )}

      <div className="advisor-links">
        {advisor.email && (
          <a href={`mailto:${advisor.email}`}>
            {advisor.email}
          </a>
        )}
        {advisor.profile_url && (
          <a
            href={advisor.profile_url}
            target="_blank"
            rel="noopener noreferrer"
          >
            Perfil ↗
          </a>
        )}
      </div>
    </article>
  );
}

function App() {
  const [query, setQuery] = useState('');
  const [advisors, setAdvisors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState('');

  async function searchAdvisors(searchQuery = query) {
    const trimmedQuery = searchQuery.trim();

    if (!trimmedQuery) {
      setAdvisors([]);
      setSearched(false);
      return;
    }

    setLoading(true);
    setError('');
    setSearched(true);

    try {
      const response = await fetch(
        `${API_URL}/advisors/search?q=${encodeURIComponent(trimmedQuery)}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Something went wrong');
      }

      setAdvisors(data);
    } catch (err) {
      console.error(err);
      setError('Could not connect to the server. Make sure the API is running.');
      setAdvisors([]);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    searchAdvisors();
  }

  return (
    <div className="app">
      <header className="hero">
        <div className="hero-content">
          <img
            src="/logo.png"
            alt="CMOrienta"
            className="brand-logo"
          />
          <h1>
            Encontre o orientador 
            <br />
            <span>
            perfeito para você
            </span>
          </h1>

          <p className="subtitle">
            Procure orientadores por linhas de pesquisa, especialização, universidade ou departamento.
          </p>

          <form className="search-form" onSubmit={handleSubmit}>
            <input
              type="text"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Biologia molecular, computação quântica, etc..."
              aria-label="Search advisors"
            />

            <button type="submit" disabled={loading}>
              {loading ? 'Pesquisando...' : 'Buscar'}
            </button>
          </form>

          <div className="suggestions">
            <span>Sugestões:</span>

            {['biologia', 'computação', 'física', 'química'].map(
              (suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  onClick={() => {
                    setQuery(suggestion);
                    searchAdvisors(suggestion);
                  }}
                >
                  {suggestion}
                </button>
              )
            )}
          </div>
        </div>
      </header>

      <main className="results-section">
        {!searched && (
          <div className="empty-state">
            <div className="empty-icon">⌕</div>
            <h2>Procure por um orientador</h2>
            <p>
              Insira uma linha de pesquisa, área do conhecimento, universidade ou departamento para começar.
            </p>
          </div>
        )}

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Pesquisando orientadores...</p>
          </div>
        )}

        {error && !loading && (
          <div className="error-state">
            <h2>Algo deu errado</h2>
            <p>{error}</p>
          </div>
        )}

        {searched && !loading && !error && advisors.length > 0 && (
          <>
            <div className="results-header">
              <div>
                <p className="results-label">RESULTADOS DA BUSCA</p>
                <h2>
                  {advisors.length}{' '}
                  {advisors.length === 1 ? 'orientador encontrado' : 'orientadores encontrados'}
                </h2>
              </div>

              <span className="query-label">
                “{query}”
              </span>
            </div>

            <div className="advisor-grid">
              {advisors.map((advisor) => (
                <AdvisorCard
                  key={advisor.id}
                  advisor={advisor}
                />
              ))}
            </div>
          </>
        )}

        {searched && !loading && !error && advisors.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">⌕</div>
            <h2>Nenhum orientador encontrado</h2>
            <p>
              Tente uma área de pesquisa mais ampla ou uma palavra-chave diferente.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
