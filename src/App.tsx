import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import FurnitureList from './pages/FurnitureList'
import FurnitureDetail from './pages/FurnitureDetail'
import ContactList from './pages/ContactList'
import ContactDetail from './pages/ContactDetail'
import { isAuthenticated } from './lib/auth'

function App() {
  return (
    <Router>
      <div className="mobile-container">
        <Routes>
          <Route 
            path="/login" 
            element={isAuthenticated() ? <Navigate to="/" replace /> : <Login />} 
          />
          <Route path="/" element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/furniture" element={
            <ProtectedRoute>
              <Layout>
                <FurnitureList />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/furniture/:id" element={
            <ProtectedRoute>
              <Layout>
                <FurnitureDetail />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/contacts" element={
            <ProtectedRoute>
              <Layout>
                <ContactList />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/contacts/:id" element={
            <ProtectedRoute>
              <Layout>
                <ContactDetail />
              </Layout>
            </ProtectedRoute>
          } />
        </Routes>
      </div>
    </Router>
  )
}

export default App
