import { Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from '../../context/AuthContext'
import { ToastProvider } from '../../context/ToastContext'
import '../../styles/admin.css'
import AccountPage from './AccountPage'
import AdminLayout from './AdminLayout'
import CollectionPage from './CollectionPage'
import DashboardPage from './DashboardPage'
import LoginPage from './LoginPage'
import MessagesPage from './MessagesPage'
import ResumePage from './ResumePage'
import SectionsPage from './SectionsPage'

function Guarded() {
  const { email, ready } = useAuth()
  if (!ready) return <div className="adm-center">Checking session…</div>
  if (!email) return <Navigate to="/admin/login" replace />
  return (
    <AdminLayout>
      <Routes>
        <Route index element={<DashboardPage />} />
        <Route path="content" element={<SectionsPage />} />
        <Route path="c/:collection" element={<CollectionPage />} />
        <Route path="messages" element={<MessagesPage />} />
        <Route path="resume" element={<ResumePage />} />
        <Route path="account" element={<AccountPage />} />
        <Route path="*" element={<Navigate to="/admin" replace />} />
      </Routes>
    </AdminLayout>
  )
}

export default function AdminApp() {
  return (
    <AuthProvider>
      <ToastProvider>
        <div className="adm">
          <Routes>
            <Route path="login" element={<LoginPage />} />
            <Route path="*" element={<Guarded />} />
          </Routes>
        </div>
      </ToastProvider>
    </AuthProvider>
  )
}
