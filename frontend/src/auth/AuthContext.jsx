import React, { createContext, useContext, useState, useCallback } from 'react'
import { authApi } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem('truthlens_user')
    return raw ? JSON.parse(raw) : null
  })
  const [token, setToken] = useState(() => localStorage.getItem('truthlens_token'))

  const persist = (accessToken, userObj) => {
    localStorage.setItem('truthlens_token', accessToken)
    localStorage.setItem('truthlens_user', JSON.stringify(userObj))
    setToken(accessToken)
    setUser(userObj)
  }

  const login = useCallback(async (email, password) => {
    const { data } = await authApi.login(email, password)
    persist(data.access_token, data.user)
    return data
  }, [])

  const register = useCallback(async (name, email, password) => {
    const { data } = await authApi.register(name, email, password)
    persist(data.access_token, data.user)
    return data
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('truthlens_token')
    localStorage.removeItem('truthlens_user')
    setToken(null)
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
