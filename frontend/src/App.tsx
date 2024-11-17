import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import AddDocumentForm from './components/AddDocumentForm';
import SearchComponent from './components/SearchComponent';
import StatsComponent from './components/StatsComponent';
import HealthComponent from './components/HealthComponent';

const App: React.FC = () => {
  return (
    <Router>
      <div>
        <h1>RAG System Frontend</h1>
        <nav>
          <ul>
            <li><Link to="/add">Add Document</Link></li>
            <li><Link to="/search">Search</Link></li>
            <li><Link to="/stats">System Stats</Link></li>
            <li><Link to="/health">Health Check</Link></li>
          </ul>
        </nav>
        <Routes>
          <Route path="/add" element={<AddDocumentForm />} />
          <Route path="/search" element={<SearchComponent />} />
          <Route path="/stats" element={<StatsComponent />} />
          <Route path="/health" element={<HealthComponent />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;