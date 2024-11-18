import React, { useState, useCallback } from 'react';
import { search, SearchResponse } from '../services/api';
import { useNavigate } from 'react-router-dom';

const SearchComponent: React.FC = () => {
  const [query, setQuery] = useState('');
  const [searchResult, setSearchResult] = useState<SearchResponse | null>(null);
  const [showSources, setShowSources] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSearch = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setShowSources(false);

    try {
      const response = await search({ query });
      console.log('Full response:', response); // デバッグログ追加
      console.log('Response data:', response.data); // デバッグログ追加
      
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
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-4xl mx-auto p-6">
        <form onSubmit={handleSearch} className="mb-8">
          <div className="flex gap-4">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your question"
              className="flex-1 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 shadow-sm bg-white"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !query.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 
                       disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
            >
              {isLoading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </form>

        {error && (
          <div className="p-4 mb-6 bg-red-50 border border-red-200 rounded-lg text-red-600">
            {error}
          </div>
        )}

{searchResult && (
  <div className="space-y-6">
    <div className="bg-white p-6 rounded-lg shadow-lg border">
      <h3 className="text-xl font-semibold mb-4 text-gray-900">Answer:</h3>
      <div className="text-gray-700 whitespace-pre-wrap leading-relaxed">
        {searchResult.answer}
      </div>

      {searchResult.sources && searchResult.sources.length > 0 && (
        <div className="mt-6">
          <button
            onClick={() => setShowSources(!showSources)}
            className="inline-flex items-center px-4 py-2 text-sm font-medium 
                     text-blue-600 hover:text-blue-800 focus:outline-none"
          >
            {showSources ? 'Hide Sources ↑' : 'Show Sources ↓'}
          </button>

          {showSources && (
            <div className="mt-4 space-y-4">
              <h4 className="font-semibold text-gray-900">Sources:</h4>
              {searchResult.sources.map((source, index) => (
                <div
                  key={index}
                  className="p-4 bg-gray-50 rounded-lg border border-gray-200"
                >
                  <div className="text-gray-600 mb-2 whitespace-pre-wrap">
                    {source.content}
                  </div>
                  {source.metadata?.source && (
                    <div className="text-sm text-gray-500">
                      <p>Source: {source.metadata.source}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  </div>
)}

        <div className="mt-8 text-center">
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 
                     underline focus:outline-none"
          >
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
};

export default SearchComponent;