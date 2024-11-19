import React, { useState, useCallback } from 'react';
import { search, SearchResponse } from '../services/api';


const SearchComponent: React.FC = () => {
  const [query, setQuery] = useState('');
  const [currentModel, setCurrentModel] = useState('llama');
  const [searchResult, setSearchResult] = useState<SearchResponse | null>(null);
  const [showSources, setShowSources] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);


  const handleSearch = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setShowSources(false);

    try {
      const response = await search({ 
        query,
        model_type: currentModel  // 現在選択されているモデルを使用
      });
      
      if (response && response.data) {
        setSearchResult(response.data);
      } else {
        setError('No response received');
      }
    } catch (error) {
      console.error('Search error:', error);
      setError(error instanceof Error ? error.message : 'An error occurred during search');
    } finally {
      setIsLoading(false);
    }
  }, [query, currentModel]);

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-4xl mx-auto p-6">
        {/* モデル選択UI */}
{/* モデル選択UI */}
<div className="mb-4">
  <label className="block text-sm font-medium text-gray-700 mb-2">
    Select Model
  </label>
  <div className="flex space-x-4">
    <button
      onClick={() => setCurrentModel('llama')}
      className={`px-4 py-2 rounded ${
        currentModel === 'llama'
          ? 'bg-blue-600 text-white'
          : 'bg-gray-200 text-gray-700'
      } hover:bg-blue-700 hover:text-white transition-colors`}
      disabled={isLoading}
    >
      llama3.2-1b
    </button>
    <button
      onClick={() => setCurrentModel('codellama')}
      className={`px-4 py-2 rounded ${
        currentModel === 'codellama'
          ? 'bg-blue-600 text-white'
          : 'bg-gray-200 text-gray-700'
      } hover:bg-blue-700 hover:text-white transition-colors`}
      disabled={isLoading}
    >
      codellama_merged_slerp
    </button>
  </div>
  <div className="mt-2 text-xs text-gray-500">
    {currentModel === 'llama' 
      ? 'General purpose language model'
      : 'Specialized model for code-related queries'}
  </div>
</div>

        {/* 検索フォーム */}
        <form onSubmit={handleSearch} className="mb-8">
          <div className="flex gap-4">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={currentModel === 'codellama' ? "Enter your programming or technical question...": "Enter your question..."}
              className="flex-1 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 shadow-sm bg-white"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !query.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 
                       disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
            >
              {isLoading ? (
                <div className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Generating...
                </div>
              ) : 'Search'}
            </button>
          </div>
        </form>

        {error && (
          <div className="p-4 mb-6 bg-red-50 border border-red-200 rounded-lg text-red-600">
            {error}
          </div>
        )}

        {/* 結果表示 */}
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
      </div>
    </div>
  );
};

export default SearchComponent;

