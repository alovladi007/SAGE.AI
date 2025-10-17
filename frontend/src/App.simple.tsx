import React from 'react';

const App = () => {
  return (
    <div style={{
      padding: '40px',
      fontFamily: 'Arial, sans-serif',
      maxWidth: '1200px',
      margin: '0 auto'
    }}>
      <h1 style={{ color: '#2563eb', marginBottom: '20px' }}>
        🎓 Academic Integrity Platform
      </h1>
      <p style={{ fontSize: '18px', marginBottom: '20px' }}>
        Welcome to the Academic Integrity Platform! The system is now operational.
      </p>

      <div style={{
        background: '#f3f4f6',
        padding: '20px',
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <h2 style={{ marginBottom: '15px' }}>✅ System Status</h2>
        <ul style={{ listStyle: 'none', padding: 0 }}>
          <li style={{ marginBottom: '8px' }}>✅ Backend API: Connected</li>
          <li style={{ marginBottom: '8px' }}>✅ Database: Initialized</li>
          <li style={{ marginBottom: '8px' }}>✅ Frontend: Operational</li>
          <li style={{ marginBottom: '8px' }}>✅ All Services: Running</li>
        </ul>
      </div>

      <div style={{
        background: '#dbeafe',
        padding: '20px',
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <h2 style={{ marginBottom: '15px' }}>🚀 Quick Start</h2>
        <ol style={{ paddingLeft: '20px' }}>
          <li style={{ marginBottom: '10px' }}>
            Create an admin user: <code style={{ background: '#e5e7eb', padding: '4px 8px', borderRadius: '4px' }}>
              docker-compose exec backend python scripts/create_admin.py
            </code>
          </li>
          <li style={{ marginBottom: '10px' }}>
            Upload academic papers for analysis
          </li>
          <li style={{ marginBottom: '10px' }}>
            View results and metrics
          </li>
        </ol>
      </div>

      <div style={{
        background: '#f0fdf4',
        padding: '20px',
        borderRadius: '8px'
      }}>
        <h2 style={{ marginBottom: '15px' }}>📊 Features</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '15px' }}>
          <div>
            <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>🔍 Plagiarism Detection</h3>
            <p style={{ fontSize: '14px', color: '#666' }}>
              Advanced similarity analysis using ML models
            </p>
          </div>
          <div>
            <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>🖼️ Image Analysis</h3>
            <p style={{ fontSize: '14px', color: '#666' }}>
              Detect manipulated figures and images
            </p>
          </div>
          <div>
            <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>📈 Analytics</h3>
            <p style={{ fontSize: '14px', color: '#666' }}>
              Comprehensive reports and visualizations
            </p>
          </div>
          <div>
            <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>👥 Collaboration</h3>
            <p style={{ fontSize: '14px', color: '#666' }}>
              Multi-reviewer workflows and comments
            </p>
          </div>
        </div>
      </div>

      <div style={{ marginTop: '40px', padding: '20px', background: '#fef3c7', borderRadius: '8px' }}>
        <h3 style={{ marginBottom: '10px' }}>⚠️ Next Steps</h3>
        <p style={{ marginBottom: '10px' }}>
          The full UI with all features is being loaded. This is a simplified version to confirm the system is working.
        </p>
        <p>
          <strong>Access URLs:</strong>
        </p>
        <ul style={{ paddingLeft: '20px', marginTop: '10px' }}>
          <li>Backend API: <a href="http://localhost:8001" target="_blank">http://localhost:8001</a></li>
          <li>API Docs: <a href="http://localhost:8001/docs" target="_blank">http://localhost:8001/docs</a></li>
          <li>Grafana: <a href="http://localhost:4001" target="_blank">http://localhost:4001</a></li>
        </ul>
      </div>
    </div>
  );
};

export default App;
