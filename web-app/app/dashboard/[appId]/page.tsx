'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { TrendingUp, TrendingDown, Search, Target, Users, ChevronLeft, Loader2, Plus, Bell, Send, Settings, BarChart3, Calendar } from 'lucide-react'
import Link from 'next/link'
import AddKeywordsModal from '@/components/AddKeywordsModal'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface PageProps {
  params: Promise<{
    appId: string
  }>
}

export default function AppDetailPage({ params: paramsPromise }: PageProps) {
  const router = useRouter()
  const supabase = createClient()

  const [appId, setAppId] = useState<string | null>(null)
  const [user, setUser] = useState<any>(null)
  const [app, setApp] = useState<any>(null)
  const [keywords, setKeywords] = useState<any[]>([])
  const [profile, setProfile] = useState<any>(null)
  const [alerts, setAlerts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddKeywordsModal, setShowAddKeywordsModal] = useState(false)
  const [activeTab, setActiveTab] = useState('keywords')
  const [timeRange, setTimeRange] = useState<'1d' | '7d' | '30d' | '90d'>('7d')
  const [topKeywords, setTopKeywords] = useState<any[]>([])
  const [chartData, setChartData] = useState<any[]>([])
  const [stats, setStats] = useState({
    totalKeywords: 0,
    avgRank: 0,
    topRankings: 0,
    avgVolume: 0,
    avgDifficulty: 0,
  })

  useEffect(() => {
    paramsPromise.then((p) => {
      setAppId(p.appId)
    })
  }, [paramsPromise])

  useEffect(() => {
    if (appId) {
      loadData()
    }
  }, [appId])

  const loadData = async () => {
    if (!appId) return

    setLoading(true)

    const {
      data: { user: currentUser },
    } = await supabase.auth.getUser()

    if (!currentUser) {
      router.push('/login')
      return
    }

    setUser(currentUser)

    const { data: userProfile } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', currentUser.id)
      .single()

    setProfile(userProfile)

    const { data: appData, error: appError } = await supabase
      .from('apps')
      .select('*')
      .eq('id', appId)
      .eq('user_id', currentUser.id)
      .single()

    if (appError || !appData) {
      router.push('/dashboard')
      return
    }

    setApp(appData)

    const { data: alertsData } = await supabase
      .from('alerts')
      .select('*')
      .eq('app_id', appId)
      .order('created_at', { ascending: false })

    setAlerts(alertsData || [])

    const { data: keywordsData } = await supabase
      .from('keywords')
      .select(`
        *,
        rankings (
          rank,
          tracked_at
        )
      `)
      .eq('app_id', appId)
      .order('keyword', { ascending: true })

    setKeywords(keywordsData || [])

    if (keywordsData && keywordsData.length > 0) {
      const newStats = {
        totalKeywords: keywordsData.length,
        avgRank: 0,
        topRankings: 0,
        avgVolume: 0,
        avgDifficulty: 0,
      }

      const ranksWithData = keywordsData.filter((k) => k.rankings && k.rankings.length > 0)

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

      const volumeData = keywordsData.filter((k) => k.volume).map((k) => k.volume)
      const difficultyData = keywordsData.filter((k) => k.difficulty).map((k) => k.difficulty)

      if (volumeData.length > 0) {
        newStats.avgVolume = Math.round(
          volumeData.reduce((a, b) => a + b, 0) / volumeData.length
        )
      }

      if (difficultyData.length > 0) {
        newStats.avgDifficulty = Math.round(
          difficultyData.reduce((a, b) => a + b, 0) / difficultyData.length
        )
      }

      setStats(newStats)
    }

    // Cargar datos del timeline
    if (keywordsData && keywordsData.length > 0) {
      await loadTopKeywordsData(keywordsData)
    }

    setLoading(false)
  }

  const loadTopKeywordsData = async (allKeywords: any[]) => {
    console.log('🔍 Total keywords recibidas:', allKeywords.length)
    console.log('🔍 Keywords con rankings:', allKeywords.filter(k => k.rankings?.length > 0).length)
    
    // Encontrar las top 20 mejores keywords (mejor ranking)
    const keywordsWithRank = allKeywords
      .filter((k) => k.rankings && k.rankings.length > 0)
      .map((k) => {
        const sorted = k.rankings.sort(
          (a: any, b: any) =>
            new Date(b.tracked_at).getTime() - new Date(a.tracked_at).getTime()
        )
        return {
          ...k,
          currentRank: sorted[0]?.rank || 999,
        }
      })
      .sort((a, b) => a.currentRank - b.currentRank)
      .slice(0, 20) // Las 20 mejores keywords

    console.log('📈 Top 20 keywords:', keywordsWithRank.map(k => `${k.keyword} (#${k.currentRank})`).slice(0, 5))
    setTopKeywords(keywordsWithRank)

    // Obtener datos históricos para el gráfico
    if (keywordsWithRank.length > 0) {
      const daysMap: Record<string, number> = {
        '1d': 1,
        '7d': 7,
        '30d': 30,
        '90d': 90,
      }
      const days = daysMap[timeRange]
      const startDate = new Date()
      startDate.setDate(startDate.getDate() - days)

      const keywordIds = keywordsWithRank.map((k) => k.id)

      const { data: historicalRankings } = await supabase
        .from('rankings')
        .select(`
          *,
          keywords!inner (
            id,
            keyword
          )
        `)
        .in('keyword_id', keywordIds)
        .gte('tracked_at', startDate.toISOString())
        .order('tracked_at', { ascending: true })

      // Agrupar datos por fecha para el gráfico
      const dataByDate: Record<string, any> = {}

      historicalRankings?.forEach((ranking: any) => {
        const date = new Date(ranking.tracked_at).toLocaleDateString('es-ES', {
          month: 'short',
          day: 'numeric',
        })
        const keyword = ranking.keywords?.keyword

        if (!dataByDate[date]) {
          dataByDate[date] = { date }
        }

        // Invertir el rank para que hacia arriba sea mejor (rank 1 = 100 en el gráfico)
        // Solo mostrar keywords en top 100
        if (ranking.rank <= 100) {
          dataByDate[date][keyword] = 101 - ranking.rank
        }
      })

      setChartData(Object.values(dataByDate))
      console.log('📊 ChartData puntos:', Object.values(dataByDate).length)
      console.log('📊 Primera entrada:', Object.values(dataByDate)[0])
    }
  }

  useEffect(() => {
    if (keywords.length > 0) {
      loadTopKeywordsData(keywords)
    }
  }, [timeRange])

  const handleKeywordsAdded = () => {
    loadData()
  }

  const handleCreateAlert = async (alertType: string) => {
    try {
      const { error } = await supabase.from('alerts').insert({
        user_id: user.id,
        app_id: app.id,
        alert_type: alertType,
        telegram_enabled: true,
        email_enabled: false,
        threshold: alertType.includes('rank') ? 5 : null,
      })

      if (error) throw error
      await loadData()
      alert('✅ Alerta creada correctamente')
    } catch (error: any) {
      alert(`Error: ${error.message}`)
    }
  }

  const handleToggleAlert = async (alertId: string, field: string, currentValue: boolean) => {
    try {
      const { error } = await supabase
        .from('alerts')
        .update({ [field]: !currentValue })
        .eq('id', alertId)

      if (error) throw error
      await loadData()
    } catch (error: any) {
      alert(`Error: ${error.message}`)
    }
  }

  const handleDeleteAlert = async (alertId: string) => {
    if (!confirm('¿Eliminar esta alerta?')) return

    try {
      const { error } = await supabase.from('alerts').delete().eq('id', alertId)

      if (error) throw error
      await loadData()
    } catch (error: any) {
      alert(`Error: ${error.message}`)
    }
  }

  const getAlertTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      rank_drop: '📉 Caída de ranking',
      rank_gain: '📈 Subida de ranking',
      new_top10: '🏆 Entrada al Top 10',
      lost_top10: '⚠️ Salida del Top 10',
      new_top50: '⭐ Entrada al Top 50',
      lost_top50: '📊 Salida del Top 50',
      daily_summary: '📅 Resumen diario',
      weekly_report: '📊 Reporte semanal',
    }
    return labels[type] || type
  }

  if (loading || !app) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
      </div>
    )
  }

  return (
    <>
      {showAddKeywordsModal && profile && (
        <AddKeywordsModal
          isOpen={showAddKeywordsModal}
          onClose={() => setShowAddKeywordsModal(false)}
          onSuccess={handleKeywordsAdded}
          appId={app.id}
          appName={app.name}
          maxKeywords={profile.max_keywords_per_app || 50}
          currentKeywordsCount={keywords.length}
        />
      )}

      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
        <nav className="bg-white shadow-sm border-b border-slate-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <Link
                href="/dashboard"
                className="flex items-center gap-2 text-slate-600 hover:text-slate-900"
              >
                <ChevronLeft className="w-5 h-5" />
                Volver al Dashboard
              </Link>
              <Link href="/" className="flex items-center gap-2">
                <TrendingUp className="w-8 h-8 text-blue-600" />
                <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  ASO RankGuard
                </span>
              </Link>
              <div className="text-sm text-slate-600">{user?.email}</div>
            </div>
          </div>
        </nav>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-8">
            <div className="flex items-start justify-between">
              <div>
                <h1 className="text-3xl font-bold text-slate-900 mb-2">{app.name}</h1>
                <div className="flex items-center gap-4 text-sm text-slate-600">
                  <span className="flex items-center gap-1">
                    <span className="font-semibold">Bundle ID:</span> {app.bundle_id}
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="font-semibold">Plataforma:</span> {app.platform.toUpperCase()}
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="font-semibold">País:</span> {app.country.toUpperCase()}
                  </span>
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setShowAddKeywordsModal(true)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  Añadir Keywords
                </button>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-600 text-sm font-medium">Keywords</span>
                <Search className="w-5 h-5 text-blue-600" />
              </div>
              <div className="text-3xl font-bold text-slate-900">{stats.totalKeywords}</div>
              <div className="text-xs text-slate-500 mt-1">keywords activas</div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-600 text-sm font-medium">Ranking Promedio</span>
                <Target className="w-5 h-5 text-orange-600" />
              </div>
              <div className="text-3xl font-bold text-slate-900">
                {stats.avgRank > 0 ? `#${stats.avgRank}` : '-'}
              </div>
              <div className="text-xs text-slate-500 mt-1">posición media</div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-600 text-sm font-medium">Top 10</span>
                <TrendingUp className="w-5 h-5 text-green-600" />
              </div>
              <div className="text-3xl font-bold text-slate-900">{stats.topRankings}</div>
              <div className="text-xs text-slate-500 mt-1">en top 10</div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-600 text-sm font-medium">Total Trackings</span>
                <BarChart3 className="w-5 h-5 text-purple-600" />
              </div>
              <div className="text-3xl font-bold text-slate-900">
                {keywords.reduce((total, kw) => total + (kw.rankings?.length || 0), 0)}
              </div>
              <div className="text-xs text-slate-500 mt-1">datos históricos</div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-600 text-sm font-medium">Última Actualización</span>
                <Calendar className="w-5 h-5 text-indigo-600" />
              </div>
              <div className="text-xl font-bold text-slate-900">
                {keywords.length > 0 && keywords[0].rankings?.length > 0
                  ? new Date(keywords[0].rankings[0].tracked_at).toLocaleDateString('es-ES', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
                  : '-'}
              </div>
              <div className="text-xs text-slate-500 mt-1">último tracking</div>
            </div>
          </div>

          {/* Top 10 Keywords Timeline */}          {console.log('🎯 Renderizando timeline - topKeywords:', topKeywords.length, 'chartData:', chartData.length)}          {topKeywords.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-8">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                    <BarChart3 className="w-6 h-6 text-blue-600" />
                    Top 20 Keywords - Evolución de Rankings
                  </h2>
                  <p className="text-sm text-slate-600 mt-1">
                    Seguimiento histórico de tus 20 mejores keywords · 
                    <span className="ml-1 font-semibold text-slate-700">
                      Cambios comparados con {
                        timeRange === '1d' ? 'hace 1 día' :
                        timeRange === '7d' ? 'hace 7 días' :
                        timeRange === '30d' ? 'hace 30 días' :
                        'hace 90 días'
                      }
                    </span>
                  </p>
                </div>
                <div className="flex gap-2">
                  {(['1d', '7d', '30d', '90d'] as const).map((range) => (
                    <button
                      key={range}
                      onClick={() => setTimeRange(range)}
                      className={`px-4 py-2 rounded-lg text-sm font-semibold transition ${
                        timeRange === range
                          ? 'bg-blue-600 text-white'
                          : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                      }`}
                    >
                      {range === '1d' && '1 día'}
                      {range === '7d' && '7 días'}
                      {range === '30d' && '30 días'}
                      {range === '90d' && '90 días'}
                    </button>
                  ))}
                </div>
              </div>

              {chartData.length > 0 ? (
                <>
                  <div className="mb-4 bg-gradient-to-br from-slate-50 to-blue-50 rounded-xl p-6">
                    <ResponsiveContainer width="100%" height={400}>
                      <LineChart data={chartData}>
                        <defs>
                          {topKeywords.slice(0, 10).map((kw, index) => {
                            const gradientColors = [
                              { start: '#60a5fa', end: '#3b82f6' },
                              { start: '#a78bfa', end: '#8b5cf6' },
                              { start: '#f0abfc', end: '#ec4899' },
                              { start: '#fbbf24', end: '#f59e0b' },
                              { start: '#34d399', end: '#10b981' },
                              { start: '#22d3ee', end: '#06b6d4' },
                              { start: '#818cf8', end: '#6366f1' },
                              { start: '#f87171', end: '#ef4444' },
                              { start: '#facc15', end: '#eab308' },
                              { start: '#2dd4bf', end: '#14b8a6' },
                            ]
                            return (
                              <linearGradient key={`gradient-${index}`} id={`colorGradient${index}`} x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor={gradientColors[index].start} stopOpacity={0.8}/>
                                <stop offset="95%" stopColor={gradientColors[index].end} stopOpacity={0.8}/>
                              </linearGradient>
                            )
                          })}
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" strokeOpacity={0.5} />
                        <XAxis
                          dataKey="date"
                          stroke="#64748b"
                          style={{ fontSize: '13px', fontWeight: '500' }}
                          tickLine={false}
                        />
                        <YAxis
                          stroke="#64748b"
                          style={{ fontSize: '13px', fontWeight: '500' }}
                          domain={[0, 100]}
                          ticks={[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]}
                          tickFormatter={(value) => {
                            const rank = 101 - value
                            return rank === 101 ? '' : `#${rank}`
                          }}
                          tickLine={false}
                        />
                        <Tooltip
                          content={({ active, payload, label }) => {
                            if (!active || !payload || payload.length === 0) return null
                            
                            return (
                              <div className="bg-white/95 backdrop-blur-sm border-2 border-slate-200 rounded-xl shadow-2xl p-4" style={{ minWidth: '240px', maxHeight: '320px', overflowY: 'auto' }}>
                                <div className="flex items-center gap-2 mb-3 pb-3 border-b-2 border-slate-200">
                                  <Calendar className="w-4 h-4 text-blue-600" />
                                  <p className="text-sm font-bold text-slate-900">{label}</p>
                                </div>
                                <div className="space-y-2.5">
                                  {payload.filter((p: any) => p.value !== undefined).map((entry: any, index: number) => {
                                    const keywordName = entry.name
                                    const rank = 101 - (entry.value as number)
                                    const keyword = topKeywords.find(k => k.keyword === keywordName)
                                    const volume = keyword?.volume || 0
                                    
                                    // Obtener el color sólido basado en el índice de la keyword
                                    const solidColors = [
                                      '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981',
                                      '#06b6d4', '#6366f1', '#ef4444', '#eab308', '#14b8a6',
                                    ]
                                    const keywordIndex = topKeywords.findIndex(k => k.keyword === keywordName)
                                    const solidColor = solidColors[keywordIndex] || entry.stroke || '#3b82f6'
                                    
                                    return (
                                      <div key={index} className="pb-2.5 border-b border-slate-100 last:border-0 hover:bg-slate-50 rounded-lg p-2 transition-colors">
                                        <div className="flex items-center gap-2 mb-1.5">
                                          <div className="w-3 h-3 rounded-full shadow-sm" style={{ backgroundColor: solidColor }}></div>
                                          <p className="font-extrabold text-slate-900 text-sm flex-1 truncate" title={keywordName}>
                                            {keywordName}
                                          </p>
                                        </div>
                                        <div className="flex items-center justify-between ml-5">
                                          <span className="text-xs text-slate-900 font-bold">Posición:</span>
                                          <span className="text-base font-extrabold text-slate-900 px-2 py-0.5 rounded-md bg-slate-100">#{rank}</span>
                                        </div>
                                        {volume > 0 && (
                                          <div className="flex items-center justify-between ml-5 mt-1">
                                            <span className="text-xs text-slate-900 font-bold">Volumen:</span>
                                            <span className="text-xs font-extrabold text-slate-900">{volume.toLocaleString()}/mes</span>
                                          </div>
                                        )}
                                      </div>
                                    )
                                  })}
                                </div>
                              </div>
                            )
                          }}
                        />
                        <Legend 
                          wrapperStyle={{ 
                            paddingTop: '20px',
                            fontWeight: 'bold',
                            color: '#0f172a'
                          }}
                          iconType="circle"
                        />
                        {topKeywords.slice(0, 10).map((kw, index) => {
                          const colors = [
                            '#3b82f6',
                            '#8b5cf6',
                            '#ec4899',
                            '#f59e0b',
                            '#10b981',
                            '#06b6d4',
                            '#6366f1',
                            '#ef4444',
                            '#eab308',
                            '#14b8a6',
                          ]
                          return (
                            <Line
                              key={kw.id}
                              type="natural"
                              dataKey={kw.keyword}
                              stroke={`url(#colorGradient${index})`}
                              strokeWidth={3}
                              dot={{ 
                                r: 4, 
                                strokeWidth: 2, 
                                fill: colors[index],
                                stroke: '#fff'
                              }}
                              activeDot={{ 
                                r: 7, 
                                strokeWidth: 3,
                                fill: colors[index],
                                stroke: '#fff',
                                filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))'
                              }}
                              animationDuration={800}
                              animationEasing="ease-in-out"
                            />
                          )
                        })}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Keywords Legend */}
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-3 pt-4 border-t border-slate-200">
                    {topKeywords.map((kw, index) => {
                      const colors = [
                        'from-blue-50 to-blue-100 border-blue-200 shadow-blue-100',
                        'from-purple-50 to-purple-100 border-purple-200 shadow-purple-100',
                        'from-pink-50 to-pink-100 border-pink-200 shadow-pink-100',
                        'from-orange-50 to-orange-100 border-orange-200 shadow-orange-100',
                        'from-green-50 to-green-100 border-green-200 shadow-green-100',
                        'from-cyan-50 to-cyan-100 border-cyan-200 shadow-cyan-100',
                        'from-indigo-50 to-indigo-100 border-indigo-200 shadow-indigo-100',
                        'from-red-50 to-red-100 border-red-200 shadow-red-100',
                        'from-yellow-50 to-yellow-100 border-yellow-200 shadow-yellow-100',
                        'from-teal-50 to-teal-100 border-teal-200 shadow-teal-100',
                      ]

                      const keywordData = chartData
                        .filter((d) => d[kw.keyword])
                        .map((d) => 101 - d[kw.keyword])  // Convertir de vuelta a rank real

                      const change =
                        keywordData.length >= 2
                          ? keywordData[keywordData.length - 1] - keywordData[0]  // último - primero
                          : 0

                      return (
                        <div
                          key={kw.id}
                          className={`p-3 rounded-xl border-2 bg-gradient-to-br ${colors[index]} hover:shadow-lg transition-all duration-200 hover:scale-105 cursor-pointer`}
                        >
                          <div className="text-xs font-bold mb-1.5 truncate text-slate-900">
                            {kw.keyword}
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-xl font-extrabold text-slate-900">#{kw.currentRank}</span>
                            {change !== 0 && (
                              <span
                                className={`flex items-center gap-1 text-xs font-bold px-2 py-1 rounded-lg ${
                                  change > 0 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                                }`}
                              >
                                {change > 0 ? (
                                  <TrendingDown className="w-3.5 h-3.5" />
                                ) : (
                                  <TrendingDown className="w-3.5 h-3.5" />
                                )}
                                {Math.abs(change)}
                              </span>
                            )}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </>
              ) : (
                <div className="text-center py-12 text-slate-500">
                  <Calendar className="w-16 h-16 mx-auto mb-4 text-slate-300" />
                  <p>No hay suficientes datos históricos para este rango de tiempo</p>
                  <p className="text-sm mt-2">
                    Los datos se irán acumulando conforme trackees tus keywords
                  </p>
                </div>
              )}
            </div>
          )}

          <div className="bg-white rounded-t-xl shadow-sm border-x border-t border-slate-200">
            <div className="flex gap-1 px-6 pt-4">
              <button
                onClick={() => setActiveTab('keywords')}
                className={`px-4 py-2 font-semibold ${
                  activeTab === 'keywords'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Keywords & Rankings
              </button>
              <button
                onClick={() => setActiveTab('settings')}
                className={`px-4 py-2 font-semibold flex items-center gap-2 ${
                  activeTab === 'settings'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Settings className="w-4 h-4" />
                Alertas & Telegram
              </button>
              <button className="px-4 py-2 font-semibold text-slate-600 hover:text-slate-900">
                Histórico
              </button>
              <button className="px-4 py-2 font-semibold text-slate-600 hover:text-slate-900">
                Análisis
              </button>
            </div>
          </div>

          <div className="bg-white rounded-b-xl shadow-sm border-x border-b border-slate-200 p-6">
            {activeTab === 'keywords' && keywords && keywords.length > 0 && (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-200">
                      <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Keyword</th>
                      <th className="text-center py-3 px-4 text-sm font-semibold text-slate-700">Ranking Actual</th>
                      <th className="text-center py-3 px-4 text-sm font-semibold text-slate-700">Volumen</th>
                      <th className="text-center py-3 px-4 text-sm font-semibold text-slate-700">Dificultad</th>
                      <th className="text-center py-3 px-4 text-sm font-semibold text-slate-700">Cambio</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Última Actualización</th>
                      <th className="text-center py-3 px-4 text-sm font-semibold text-slate-700">Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {keywords.map((keyword: any) => {
                      const latestRanking = keyword.rankings?.sort(
                        (a: any, b: any) =>
                          new Date(b.tracked_at).getTime() - new Date(a.tracked_at).getTime()
                      )[0]

                      const currentRank = latestRanking?.rank
                      const change = 0

                      return (
                        <tr key={keyword.id} className="border-b border-slate-100 hover:bg-slate-50">
                          <td className="py-3 px-4 font-medium text-slate-900">{keyword.keyword}</td>
                          <td className="py-3 px-4 text-center">
                            {currentRank ? (
                              <span
                                className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${
                                  currentRank <= 10
                                    ? 'bg-green-100 text-green-800'
                                    : currentRank <= 50
                                    ? 'bg-yellow-100 text-yellow-800'
                                    : 'bg-slate-100 text-slate-800'
                                }`}
                              >
                                #{currentRank}
                              </span>
                            ) : (
                              <span className="text-slate-400">-</span>
                            )}
                          </td>
                          <td className="py-3 px-4 text-center text-slate-700">
                            {keyword.volume ? keyword.volume.toLocaleString() : '-'}
                          </td>
                          <td className="py-3 px-4 text-center">
                            {keyword.difficulty ? (
                              <span
                                className={`inline-flex items-center px-2 py-1 rounded text-xs font-semibold ${
                                  keyword.difficulty <= 40
                                    ? 'bg-green-100 text-green-800'
                                    : keyword.difficulty <= 70
                                    ? 'bg-yellow-100 text-yellow-800'
                                    : 'bg-red-100 text-red-800'
                                }`}
                              >
                                {keyword.difficulty}
                              </span>
                            ) : (
                              <span className="text-slate-400">-</span>
                            )}
                          </td>
                          <td className="py-3 px-4 text-center">
                            {change !== 0 ? (
                              <span className={`inline-flex items-center gap-1 ${change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {change > 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                                {Math.abs(change)}
                              </span>
                            ) : (
                              <span className="text-slate-400">-</span>
                            )}
                          </td>
                          <td className="py-3 px-4 text-slate-600 text-sm">
                            {latestRanking ? new Date(latestRanking.tracked_at).toLocaleDateString('es-ES') : 'Sin datos'}
                          </td>
                          <td className="py-3 px-4 text-center">
                            <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">Ver Histórico</button>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}

            {activeTab === 'keywords' && (!keywords || keywords.length === 0) && (
              <div className="text-center py-12">
                <Search className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-slate-900 mb-2">No hay keywords todavía</h3>
                <p className="text-slate-600 mb-6">Añade keywords para empezar a trackear tus rankings</p>
                <button
                  onClick={() => setShowAddKeywordsModal(true)}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 transition flex items-center gap-2 mx-auto"
                >
                  <Plus className="w-4 h-4" />
                  Añadir Primera Keyword
                </button>
              </div>
            )}

            {activeTab === 'settings' && (
              <div className="space-y-8">
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-200">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
                        <Send className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-slate-900 mb-1">Telegram Bot</h3>
                        {profile?.telegram_user_id ? (
                          <div>
                            <p className="text-sm text-green-700 font-semibold mb-1">✅ Vinculado</p>
                            <p className="text-xs text-slate-600">ID: {profile.telegram_user_id}</p>
                          </div>
                        ) : (
                          <div>
                            <p className="text-sm text-orange-700 font-semibold mb-1">⚠️ No vinculado</p>
                            <p className="text-xs text-slate-600 mb-3">Vincula tu cuenta de Telegram para recibir alertas</p>
                            <a
                              href="https://t.me/YOUR_BOT_USERNAME"
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 transition"
                            >
                              <Send className="w-4 h-4" />
                              Abrir Bot de Telegram
                            </a>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-slate-900">Alertas Configuradas</h3>
                    <div className="relative group">
                      <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center gap-2">
                        <Plus className="w-4 h-4" />
                        Nueva Alerta
                      </button>
                      <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-slate-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
                        <div className="p-2">
                          <button
                            onClick={() => handleCreateAlert('rank_drop')}
                            className="w-full text-left px-4 py-2 rounded hover:bg-slate-100 text-sm"
                          >
                            📉 Caída de ranking
                          </button>
                          <button
                            onClick={() => handleCreateAlert('rank_gain')}
                            className="w-full text-left px-4 py-2 rounded hover:bg-slate-100 text-sm"
                          >
                            📈 Subida de ranking
                          </button>
                          <button
                            onClick={() => handleCreateAlert('new_top10')}
                            className="w-full text-left px-4 py-2 rounded hover:bg-slate-100 text-sm"
                          >
                            🏆 Entrada al Top 10
                          </button>
                          <button
                            onClick={() => handleCreateAlert('daily_summary')}
                            className="w-full text-left px-4 py-2 rounded hover:bg-slate-100 text-sm"
                          >
                            📅 Resumen diario
                          </button>
                          <button
                            onClick={() => handleCreateAlert('weekly_report')}
                            className="w-full text-left px-4 py-2 rounded hover:bg-slate-100 text-sm"
                          >
                            📊 Reporte semanal
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  {alerts && alerts.length > 0 ? (
                    <div className="space-y-3">
                      {alerts.map((alert) => (
                        <div
                          key={alert.id}
                          className="flex items-center justify-between p-4 bg-slate-50 rounded-lg border border-slate-200 hover:border-blue-300 transition"
                        >
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <span className="text-sm font-semibold text-slate-900">
                                {getAlertTypeLabel(alert.alert_type)}
                              </span>
                              {!alert.is_active && (
                                <span className="px-2 py-0.5 bg-slate-200 text-slate-600 text-xs rounded">Pausada</span>
                              )}
                            </div>
                            <div className="flex items-center gap-4 text-xs text-slate-600">
                              <label className="flex items-center gap-2 cursor-pointer">
                                <input
                                  type="checkbox"
                                  checked={alert.telegram_enabled}
                                  onChange={() =>
                                    handleToggleAlert(alert.id, 'telegram_enabled', alert.telegram_enabled)
                                  }
                                  className="rounded"
                                />
                                <Send className="w-3 h-3" />
                                Telegram
                              </label>
                              <label className="flex items-center gap-2 cursor-pointer">
                                <input
                                  type="checkbox"
                                  checked={alert.email_enabled}
                                  onChange={() =>
                                    handleToggleAlert(alert.id, 'email_enabled', alert.email_enabled)
                                  }
                                  className="rounded"
                                />
                                📧 Email
                              </label>
                              {alert.threshold && (
                                <span className="text-slate-500">Umbral: ±{alert.threshold} posiciones</span>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => handleToggleAlert(alert.id, 'is_active', alert.is_active)}
                              className={`px-3 py-1 rounded text-xs font-semibold transition ${
                                alert.is_active
                                  ? 'bg-green-100 text-green-700 hover:bg-green-200'
                                  : 'bg-slate-200 text-slate-600 hover:bg-slate-300'
                              }`}
                            >
                              {alert.is_active ? 'Activa' : 'Pausada'}
                            </button>
                            <button
                              onClick={() => handleDeleteAlert(alert.id)}
                              className="px-3 py-1 text-red-600 hover:bg-red-50 rounded text-xs font-semibold transition"
                            >
                              Eliminar
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12 bg-slate-50 rounded-lg border border-slate-200">
                      <Bell className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                      <h3 className="text-lg font-semibold text-slate-900 mb-2">No hay alertas configuradas</h3>
                      <p className="text-slate-600 text-sm">
                        Crea alertas para recibir notificaciones de cambios en tus rankings
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  )
}
