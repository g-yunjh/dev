import { supabase, type Contact, type ContactAttachment } from './supabase'
export type { Contact, ContactAttachment } from './supabase'

export interface PaginationParams {
  page: number
  limit: number
}

export interface ContactListResponse {
  data: Contact[]
  total: number
  page: number
  limit: number
  totalPages: number
}

export const contact = {
  async getAll(pagination: PaginationParams = { page: 1, limit: 20 }, status?: string): Promise<ContactListResponse> {
    let query = supabase
      .from('contacts')
      .select('*', { count: 'exact' })
      .order('created_at', { ascending: false })

    if (status) {
      query = query.eq('status', status)
    }

    // Apply pagination
    const from = (pagination.page - 1) * pagination.limit
    const to = from + pagination.limit - 1
    query = query.range(from, to)

    const { data, error, count } = await query

    if (error) {
      throw new Error(`Failed to fetch contacts: ${error.message}`)
    }

    const total = count || 0
    const totalPages = Math.ceil(total / pagination.limit)

    return {
      data: data || [],
      total,
      page: pagination.page,
      limit: pagination.limit,
      totalPages
    }
  },

  async getById(id: string): Promise<Contact | null> {
    const { data, error } = await supabase
      .from('contacts')
      .select('*')
      .eq('id', id)
      .single()

    if (error) {
      if (error.code === 'PGRST116') {
        return null
      }
      throw new Error(`Failed to fetch contact: ${error.message}`)
    }

    return data
  },

  async getAttachments(contactId: string): Promise<ContactAttachment[]> {
    const { data, error } = await supabase
      .from('contact_attachments')
      .select('*')
      .eq('contact_id', contactId)
      .order('created_at', { ascending: true })

    if (error) {
      throw new Error(`Failed to fetch attachments: ${error.message}`)
    }

    return data || []
  },

  async updateStatus(id: string, status: 'pending' | 'processing' | 'completed'): Promise<Contact> {
    const { data, error } = await supabase
      .from('contacts')
      .update({ status })
      .eq('id', id)
      .select()
      .single()

    if (error) {
      throw new Error(`Failed to update contact status: ${error.message}`)
    }

    return data
  }
}
