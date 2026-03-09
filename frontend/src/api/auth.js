import axios from "axios"

const API = "http://127.0.0.1:8000/api/auth"

export const login = (data) =>
  axios.post(`${API}/login/`, data, { withCredentials: true })

export const register = (data) =>
  axios.post(`${API}/register/`, data)

export const logout = () =>
  axios.post(`${API}/logout/`)

export const getUser = () =>
  axios.get(`${API}/me/`)