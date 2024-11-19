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
    <div className="content-box">
      <h2 className="text-xl font-semibold mb-4">Add Document</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-sm mb-2">Document URL</label>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com"
            className="input-area"
            required
          />
        </div>

        <div className="mb-4">
          <label className="block text-sm mb-2">Category</label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="input-area"
          >
            <option value="general">General</option>
            <option value="code">Code</option>
          </select>
        </div>

        <div className="button-wrapper">
          <button
            type="submit"
            disabled={isLoading}
            className="submit-button"
          >
            {isLoading ? 'Adding...' : 'Add Document'}
          </button>
        </div>
      </form>

      {error && (
        <div className="mt-4 text-red-400">{error}</div>
      )}

      {success && (
        <div className="mt-4 text-green-400">{success}</div>
      )}
    </div>
  );
};

export default AddDocumentForm;
