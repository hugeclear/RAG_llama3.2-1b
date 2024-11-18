import React, { useState } from 'react';
import { addDocument } from '../services/api';
import { useNavigate } from 'react-router-dom';

const AddDocumentForm: React.FC = () => {
  const [url, setUrl] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

// AddDocumentForm.tsxの一部を修正

const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setError(null);
  setIsLoading(true);

  try {
    const response = await addDocument({ url });
    console.log('Document added:', response.data);
    
    // レスポンスの内容をチェック
    if (response.data.status === "success") {
      navigate('/');
    } else {
      setError(response.data.message || "Failed to process document");
    }
  } catch (error: any) {
    setError(error.response?.data?.detail || error.message || "Failed to add document");
    console.error('Error adding document:', error);
  } finally {
    setIsLoading(false);
  }
};


  return (
    <div className="max-w-md mx-auto p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="url" className="block text-sm font-medium text-gray-700">
            Document URL
          </label>
          <input
            id="url"
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/document"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            disabled={isLoading}
            required
          />
        </div>

        {error && (
          <div className="text-red-600 text-sm">
            {error}
          </div>
        )}

        <button
          type="submit"
          className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
            isLoading ? 'opacity-50 cursor-not-allowed' : ''
          }`}
          disabled={isLoading}
        >
          {isLoading ? 'Adding Document...' : 'Add Document'}
        </button>
      </form>
    </div>
  );
};

export default AddDocumentForm;