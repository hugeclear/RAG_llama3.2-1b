import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import AddDocumentForm from './components/AddDocumentForm';
import SearchComponent from './components/SearchComponent';
import StatsComponent from './components/StatsComponent';
import HealthComponent from './components/HealthComponent';
import './styles.css';

const App: React.FC = () => {
  return (
    <Router>
      <div className="app-container">
        <div className="main-content">
          <h1>RAG System</h1>
          <nav className="main-nav">
            <Link to="/add" className="large-button">Add New Document</Link>
            <Link to="/search" className="large-button">Generate Answer from Documents</Link>
          </nav>
        </div>

        <Routes>
          <Route path="/add" element={<AddDocumentForm />} />
          <Route path="/search" element={<SearchComponent />} />
        </Routes>

        {/* Stats and Health components positioned in the bottom right */}
        <div className="floating-components">
          <StatsComponent />
          <HealthComponent />
        </div>
      </div>
    </Router>
  );
};

export default App;
