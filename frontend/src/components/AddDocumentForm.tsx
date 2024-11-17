import React, { useState } from 'react';
import { addDocument } from '../services/api';
import { useNavigate } from 'react-router-dom';

const AddDocumentForm: React.FC = () => {
  const [content, setContent] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await addDocument({ content });
      console.log('Document added:', response.data);
      navigate('/'); // Redirect to home or another page after successful submission
    } catch (error) {
      console.error('Error adding document:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Enter document content"
      />
      <button type="submit">Add Document</button>
    </form>
  );
};

export default AddDocumentForm;