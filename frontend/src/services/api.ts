import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000', // A URL do seu FastAPI
});

// Antes de qualquer chamada sair do navegador, este código "grampeia" o token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  
  if (token) {
    // Remove aspas se existirem e adiciona ao Header
    const cleanToken = token.replace(/"/g, '');
    config.headers.Authorization = `Bearer ${cleanToken}`;
  }
  
  return config;
});

export default api;