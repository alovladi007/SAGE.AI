import React, { useState } from 'react';
import LandingPage from './LandingPage';
import DashboardApp from './DashboardApp';

const App = () => {
  const [showDashboard, setShowDashboard] = useState(false);

  if (showDashboard) {
    return <DashboardApp />;
  }

  return <LandingPage onGetStarted={() => setShowDashboard(true)} />;
};

export default App;
