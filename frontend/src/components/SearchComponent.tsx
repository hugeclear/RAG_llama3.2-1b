import React, { useState, useCallback } from 'react';
import { search, SearchResponse } from '../services/api';

const SearchComponent: React.FC = () => {
  const [query, setQuery] = useState('');
  const [searchResult, setSearchResult] = useState<SearchResponse | null>(null);
  const [showSources, setShowSources] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState('llama');

  const handleSearch = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setShowSources(false);

    try {
      const response = await search({ query });
      if (response.data && response.data.answer) {
        setSearchResult({
          answer: response.data.answer,
          sources: response.data.sources || []
        });
      } else {
        console.error('Invalid response structure:', response.data);
        setError('Invalid response received from server');
      }
    } catch (error) {
      console.error('Search error:', error);
      setError(error instanceof Error ? error.message : 'An error occurred during search');
    } finally {
      setIsLoading(false);
    }
  }, [query]);

  return (
    <div className="content-box">
      <h2 className="text-xl font-semibold mb-4">Ask Questions</h2>
      
      <div className="mb-4">
        <label className="block text-sm mb-2">Select Model</label>
        <div className="model-buttons">
          <button
            onClick={() => setSelectedModel('llama')}
            className={`model-button ${selectedModel === 'llama' ? 'active' : ''}`}
          >
            Llama
          </button>
          <button
            onClick={() => setSelectedModel('codellama')}
            className={`model-button ${selectedModel === 'codellama' ? 'active' : ''}`}
          >
            codellama_merged_slerp
          </button>
        </div>
      </div>

      <form onSubmit={handleSearch}>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your question..."
          className="input-area"
          disabled={isLoading}
          rows={4}
        />
  
        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className="submit-button"
        >
          {isLoading ? 'Generating...' : 'Generate Answer'}
        </button>
      </form>

      {error && (
        <div className="mt-4 text-red-400">{error}</div>
      )}

      {searchResult && (
        <div className="results-box">
          <div className="mb-4">{searchResult.answer}</div>

          {searchResult.sources?.length > 0 && (
            <div>
              <button
                onClick={() => setShowSources(!showSources)}
                className="sources-toggle"
              >
                {showSources ? 'Hide Sources ↑' : 'Show Sources ↓'}
              </button>

              {showSources && (
                <div className="mt-4 space-y-4">
                  {searchResult.sources.map((source, index) => (
                    <div key={index} className="bg-[#3a3b52] p-3 rounded">
                      <div className="text-sm">{source.content}</div>
                      {source.metadata?.source && (
                        <div className="text-xs text-gray-400 mt-2">
                          Source: {source.metadata.source}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SearchComponent;