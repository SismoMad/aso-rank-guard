'use client'

import { useState } from 'react'
import { createClient } from '@/lib/supabase/client'
import { X, Loader2, Smartphone } from 'lucide-react'

interface AddAppModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  userId: string
  maxApps: number
  currentAppsCount: number
}

export default function AddAppModal({
  isOpen,
  onClose,
  onSuccess,
  userId,
  maxApps,
  currentAppsCount,
}: AddAppModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    bundleId: '',
    platform: 'ios' as 'ios' | 'android',
    country: 'us',
    category: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const supabase = createClient()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // Verificar límite de apps
      if (currentAppsCount >= maxApps) {
        throw new Error(`Has alcanzado el límite de ${maxApps} apps. Actualiza tu plan para añadir más.`)
      }

      // Crear app
      const { data, error } = await supabase
        .from('apps')
        .insert({
          user_id: userId,
          name: formData.name,
          bundle_id: formData.bundleId,
          platform: formData.platform,
          country: formData.country,
          category: formData.category || null,
          is_active: true,
        })
        .select()
        .single()

      if (error) throw error

      // Resetear form
      setFormData({
        name: '',
        bundleId: '',
        platform: 'ios',
        country: 'us',
        category: '',
      })

      onSuccess()
      onClose()
    } catch (err: any) {
      console.error('Error creando app:', err)
      setError(err.message || 'Error al crear la app')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Smartphone className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-slate-900">Añadir Nueva App</h2>
              <p className="text-sm text-slate-600">
                Apps: {currentAppsCount} de {maxApps} permitidas
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-100 rounded-lg transition"
          >
            <X className="w-6 h-6 text-slate-400" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Nombre de la App */}
          <div>
            <label htmlFor="name" className="block text-sm font-semibold text-slate-700 mb-2">
              Nombre de la App *
            </label>
            <input
              id="name"
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              placeholder="Ej: BiblieNow"
            />
            <p className="mt-1 text-xs text-slate-500">
              El nombre que quieres que aparezca en tu dashboard
            </p>
          </div>

          {/* Bundle ID */}
          <div>
            <label htmlFor="bundleId" className="block text-sm font-semibold text-slate-700 mb-2">
              Bundle ID / Package Name *
            </label>
            <input
              id="bundleId"
              type="text"
              value={formData.bundleId}
              onChange={(e) => setFormData({ ...formData, bundleId: e.target.value })}
              required
              className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              placeholder="com.example.myapp"
            />
            <p className="mt-1 text-xs text-slate-500">
              iOS: Bundle Identifier | Android: Package Name
            </p>
          </div>

          {/* Plataforma y País */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="platform" className="block text-sm font-semibold text-slate-700 mb-2">
                Plataforma *
              </label>
              <select
                id="platform"
                value={formData.platform}
                onChange={(e) => setFormData({ ...formData, platform: e.target.value as 'ios' | 'android' })}
                className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              >
                <option value="ios">iOS (App Store)</option>
                <option value="android">Android (Google Play)</option>
              </select>
            </div>

            <div>
              <label htmlFor="country" className="block text-sm font-semibold text-slate-700 mb-2">
                País *
              </label>
              <select
                id="country"
                value={formData.country}
                onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              >
                <option value="us">🇺🇸 Estados Unidos</option>
                <option value="es">🇪🇸 España</option>
                <option value="mx">🇲🇽 México</option>
                <option value="ar">🇦🇷 Argentina</option>
                <option value="co">🇨🇴 Colombia</option>
                <option value="cl">🇨🇱 Chile</option>
                <option value="pe">🇵🇪 Perú</option>
                <option value="uk">🇬🇧 Reino Unido</option>
                <option value="de">🇩🇪 Alemania</option>
                <option value="fr">🇫🇷 Francia</option>
                <option value="br">🇧🇷 Brasil</option>
              </select>
            </div>
          </div>

          {/* Categoría */}
          <div>
            <label htmlFor="category" className="block text-sm font-semibold text-slate-700 mb-2">
              Categoría (opcional)
            </label>
            <input
              id="category"
              type="text"
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              placeholder="Ej: Productividad, Juegos, Salud..."
            />
          </div>

          {/* Error */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          {/* Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 border border-slate-300 text-slate-700 rounded-lg font-semibold hover:bg-slate-50 transition"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold hover:shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Creando...
                </>
              ) : (
                'Crear App'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
