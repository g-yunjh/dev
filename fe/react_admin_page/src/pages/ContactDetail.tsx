import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Mail, Download, File, Clock, CheckCircle } from 'lucide-react'
import { contact, type Contact, type ContactAttachment } from '../lib/contact'
import { storage } from '../lib/storage'
import { format } from 'date-fns'
import { ko } from 'date-fns/locale'

const ContactDetail = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [contactItem, setContactItem] = useState<Contact | null>(null)
  const [attachments, setAttachments] = useState<ContactAttachment[]>([])
  const [loading, setLoading] = useState(true)

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
    if (id) {
      fetchContact()
    }
  }, [id])

  const fetchContact = async () => {
    if (!id) return

    try {
      setLoading(true)
      const [contactData, attachmentData] = await Promise.all([
        contact.getById(id),
        contact.getAttachments(id)
      ])

      if (contactData) {
        setContactItem(contactData)
        setAttachments(attachmentData)
      } else {
        navigate('/contacts')
      }
    } catch (error) {
      console.error('Failed to fetch contact:', error)
      navigate('/contacts')
    } finally {
      setLoading(false)
    }
  }

  const handleStatusChange = async (newStatus: 'pending' | 'processing' | 'completed') => {
    if (!id || !contactItem) return

    try {
      const updatedContact = await contact.updateStatus(id, newStatus)
      setContactItem(updatedContact)
    } catch (error) {
      console.error('Failed to update contact status:', error)
      alert('상태 변경에 실패했습니다.')
    }
  }

  const handleDownloadAttachment = async (attachment: ContactAttachment) => {
    try {
      const blob = await storage.downloadAttachment(attachment.contact_id, attachment.file_path)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = attachment.file_name
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Failed to download attachment:', error)
      alert('파일 다운로드에 실패했습니다.')
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!contactItem) {
    return (
      <div className="text-center py-12">
        <Mail className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">문의를 찾을 수 없습니다</h3>
        <button
          onClick={() => navigate('/contacts')}
          className="btn-primary"
        >
          목록으로 돌아가기
        </button>
      </div>
    )
  }

  const normalized = normalizeStatus(contactItem.status)
  const StatusIcon = statusIcons[normalized]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/contacts')}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">문의 상세</h2>
            <p className="text-gray-600">문의 내용을 확인하고 처리합니다.</p>
          </div>
        </div>
        {/* 상단 상태 셀렉터 제거: 하단 빠른 작업으로만 상태 변경 */}
      </div>

      {/* Status Badge */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <StatusIcon className="w-6 h-6 text-gray-400" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{contactItem.subject}</h3>
              <p className="text-sm text-gray-600">
                {format(new Date(contactItem.created_at), 'yyyy년 MM월 dd일 HH:mm', { locale: ko })}
              </p>
            </div>
          </div>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColors[normalized]}`}>
            {statusLabels[normalized]}
          </span>
        </div>
      </div>

      {/* Contact Info */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">문의자 정보</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">이름</label>
            <p className="text-gray-900">{contactItem.name}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">이메일</label>
            <div className="flex items-center">
              <Mail className="w-4 h-4 text-gray-400 mr-2" />
              <a
                href={`mailto:${contactItem.email}`}
                className="text-primary-600 hover:text-primary-700"
              >
                {contactItem.email}
              </a>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">문의 제목</label>
            <p className="text-gray-900">{contactItem.subject}</p>
          </div>
        </div>
      </div>

      {/* Message */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">문의 내용</h3>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-gray-900 whitespace-pre-wrap">{contactItem.message}</p>
        </div>
      </div>

      {/* Attachments */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">첨부파일</h3>
        {attachments.length === 0 ? (
          <p className="text-sm text-gray-500">첨부파일이 없습니다.</p>
        ) : (
          <div className="space-y-3">
            {attachments.map((attachment, idx) => {
              const publicUrl = storage.getContactAttachmentUrl(attachment.contact_id, attachment.file_path)
              return (
                <div
                  key={attachment.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center space-x-3 min-w-0">
                    <File className="w-5 h-5 text-gray-400" />
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate" title={attachment.file_name}>
                        파일 {idx + 1}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatFileSize(attachment.file_size)} • {attachment.file_type}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2 shrink-0">
                    <a
                      href={publicUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn-secondary text-sm px-3 py-2"
                    >
                      열기
                    </a>
                    <button
                      onClick={() => handleDownloadAttachment(attachment)}
                      className="btn-secondary flex items-center text-sm"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      다운로드
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">빠른 작업</h3>
        <div className="flex flex-col space-y-3">
          <a
            href={`mailto:${contactItem.email}?subject=Re: ${contactItem.subject}`}
            className="btn-primary flex items-center justify-center"
          >
            <Mail className="w-4 h-4 mr-2" />
            이메일 답장
          </a>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => handleStatusChange('pending')}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                normalized === 'pending'
                  ? 'bg-orange-100 text-orange-800'
                  : 'bg-gray-100 text-gray-600 hover:bg-orange-50'
              }`}
            >
              대기
            </button>
            <button
              onClick={() => handleStatusChange('completed')}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                normalized === 'completed'
                  ? 'bg-green-100 text-green-800'
                  : 'bg-gray-100 text-gray-600 hover:bg-green-50'
              }`}
            >
              완료
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ContactDetail
