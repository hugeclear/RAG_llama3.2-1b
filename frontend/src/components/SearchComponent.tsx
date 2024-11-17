import React, { useState } from 'react';
import { search } from '../services/api';
import { useNavigate } from 'react-router-dom';

interface SearchResult {
  content: string;
  [key: string]: any;
}

const SearchComponent: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const navigate = useNavigate();

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await search({ query });
      setResults(response.data.results);
    } catch (error) {
      console.error('Error performing search:', error);
    }
  };

  return (
    <div>
      <form onSubmit={handleSearch}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search query"
        />
        <button type="submit">Search</button>
      </form>
      <ul>
        {results.map((result, index) => (
          <li key={index}>{result.content}</li>
        ))}
      </ul>
      <button onClick={() => navigate('/')}>Go Home</button>
    </div>
  );
};

export default SearchComponent;