import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Navbar from './components/Navbar';
import Footer from './components/Footer';
import SafeModeBanner from './components/SafeModeBanner';

import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import Playground from './pages/Playground';
import Versions from './pages/Versions';
import Health from './pages/Health';
import SettingsPage from './pages/Settings';

import { SystemAPI } from './services/api';

export default function App() {
  const [integrity, setIntegrity] = useState(null);

  const fetchIntegrity = async () => {
    try {
      const res = await SystemAPI.getIntegrity();
      if (res && res.data) {
        setIntegrity(res.data);
      }
    } catch (e) {
      console.warn('Failed to fetch system integrity:', e);
    }
  };

  useEffect(() => {
    fetchIntegrity();
    const interval = setInterval(fetchIntegrity, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Router>
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-blue-600 selection:text-white">
        
        {/* Global Safe Mode Alert Banner if Integrity Fails */}
        <SafeModeBanner integrity={integrity} onResolve={fetchIntegrity} />

        {/* Global Corporate Navbar */}
        <Navbar integrity={integrity} />

        {/* Page Viewport */}
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route 
              path="/dashboard" 
              element={<Dashboard integrity={integrity} onRefreshIntegrity={fetchIntegrity} />} 
            />
            <Route 
              path="/playground" 
              element={<Playground integrity={integrity} />} 
            />
            <Route 
              path="/versions" 
              element={<Versions onRefreshIntegrity={fetchIntegrity} />} 
            />
            <Route path="/health" element={<Health />} />
            <Route 
              path="/settings" 
              element={<SettingsPage integrity={integrity} onRefreshIntegrity={fetchIntegrity} />} 
            />
          </Routes>
        </main>

        {/* Global Footer */}
        <Footer />

      </div>
    </Router>
  );
}
