'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { TrendingUp, Mail, Lock, Loader2 } from 'lucide-react'
import { createClient } from '@/lib/supabase/client'

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()

  const supabase = createClient()

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isLogin) {
        // Login
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        })

        if (error) throw error

        console.log('Login exitoso:', data)
        // Redirigir al dashboard de Next.js con sus apps
        router.push('/dashboard')
      } else {
        // Signup
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            emailRedirectTo: `${window.location.origin}/dashboard`,
          },
        })

        if (error) throw error

        // Crear perfil de usuario
        if (data.user) {
          const { error: profileError } = await supabase
            .from('profiles')
            .insert({
              id: data.user.id,
              email: data.user.email,
              tier: 'free',
              max_apps: 1,
              max_keywords_per_app: 50,
            })

          if (profileError) {
            console.error('Error creando perfil:', profileError)
          }
        }

        alert('¡Cuenta creada! Revisa tu email para confirmar.')
        setIsLogin(true)
      }
    } catch (err: any) {
      console.error('Error de autenticación:', err)
      setError(err.message || 'Error al autenticarse')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center px-4">
      {/* Navbar */}
      <nav className="absolute top-0 left-0 right-0 bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/" className="flex items-center gap-2">
              <TrendingUp className="w-8 h-8 text-blue-600" />
              <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                ASO RankGuard
              </span>
            </Link>
          </div>
        </div>
      </nav>

      {/* Login/Signup Card */}
      <div className="w-full max-w-md">
        <div className="bg-white shadow-2xl rounded-2xl p-8">
          {/* Tabs */}
          <div className="flex gap-4 mb-8 border-b border-slate-200">
            <button
              onClick={() => setIsLogin(true)}
              className={`pb-3 px-4 font-semibold transition ${
                isLogin
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Iniciar Sesión
            </button>
            <button
              onClick={() => setIsLogin(false)}
              className={`pb-3 px-4 font-semibold transition ${
                !isLogin
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Registrarse
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleAuth} className="space-y-6">
            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-2">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full pl-11 pr-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                  placeholder="tu@email.com"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-700 mb-2">
                Contraseña
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={6}
                  className="w-full pl-11 pr-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                  placeholder="••••••••"
                />
              </div>
            </div>

            {/* Error */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg font-semibold hover:shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Procesando...
                </>
              ) : (
                <>{isLogin ? 'Iniciar Sesión' : 'Crear Cuenta'}</>
              )}
            </button>
          </form>

          {/* Footer */}
          <div className="mt-6 text-center text-sm text-slate-600">
            {isLogin ? (
              <p>
                ¿No tienes cuenta?{' '}
                <button
                  onClick={() => setIsLogin(false)}
                  className="text-blue-600 hover:underline font-semibold"
                >
                  Regístrate gratis
                </button>
              </p>
            ) : (
              <p>
                ¿Ya tienes cuenta?{' '}
                <button
                  onClick={() => setIsLogin(true)}
                  className="text-blue-600 hover:underline font-semibold"
                >
                  Inicia sesión
                </button>
              </p>
            )}
          </div>
        </div>

        {/* Extra Info */}
        <div className="mt-6 text-center text-sm text-slate-600">
          <p>🔒 Tus datos están protegidos con cifrado de extremo a extremo</p>
        </div>
      </div>
    </div>
  )
}
