import { supabase, type Furniture } from './supabase'
export type { Furniture } from './supabase'

export interface FurnitureFilters {
  is_sold?: boolean
  location?: string
  condition?: string
  min_price?: number
  max_price?: number
  title?: string
}

export interface PaginationParams {
  page: number
  limit: number
}

export interface FurnitureListResponse {
  data: Furniture[]
  total: number
  page: number
  limit: number
  totalPages: number
}

export const furniture = {
  async getAll(filters: FurnitureFilters = {}, pagination: PaginationParams = { page: 1, limit: 20 }): Promise<FurnitureListResponse> {
    let query = supabase
      .from('furniture')
      .select('*', { count: 'exact' })
      .order('created_at', { ascending: false })

    // Apply filters
    if (filters.is_sold !== undefined) {
      query = query.eq('is_sold', filters.is_sold)
    }
    
    if (filters.location) {
      query = query.ilike('location', `%${filters.location}%`)
    }
    
    if (filters.condition) {
      query = query.eq('condition', filters.condition)
    }

    if (filters.title) {
      query = query.ilike('title', `%${filters.title}%`)
    }
    
    if (filters.min_price !== undefined) {
      query = query.gte('price', filters.min_price)
    }
    
    if (filters.max_price !== undefined) {
      query = query.lte('price', filters.max_price)
    }

    // Apply pagination
    const from = (pagination.page - 1) * pagination.limit
    const to = from + pagination.limit - 1
    query = query.range(from, to)

    const { data, error, count } = await query

    if (error) {
      throw new Error(`Failed to fetch furniture: ${error.message}`)
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

  async getById(id: string): Promise<Furniture | null> {
    const { data, error } = await supabase
      .from('furniture')
      .select('*')
      .eq('id', id)
      .single()

    if (error) {
      if (error.code === 'PGRST116') {
        return null
      }
      throw new Error(`Failed to fetch furniture: ${error.message}`)
    }

    return data
  },

  async update(id: string, updates: Partial<Omit<Furniture, 'id' | 'created_at' | 'updated_at'>>): Promise<Furniture> {
    const { data, error } = await supabase
      .from('furniture')
      .update({
        ...updates,
        updated_at: new Date().toISOString()
      })
      .eq('id', id)
      .select()
      .single()

    if (error) {
      throw new Error(`Failed to update furniture: ${error.message}`)
    }

    return data
  },

  async delete(id: string): Promise<void> {
    const { error } = await supabase
      .from('furniture')
      .delete()
      .eq('id', id)

    if (error) {
      throw new Error(`Failed to delete furniture: ${error.message}`)
    }
  }
}
