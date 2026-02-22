import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Edit, Trash2, Phone, MapPin, Calendar, Package } from 'lucide-react'
import { furniture, type Furniture } from '../lib/furniture'
import { format } from 'date-fns'
import { ko } from 'date-fns/locale'

const FurnitureDetail = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [furnitureItem, setFurnitureItem] = useState<Furniture | null>(null)
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [formData, setFormData] = useState<Partial<Furniture>>({})

  const conditionLabels: { new: string; like_new: string; good: string; fair: string; poor: string } = {
    new: '새상품',
    like_new: '거의 새것',
    good: '양호',
    fair: '보통',
    poor: '나쁨'
  }

  const locationLabels: Record<string, string> = {
    insa: '명륜',
    jagwa: '율전'
  }

  const getLocationLabel = (value?: string) => {
    if (!value) return ''
    return locationLabels[value] ?? value
  }

  useEffect(() => {
    if (id) {
      fetchFurniture()
    }
  }, [id])

  const fetchFurniture = async () => {
    if (!id) return

    try {
      setLoading(true)
      const item = await furniture.getById(id)
      if (item) {
        setFurnitureItem(item)
        setFormData(item)
      } else {
        navigate('/furniture')
      }
    } catch (error) {
      console.error('Failed to fetch furniture:', error)
      navigate('/furniture')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!id || !furnitureItem) return

    try {
      await furniture.update(id, formData)
      setFurnitureItem({ ...furnitureItem, ...formData })
      setEditing(false)
    } catch (error) {
      console.error('Failed to update furniture:', error)
      alert('수정에 실패했습니다.')
    }
  }

  const handleDelete = async () => {
    if (!id) return

    if (!confirm('정말로 이 가구를 삭제하시겠습니까?')) return

    try {
      await furniture.delete(id)
      navigate('/furniture')
    } catch (error) {
      console.error('Failed to delete furniture:', error)
      alert('삭제에 실패했습니다.')
    }
  }

  const handleInputChange = (field: keyof Furniture, value: unknown) => {
    setFormData((prev: Partial<Furniture>) => ({ ...prev, [field]: value as any }))
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!furnitureItem) {
    return (
      <div className="text-center py-12">
        <Package className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">가구를 찾을 수 없습니다</h3>
        <button
          onClick={() => navigate('/furniture')}
          className="btn-primary"
        >
          목록으로 돌아가기
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-3">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/furniture')}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">가구 상세</h2>
            <p className="text-gray-600">가구 정보를 확인하고 수정할 수 있습니다.</p>
          </div>
        </div>
        <div className="w-full flex flex-wrap items-center justify-end gap-2">
          {editing ? (
            <>
              <button
                onClick={() => {
                  setEditing(false)
                  setFormData(furnitureItem)
                }}
                className="btn-secondary"
              >
                취소
              </button>
              <button
                onClick={handleSave}
                className="btn-primary"
              >
                저장
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => setEditing(true)}
                className="btn-secondary flex items-center justify-center"
              >
                <Edit className="w-4 h-4 mr-2" />
                수정
              </button>
              <button
                onClick={handleDelete}
                className="btn-danger flex items-center justify-center"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                삭제
              </button>
            </>
          )}
        </div>
      </div>

      {/* Images */}
      {furnitureItem.images.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">이미지</h3>
          <div className="grid grid-cols-2 gap-4">
            {furnitureItem.images.map((image, index) => (
              <img
                key={index}
                src={image}
                alt={`${furnitureItem.title} ${index + 1}`}
                className="w-full h-48 object-cover rounded-lg"
              />
            ))}
          </div>
        </div>
      )}

      {/* Basic Info */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">기본 정보</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">상품명</label>
            {editing ? (
              <input
                type="text"
                value={formData.title || ''}
                onChange={(e) => handleInputChange('title', e.target.value)}
                className="input-field"
              />
            ) : (
              <p className="text-gray-900">{furnitureItem.title}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">상품 설명</label>
            {editing ? (
              <textarea
                value={formData.description || ''}
                onChange={(e) => handleInputChange('description', e.target.value)}
                className="input-field h-24 resize-none"
              />
            ) : (
              <p className="text-gray-900 whitespace-pre-wrap">{furnitureItem.description}</p>
            )}
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">가격</label>
              {editing ? (
                <input
                  type="number"
                  value={formData.price || ''}
                  onChange={(e) => handleInputChange('price', parseInt(e.target.value))}
                  className="input-field"
                />
              ) : (
                <p className="text-gray-900">{furnitureItem.price.toLocaleString()}원</p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">상품 상태</label>
              {editing ? (
                <select
                  value={formData.condition || ''}
                  onChange={(e) => handleInputChange('condition', e.target.value)}
                  className="select-field"
                >
                  {Object.entries(conditionLabels).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
              ) : (
                <p className="text-gray-900">{conditionLabels[furnitureItem.condition]}</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Contact Info */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">연락처 정보</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">판매자 연락처</label>
            {editing ? (
              <input
                type="tel"
                value={formData.seller_phone || ''}
                onChange={(e) => handleInputChange('seller_phone', e.target.value)}
                className="input-field"
              />
            ) : (
              <div className="flex items-center">
                <Phone className="w-4 h-4 text-gray-400 mr-2" />
                <a
                  href={`tel:${furnitureItem.seller_phone}`}
                  className="text-primary-600 hover:text-primary-700"
                >
                  {furnitureItem.seller_phone}
                </a>
              </div>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">지역</label>
            {editing ? (
              <input
                type="text"
                value={formData.location || ''}
                onChange={(e) => handleInputChange('location', e.target.value)}
                className="input-field"
              />
            ) : (
              <div className="flex items-center">
                <MapPin className="w-4 h-4 text-gray-400 mr-2" />
                <span className="text-gray-900">{getLocationLabel(furnitureItem.location)}</span>
              </div>
            )}
          </div>
          {furnitureItem.chat_link && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">채팅 링크</label>
              {editing ? (
                <input
                  type="url"
                  value={formData.chat_link || ''}
                  onChange={(e) => handleInputChange('chat_link', e.target.value)}
                  className="input-field"
                />
              ) : (
                <a
                  href={furnitureItem.chat_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:text-primary-700 break-all"
                >
                  {furnitureItem.chat_link}
                </a>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Status and Dates */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">상태 및 날짜</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">판매 상태</label>
            {editing ? (
              <select
                value={formData.is_sold ? 'true' : 'false'}
                onChange={(e) => handleInputChange('is_sold', e.target.value === 'true')}
                className="select-field"
              >
                <option value="false">판매중</option>
                <option value="true">판매완료</option>
              </select>
            ) : (
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                furnitureItem.is_sold ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
              }`}>
                {furnitureItem.is_sold ? '판매완료' : '판매중'}
              </span>
            )}
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">등록일</label>
              <div className="flex items-center">
                <Calendar className="w-4 h-4 text-gray-400 mr-2" />
                <span className="text-gray-900">
                  {format(new Date(furnitureItem.created_at), 'yyyy.MM.dd HH:mm', { locale: ko })}
                </span>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">수정일</label>
              <div className="flex items-center">
                <Calendar className="w-4 h-4 text-gray-400 mr-2" />
                <span className="text-gray-900">
                  {format(new Date(furnitureItem.updated_at), 'yyyy.MM.dd HH:mm', { locale: ko })}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default FurnitureDetail
