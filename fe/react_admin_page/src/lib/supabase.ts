import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Database types
export interface Furniture {
  id: string
  title: string
  description: string
  price: number
  seller_phone: string
  condition: 'new' | 'like_new' | 'good' | 'fair' | 'poor'
  location: string
  images: string[]
  is_sold: boolean
  password: string
  chat_link?: string
  created_at: string
  updated_at: string
}

export interface Contact {
  id: string
  name: string
  email: string
  subject: string
  message: string
  status: 'pending' | 'processing' | 'completed'
  created_at: string
}

export interface ContactAttachment {
  id: string
  contact_id: string
  file_name: string
  file_path: string
  file_size: number
  file_type: string
  created_at: string
}
