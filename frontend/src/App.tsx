import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './hooks/useStore';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Transactions from './pages/Transactions';
import Users from './pages/Users';
import Alerts from './pages/Alerts';
import Analytics from './pages/Analytics';

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/*"
          element={
            <PrivateRoute>
              <Layout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/transactions" element={<Transactions />} />
                  <Route path="/users" element={<Users />} />
                  <Route path="/alerts" element={<Alerts />} />
                  <Route path="/analytics" element={<Analytics />} />
                </Routes>
              </Layout>
            </PrivateRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;