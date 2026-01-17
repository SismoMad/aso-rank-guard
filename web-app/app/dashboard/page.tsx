'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { TrendingUp, Plus, Search, BarChart3, Globe, Loader2, Trash2 } from 'lucide-react'
import Link from 'next/link'
import AddAppModal from '@/components/AddAppModal'
import Onboarding from '@/components/Onboarding'

export default function DashboardPage() {
  const router = useRouter()
  const supabase = createClient()

  const [user, setUser] = useState<any>(null)
  const [apps, setApps] = useState<any[]>([])
  const [profile, setProfile] = useState<any>(null)
  const [stats, setStats] = useState({
    totalKeywords: 0,
    avgRank: 0,
    topRankings: 0,
    changes: 0,
  })
  const [loading, setLoading] = useState(true)
  const [showAddAppModal, setShowAddAppModal] = useState(false)
  const [showOnboarding, setShowOnboarding] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)

    // Verificar autenticación
    const {
      data: { user: currentUser },
    } = await supabase.auth.getUser()

    if (!currentUser) {
      router.push('/login')
      return
    }

    setUser(currentUser)

    // Obtener perfil
    const { data: userProfile } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', currentUser.id)
      .single()

    setProfile(userProfile)

    // Obtener apps
    const { data: userApps, error: appsError } = await supabase
      .from('apps')
      .select('*')
      .eq('user_id', currentUser.id)
      .order('created_at', { ascending: false })

    if (appsError) {
      console.error('Error cargando apps:', appsError)
    }

    setApps(userApps || [])

    // Mostrar onboarding si es nuevo usuario sin apps
    if (!userApps || userApps.length === 0) {
      const hasSeenOnboarding = localStorage.getItem('hasSeenOnboarding')
      if (!hasSeenOnboarding) {
        setShowOnboarding(true)
      }
    }

    // Calcular estadísticas
    if (userApps && userApps.length > 0) {
      const { data: allKeywords } = await supabase
        .from('keywords')
        .select(`
          *,
          rankings (
            rank,
            tracked_at
          )
        `)
        .in(
          'app_id',
          userApps.map((app) => app.id)
        )

      if (allKeywords && allKeywords.length > 0) {
        const newStats = {
          totalKeywords: allKeywords.length,
          avgRank: 0,
          topRankings: 0,
          changes: 0,
        }

        const ranksWithData = allKeywords.filter((k) => k.rankings && k.rankings.length > 0)
        if (ranksWithData.length > 0) {
          const latestRanks = ranksWithData
            .map((k) => {
              const sorted = k.rankings.sort(
                (a: any, b: any) =>
                  new Date(b.tracked_at).getTime() - new Date(a.tracked_at).getTime()
              )
              return sorted[0]?.rank
            })
            .filter((r) => r !== null && r !== undefined)

          if (latestRanks.length > 0) {
            newStats.avgRank = Math.round(
              latestRanks.reduce((a: number, b: number) => a + b, 0) / latestRanks.length
            )
            newStats.topRankings = latestRanks.filter((r: number) => r <= 10).length
          }
        }

        setStats(newStats)
      }
    }

    setLoading(false)
  }

  const handleOnboardingComplete = () => {
    localStorage.setItem('hasSeenOnboarding', 'true')
    setShowOnboarding(false)
    setShowAddAppModal(true)
  }

  const handleAppAdded = () => {
    loadData()
  }

  const handleDeleteApp = async (appId: string, appName: string) => {
    if (!confirm(`¿Estás seguro de eliminar "${appName}"? Se borrarán todos los keywords y rankings asociados.`)) {
      return
    }

    try {
      const { error } = await supabase
        .from('apps')
        .delete()
        .eq('id', appId)

      if (error) throw error

      // Recargar datos
      await loadData()
    } catch (error: any) {
      alert(`Error al eliminar app: ${error.message}`)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
      </div>
    )
  }

  return (
    <>
      {/* Onboarding */}
      {showOnboarding && <Onboarding onComplete={handleOnboardingComplete} />}

      {/* Add App Modal */}
      {showAddAppModal && user && profile && (
        <AddAppModal
          isOpen={showAddAppModal}
          onClose={() => setShowAddAppModal(false)}
          onSuccess={handleAppAdded}
          userId={user.id}
          maxApps={profile.max_apps || 1}
          currentAppsCount={apps.length}
        />
      )}

      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
        {/* Navbar */}
        <nav className="bg-white shadow-sm border-b border-slate-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <Link href="/" className="flex items-center gap-2">
                <TrendingUp className="w-8 h-8 text-blue-600" />
                <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  ASO RankGuard
                </span>
              </Link>
              <div className="flex items-center gap-4">
                <div className="text-sm">
                  <span className="text-slate-600">Plan:</span>{' '}
                  <span className="font-semibold text-blue-600 capitalize">
                    {profile?.tier || 'Free'}
                  </span>
                </div>
                <div className="text-sm text-slate-600">{user?.email}</div>
              </div>
            </div>
          </div>
        </nav>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-slate-900">Dashboard</h1>
              <p className="text-slate-600 mt-1">Monitorea tus apps y rankings en tiempo real</p>
            </div>
            <button
              onClick={() => setShowAddAppModal(true)}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:shadow-lg transition flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              Nueva App
            </button>
          </div>

        {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-600 text-sm font-medium">Total Apps</span>
                <BarChart3 className="w-5 h-5 text-blue-600" />
              </div>
              <div className="text-3xl font-bold text-slate-900">{apps?.length || 0}</div>
              <div className="text-xs text-slate-500 mt-1">
                de {profile?.max_apps || 1} permitidas
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-600 text-sm font-medium">Keywords</span>
                <Search className="w-5 h-5 text-green-600" />
              </div>
              <div className="text-3xl font-bold text-slate-900">{stats.totalKeywords}</div>
              <div className="text-xs text-slate-500 mt-1">
                de {profile?.max_keywords_per_app || 50} por app
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-600 text-sm font-medium">Ranking Promedio</span>
                <TrendingUp className="w-5 h-5 text-orange-600" />
              </div>
              <div className="text-3xl font-bold text-slate-900">
                {stats.avgRank > 0 ? `#${stats.avgRank}` : '-'}
              </div>
              <div className="text-xs text-green-600 mt-1 flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                {stats.changes >= 0 ? `+${stats.changes}` : stats.changes} hoy
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-600 text-sm font-medium">Top 10</span>
                <Globe className="w-5 h-5 text-purple-600" />
              </div>
              <div className="text-3xl font-bold text-slate-900">{stats.topRankings}</div>
              <div className="text-xs text-slate-500 mt-1">keywords en top 10</div>
            </div>
          </div>

          {/* Apps Grid */}
          {apps && apps.length > 0 ? (
            <div>
              <h2 className="text-xl font-bold text-slate-900 mb-6">Tus Apps</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {apps.map((app) => (
                  <div
                    key={app.id}
                    className="bg-white rounded-xl shadow-sm border border-slate-200 hover:shadow-lg hover:border-blue-300 transition-all group relative overflow-hidden"
                  >
                    {/* Delete Button - Mejorado */}
                    <button
                      onClick={(e) => {
                        e.preventDefault()
                        e.stopPropagation()
                        handleDeleteApp(app.id, app.name)
                      }}
                      className="absolute top-3 right-3 z-10 p-2.5 bg-white/90 backdrop-blur-sm border border-slate-200 text-slate-400 hover:text-white hover:bg-red-500 hover:border-red-500 rounded-lg shadow-sm transition-all duration-200 opacity-0 group-hover:opacity-100 hover:scale-110"
                      title="Eliminar app"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>

                    <Link href={`/dashboard/${app.id}`} className="block p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1 pr-12">
                          <h3 className="text-lg font-bold text-slate-900 group-hover:text-blue-600 transition">
                            {app.name}
                          </h3>
                          <p className="text-sm text-slate-600 mt-1 truncate">{app.bundle_id}</p>
                        </div>
                        <div
                          className={`w-12 h-12 rounded-lg flex items-center justify-center shrink-0 ${
                            app.is_active ? 'bg-green-100' : 'bg-slate-100'
                          }`}
                        >
                          <TrendingUp
                            className={`w-6 h-6 ${
                              app.is_active ? 'text-green-600' : 'text-slate-400'
                            }`}
                          />
                        </div>
                      </div>

                      <div className="flex items-center gap-2 flex-wrap text-xs text-slate-600 mb-4">
                        <span className="px-2.5 py-1 bg-slate-100 rounded-md font-medium">
                          {app.platform.toUpperCase()}
                        </span>
                        <span className="px-2.5 py-1 bg-slate-100 rounded-md font-medium">
                          {app.country.toUpperCase()}
                        </span>
                        {app.category && (
                          <span className="px-2.5 py-1 bg-blue-100 text-blue-700 rounded-md font-medium">
                            {app.category}
                          </span>
                        )}
                      </div>

                      <div className="flex items-center justify-between pt-4 border-t border-slate-100">
                        <span className="text-sm text-slate-600 font-medium">Ver Dashboard</span>
                        <TrendingUp className="w-4 h-4 text-blue-600 group-hover:translate-x-1 transition" />
                      </div>
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-12 text-center">
              <BarChart3 className="w-20 h-20 text-slate-300 mx-auto mb-4" />
              <h3 className="text-2xl font-bold text-slate-900 mb-2">No tienes apps todavía</h3>
              <p className="text-slate-600 mb-6 max-w-md mx-auto">
                Añade tu primera app para empezar a trackear rankings y optimizar tu ASO
              </p>
              <button
                onClick={() => setShowAddAppModal(true)}
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-3 rounded-lg font-semibold hover:shadow-lg transition inline-flex items-center gap-2"
              >
                <Plus className="w-5 h-5" />
                Añadir Mi Primera App
              </button>
            </div>
          )}
        </div>
      </div>
    </>
  )
}
