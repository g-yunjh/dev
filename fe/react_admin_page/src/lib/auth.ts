import adminAccounts from '../data/admin-accounts.json'

export interface AdminAccount {
  id: string
  password: string
  name: string
}

export interface LoginCredentials {
  id: string
  password: string
}

export const authenticateAdmin = (credentials: LoginCredentials): AdminAccount | null => {
  const admin = adminAccounts.admins.find(
    (admin) => admin.id === credentials.id && admin.password === credentials.password
  )
  return admin || null
}

export const isAuthenticated = (): boolean => {
  return localStorage.getItem('admin-authenticated') === 'true'
}

export const setAuthenticated = (admin: AdminAccount): void => {
  localStorage.setItem('admin-authenticated', 'true')
  localStorage.setItem('admin-info', JSON.stringify(admin))
}

export const logout = (): void => {
  localStorage.removeItem('admin-authenticated')
  localStorage.removeItem('admin-info')
}

export const getCurrentAdmin = (): AdminAccount | null => {
  const adminInfo = localStorage.getItem('admin-info')
  return adminInfo ? JSON.parse(adminInfo) : null
}
