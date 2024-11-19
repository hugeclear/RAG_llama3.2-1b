import React, { useState } from 'react';
import { addDocument } from '../services/api';

const AddDocumentForm: React.FC = () => {
  const [url, setUrl] = useState('');
  const [category, setCategory] = useState('general');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await addDocument({ url, category });
      setSuccess('Document added successfully');
      setUrl('');
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to add document');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Document URL
          </label>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="https://example.com"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Category
          </label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="general">General</option>
            <option value="code">Code</option>
          </select>
        </div>

        {error && (
          <div className="text-red-600 text-sm">{error}</div>
        )}

        {success && (
          <div className="text-green-600 text-sm">{success}</div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          {isLoading ? 'Adding...' : 'Add Document'}
        </button>
      </form>
    </div>
  );
};

export default AddDocumentForm;