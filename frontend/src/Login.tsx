import { useState } from 'react';

interface LoginProps {
  onLoginSuccess: (token: string) => void;
  onNavigateToRegister?: () => void;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
}

export default function Login({ onLoginSuccess, onNavigateToRegister }: LoginProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault(); 
    setIsLoading(true);
    setError('');

    try {
      const formData = new URLSearchParams();
      formData.append('username', email); 
      formData.append('password', password);

      const response = await fetch('http://localhost:8000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('E-mail ou senha incorretos');
      }

      const data: TokenResponse = await response.json();

      onLoginSuccess(data.access_token);

    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-full items-center justify-center bg-gray-50">
      <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-xl">
        
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-bold text-slate-800">PaperBroker</h1>
          <p className="text-sm text-slate-500">Acesse sua carteira digital</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-700">E-mail</label>
            <input
              type="email"
              required
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="seu@email.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700">Senha</label>
            <input
              type="password"
              required
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </div>

          {error && (
            <div className="rounded-md bg-red-50 p-3 text-sm text-red-600">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full rounded-md bg-slate-800 py-2.5 text-white transition-colors hover:bg-slate-700 disabled:bg-slate-400"
          >
            {isLoading ? 'Autenticando...' : 'Entrar'}
          </button>

        <div className="mt-6 text-center text-sm text-slate-600">
          Ainda não tem conta?{' '}
          <button 
            type="button" 
            onClick={onNavigateToRegister}
            className="text-blue-600 font-semibold hover:underline bg-transparent border-none cursor-pointer p-0"
          >
            Abra sua conta aqui
          </button>
        </div>

        </form>

      </div>
    </div>
  );
}