import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Search, Filter, MessageSquare, Clock, CheckCircle } from 'lucide-react'
import { contact, type Contact } from '../lib/contact'
import { format } from 'date-fns'
import { ko } from 'date-fns/locale'

const ContactList = () => {
  const [searchParams] = useSearchParams()
  const [contactList, setContactList] = useState<Contact[]>([])
  const [loading, setLoading] = useState(true)
  const [totalPages, setTotalPages] = useState(1)
  const [currentPage, setCurrentPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [showFilters, setShowFilters] = useState(false)

  const statusLabels = {
    pending: '처리 대기',
    completed: '처리 완료'
  }

  const statusColors = {
    pending: 'bg-orange-100 text-orange-800',
    completed: 'bg-green-100 text-green-800'
  }

  const statusIcons = {
    pending: Clock,
    completed: CheckCircle
  }

  const normalizeStatus = (value: string): 'pending' | 'completed' =>
    value === 'completed' ? 'completed' : 'pending'

  useEffect(() => {
    fetchContacts()
  }, [currentPage, statusFilter])

  // Sync URL filter -> internal filters (pending/completed)
  useEffect(() => {
    const f = searchParams.get('filter')
    if (f === 'pending' || f === 'completed') {
      setStatusFilter(f)
    }
  }, [searchParams])

  const fetchContacts = async () => {
    try {
      setLoading(true)
      const response = await contact.getAll({ page: currentPage, limit: 10 }, statusFilter || undefined)
      setContactList(response.data)
      setTotalPages(response.totalPages)
    } catch (error) {
      console.error('Failed to fetch contacts:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleStatusChange = async (id: string, newStatus: 'pending' | 'processing' | 'completed') => {
    try {
      await contact.updateStatus(id, newStatus)
      fetchContacts()
    } catch (error) {
      console.error('Failed to update contact status:', error)
      alert('상태 변경에 실패했습니다.')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">문의 관리</h2>
          <p className="text-gray-600">고객 문의를 확인하고 처리합니다.</p>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="card">
        <div className="flex flex-col space-y-4">
          <div className="flex items-center space-x-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="문의 제목으로 검색..."
                className="input-field pl-10"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="btn-secondary flex items-center"
            >
              <Filter className="w-4 h-4 mr-2" />
              필터
            </button>
          </div>

          {showFilters && (
            <div className="pt-4 border-t border-gray-200">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">처리 상태</label>
                <select
                  className="select-field"
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <option value="">전체</option>
                  <option value="pending">처리 대기</option>
                  <option value="completed">처리 완료</option>
                </select>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Contact List */}
      <div className="space-y-4">
        {contactList.length === 0 ? (
          <div className="card text-center py-12">
            <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">문의가 없습니다</h3>
            <p className="text-gray-600">새로운 문의가 등록되면 여기에 표시됩니다.</p>
          </div>
        ) : (
          contactList.map((item) => {
            const normalized = normalizeStatus(item.status as any)
            const StatusIcon = statusIcons[normalized]
            return (
              <div key={item.id} className="card overflow-hidden">
                <div className="flex items-start justify-between min-w-0">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 truncate">{item.subject}</h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[normalized]}`}>
                        {statusLabels[normalized]}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3 line-clamp-2 break-words">{item.message}</p>
                    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-gray-500">
                      <span>{item.name}</span>
                      <span>{item.email}</span>
                      <span>{format(new Date(item.created_at), 'yyyy.MM.dd HH:mm', { locale: ko })}</span>
                    </div>
                  </div>
                  <div className="flex flex-col items-end space-y-2 ml-4 shrink-0">
                    <div className="flex items-center space-x-1">
                      <StatusIcon className="w-4 h-4" />
                    </div>
                    <div className="flex flex-col space-y-1">
                      <select
                        value={normalized}
                        onChange={(e) => handleStatusChange(item.id, e.target.value as 'pending' | 'completed')}
                        className="text-xs px-2 py-1 border border-gray-300 rounded whitespace-nowrap"
                      >
                        <option value="pending">대기</option>
                        <option value="completed">완료</option>
                      </select>
                    </div>
                  </div>
                </div>
                <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
                  <div className="flex items-center space-x-2">
                    <a
                      href={`mailto:${item.email}`}
                      className="text-sm text-primary-600 hover:text-primary-700"
                    >
                      이메일 답장
                    </a>
                  </div>
                  <Link
                    to={`/contacts/${item.id}`}
                    className="text-sm text-primary-600 hover:text-primary-700"
                  >
                    자세히 보기 →
                  </Link>
                </div>
              </div>
            )
          })
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center space-x-2">
          <button
            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
            className="px-3 py-2 rounded-lg border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            이전
          </button>
          <span className="px-4 py-2 text-sm text-gray-600">
            {currentPage} / {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
            disabled={currentPage === totalPages}
            className="px-3 py-2 rounded-lg border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            다음
          </button>
        </div>
      )}
    </div>
  )
}

export default ContactList
