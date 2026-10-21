import { lazy, Suspense } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import PortfolioPage from './pages/PortfolioPage'

// The admin bundle is only downloaded when someone visits /admin.
const AdminApp = lazy(() => import('./pages/admin/AdminApp'))

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<PortfolioPage />} />
        <Route path="/admin/*" element={<Suspense fallback={null}><AdminApp /></Suspense>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
