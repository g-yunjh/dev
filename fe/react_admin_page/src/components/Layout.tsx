import { ReactNode } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Home, Package, MessageSquare, LogOut, User } from 'lucide-react'
import { logout, getCurrentAdmin } from '../lib/auth'

interface LayoutProps {
  children: ReactNode
}

const Layout = ({ children }: LayoutProps) => {
  const location = useLocation()
  const navigate = useNavigate()
  const currentAdmin = getCurrentAdmin()

  const navigation = [
    { name: '대시보드', href: '/', icon: Home },
    { name: '가구 관리', href: '/furniture', icon: Package },
    { name: '문의 관리', href: '/contacts', icon: MessageSquare },
  ]

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header with inline navigation */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="px-3 py-2">
          <div className="flex items-center justify-between mb-2">
            <h1 className="text-lg font-semibold text-gray-900">가져가구 관리자</h1>
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1 text-sm text-gray-600">
                <User className="w-4 h-4" />
                <span>{currentAdmin?.name || '관리자'}</span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center gap-1 px-2 py-1 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded transition-colors"
              >
                <LogOut className="w-4 h-4" />
                <span>로그아웃</span>
              </button>
            </div>
          </div>
          <nav>
            <ul className="flex items-stretch gap-2">
              {navigation.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.href
                return (
                  <li key={item.name} className="flex-1">
                    <Link
                      to={item.href}
                      className={`flex items-center justify-center w-full px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                        isActive
                          ? 'bg-primary-100 text-primary-700'
                          : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                      }`}
                    >
                      <Icon className="w-4 h-4 mr-2" />
                      {item.name}
                    </Link>
                  </li>
                )
              })}
            </ul>
          </nav>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1">
        <div className="p-4">
          {children}
        </div>
      </main>
    </div>
  )
}

export default Layout
