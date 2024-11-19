import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import AddDocumentForm from './components/AddDocumentForm';
import SearchComponent from './components/SearchComponent';
import StatsComponent from './components/StatsComponent';
import HealthComponent from './components/HealthComponent';
import './styles.css';
import Sidebar from './components/Sidebar';

const App: React.FC = () => {
  return (
    <Router>
      <div className="app-container">
         <Sidebar />
        <div className="main-content">
          <h1>Medical & Code RAG</h1>
          <div className="genrate-content">
              <AddDocumentForm />
              <SearchComponent />
          </div>
          {/* <div className="floating-components">
            <StatsComponent />
            <HealthComponent />
          </div> */}
        </div>
      </div>
    </Router>
  );
};

export default App;
