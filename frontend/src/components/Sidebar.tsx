import React from 'react';
import './Sidebar.css';

const Sidebar: React.FC = () => {
  return (
    <div className="sidebar">
      <div className="header">
      <h1 className="team-title">
          <span className="team">Team</span>
          <br />
          <span className="medical">Medical</span>
        </h1>
      </div>

      <div className="top-section">
        <div className="sidebar-item">
          <span className="icon">🏥</span> Dashboard
        </div>
        <div className="sidebar-item">
          <span className="icon">📋</span> Patient Records
        </div>
        <div className="sidebar-item">
          <span className="icon">🩺</span> Appointments
        </div>
        <div className="sidebar-item">
          <span className="icon">📊</span> Analytics
        </div>
      </div>

      <div className="middle-section">
        <h3 className="section-title">Today</h3>
        <div className="sidebar-item">
          <span className="bullet">•</span> New Appointment Requests
        </div>
        <div className="sidebar-item">
          <span className="bullet">•</span> Check Patient Reports
        </div>
        <div className="sidebar-item">
          <span className="bullet">•</span> Update Inventory
        </div>
      </div>

      <div className="bottom-section">
        <div className="sidebar-item">
          Settings
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
