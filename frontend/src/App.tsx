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
            {/* <div className="w-full md:w-1/2 border-b md:border-b-0 md:border-r border-gray-600"> */}
              <AddDocumentForm />
            {/* </div>
            <div className="w-full md:w-1/2"> */}
              <SearchComponent />
          </div>
          {/* <div className="floating-components">
            <StatsComponent />
            <HealthComponent />
          </div> */}
        </div>
        {/* Stats and Health components positioned in the bottom right */}
      </div>
    </Router>
  );
};

export default App;
