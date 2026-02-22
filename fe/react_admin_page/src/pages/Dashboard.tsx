import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Package, MessageSquare, TrendingUp, Clock, CheckCircle } from 'lucide-react'
import { furniture } from '../lib/furniture'
import { contact } from '../lib/contact'

interface DashboardStats {
  sellingFurniture: number
  soldFurniture: number
  pendingContacts: number
  completedContacts: number
}

const Dashboard = () => {
  const [stats, setStats] = useState<DashboardStats>({
    sellingFurniture: 0,
    soldFurniture: 0,
    pendingContacts: 0,
    completedContacts: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [allFurniture, soldFurniture, pendingContacts, completedContacts] = await Promise.all([
          furniture.getAll({}, { page: 1, limit: 1 }),
          furniture.getAll({ is_sold: true }, { page: 1, limit: 1 }),
          contact.getAll({ page: 1, limit: 1 }, 'pending'),
          contact.getAll({ page: 1, limit: 1 }, 'completed')
        ])

        setStats({
          sellingFurniture: Math.max(0, allFurniture.total - soldFurniture.total),
          soldFurniture: soldFurniture.total,
          pendingContacts: pendingContacts.total,
          completedContacts: completedContacts.total
        })
      } catch (error) {
        console.error('Failed to fetch dashboard stats:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const statCards = [
    {
      title: '판매 중',
      value: stats.sellingFurniture,
      icon: Package,
      color: 'bg-blue-500',
      link: '/furniture?filter=onsale'
    },
    {
      title: '판매 완료',
      value: stats.soldFurniture,
      icon: TrendingUp,
      color: 'bg-green-500',
      link: '/furniture?filter=sold'
    },
    {
      title: '처리 대기',
      value: stats.pendingContacts,
      icon: Clock,
      color: 'bg-orange-500',
      link: '/contacts?filter=pending'
    },
    {
      title: '처리 완료',
      value: stats.completedContacts,
      icon: CheckCircle,
      color: 'bg-emerald-500',
      link: '/contacts?filter=completed'
    }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">대시보드</h2>
        <p className="text-gray-600">가져가구 관리자 페이지에 오신 것을 환영합니다.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4">
        {statCards.map((stat) => {
          const Icon = stat.icon
          return (
            <Link
              key={stat.title}
              to={stat.link}
              className="card hover:shadow-md transition-shadow"
            >
              <div className="flex items-center">
                <div className={`p-3 rounded-lg ${stat.color}`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
              </div>
            </Link>
          )
        })}
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">빠른 작업</h3>
        <div className="grid grid-cols-1 gap-3">
          <Link
            to="/furniture"
            className="flex items-center p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
          >
            <Package className="w-5 h-5 text-primary-600 mr-3" />
            <span className="font-medium">가구 목록 보기</span>
          </Link>
          <Link
            to="/contacts"
            className="flex items-center p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
          >
            <MessageSquare className="w-5 h-5 text-primary-600 mr-3" />
            <span className="font-medium">문의 목록 보기</span>
          </Link>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
