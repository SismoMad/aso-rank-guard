'use client'

import { useState } from 'react'
import { createClient } from '@/lib/supabase/client'
import { X, Loader2, Search, Plus, Trash2 } from 'lucide-react'

interface AddKeywordsModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  appId: string
  appName: string
  maxKeywords: number
  currentKeywordsCount: number
}

interface KeywordInput {
  id: string
  keyword: string
  volume: number | null
  difficulty: number | null
}

export default function AddKeywordsModal({
  isOpen,
  onClose,
  onSuccess,
  appId,
  appName,
  maxKeywords,
  currentKeywordsCount,
}: AddKeywordsModalProps) {
  const [keywords, setKeywords] = useState<KeywordInput[]>([
    { id: '1', keyword: '', volume: null, difficulty: null },
  ])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [bulkText, setBulkText] = useState('')

  const supabase = createClient()

  const addKeywordRow = () => {
    setKeywords([
      ...keywords,
      { id: Date.now().toString(), keyword: '', volume: null, difficulty: null },
    ])
  }

  const removeKeywordRow = (id: string) => {
    setKeywords(keywords.filter((k) => k.id !== id))
  }

  const updateKeyword = (id: string, field: keyof KeywordInput, value: any) => {
    setKeywords(
      keywords.map((k) =>
        k.id === id ? { ...k, [field]: value } : k
      )
    )
  }

  const handleBulkImport = () => {
    const lines = bulkText.split('\n').filter((line) => line.trim())
    const newKeywords = lines.map((line) => ({
      id: Date.now().toString() + Math.random(),
      keyword: line.trim(),
      volume: null,
      difficulty: null,
    }))
    setKeywords([...keywords.filter((k) => k.keyword), ...newKeywords])
    setBulkText('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // Filtrar keywords vacías
      const validKeywords = keywords.filter((k) => k.keyword.trim())

      if (validKeywords.length === 0) {
        throw new Error('Debes añadir al menos una keyword')
      }

      // Verificar límite
      const totalKeywords = currentKeywordsCount + validKeywords.length
      if (totalKeywords > maxKeywords) {
        throw new Error(
          `Límite excedido. Puedes añadir ${maxKeywords - currentKeywordsCount} keywords más (${currentKeywordsCount}/${maxKeywords} usadas)`
        )
      }

      // Insertar keywords
      const { data, error } = await supabase
        .from('keywords')
        .insert(
          validKeywords.map((k) => ({
            app_id: appId,
            keyword: k.keyword.trim(),
            volume: k.volume,
            difficulty: k.difficulty,
            is_active: true,
          }))
        )
        .select()

      if (error) throw error

      // Resetear form
      setKeywords([{ id: '1', keyword: '', volume: null, difficulty: null }])

      onSuccess()
      onClose()
    } catch (err: any) {
      console.error('Error añadiendo keywords:', err)
      setError(err.message || 'Error al añadir keywords')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Search className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-slate-900">Añadir Keywords</h2>
              <p className="text-sm text-slate-600">
                App: {appName} | Keywords: {currentKeywordsCount} de {maxKeywords} permitidas
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
          {/* Bulk Import */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <label className="block text-sm font-semibold text-slate-700 mb-2">
              Importación Rápida (una keyword por línea)
            </label>
            <textarea
              value={bulkText}
              onChange={(e) => setBulkText(e.target.value)}
              rows={4}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition text-sm"
              placeholder={'biblia\nbiblia católica\nestudio bíblico\ndevocional diario'}
            />
            <button
              type="button"
              onClick={handleBulkImport}
              className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold hover:bg-blue-700 transition"
            >
              Importar Keywords
            </button>
          </div>

          {/* Individual Keywords */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <label className="block text-sm font-semibold text-slate-700">
                Keywords Individuales
              </label>
              <button
                type="button"
                onClick={addKeywordRow}
                className="flex items-center gap-1 px-3 py-1.5 text-sm bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition"
              >
                <Plus className="w-4 h-4" />
                Añadir fila
              </button>
            </div>

            <div className="space-y-2 max-h-96 overflow-y-auto">
              {keywords.map((kw, index) => (
                <div key={kw.id} className="flex gap-2 items-center">
                  <div className="flex-1">
                    <input
                      type="text"
                      value={kw.keyword}
                      onChange={(e) => updateKeyword(kw.id, 'keyword', e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition text-sm"
                      placeholder="Keyword..."
                    />
                  </div>
                  <div className="w-28">
                    <input
                      type="number"
                      value={kw.volume || ''}
                      onChange={(e) =>
                        updateKeyword(kw.id, 'volume', e.target.value ? parseInt(e.target.value) : null)
                      }
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition text-sm"
                      placeholder="Volumen"
                      min="0"
                    />
                  </div>
                  <div className="w-28">
                    <input
                      type="number"
                      value={kw.difficulty || ''}
                      onChange={(e) =>
                        updateKeyword(kw.id, 'difficulty', e.target.value ? parseInt(e.target.value) : null)
                      }
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition text-sm"
                      placeholder="Dificultad"
                      min="0"
                      max="100"
                    />
                  </div>
                  {keywords.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeKeywordRow(kw.id)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
            </div>

            <div className="mt-3 flex items-center gap-2 text-xs text-slate-600">
              <span>💡 <strong>Tip:</strong></span>
              <span>Volumen = búsquedas/mes | Dificultad = 0-100 (opcional)</span>
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          {/* Stats */}
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-600">Keywords a añadir:</span>
              <span className="font-bold text-slate-900">
                {keywords.filter((k) => k.keyword.trim()).length}
              </span>
            </div>
            <div className="flex items-center justify-between text-sm mt-2">
              <span className="text-slate-600">Total después de añadir:</span>
              <span className="font-bold text-slate-900">
                {currentKeywordsCount + keywords.filter((k) => k.keyword.trim()).length} / {maxKeywords}
              </span>
            </div>
          </div>

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
              disabled={loading || keywords.filter((k) => k.keyword.trim()).length === 0}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg font-semibold hover:shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Añadiendo...
                </>
              ) : (
                <>
                  <Plus className="w-5 h-5" />
                  Añadir Keywords
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
