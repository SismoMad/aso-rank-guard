'use client'

import { useState } from 'react'
import { Smartphone, Search, TrendingUp, CheckCircle, ArrowRight } from 'lucide-react'

interface OnboardingProps {
  onComplete: () => void
  userName?: string
}

export default function Onboarding({ onComplete, userName }: OnboardingProps) {
  const [step, setStep] = useState(1)

  const steps = [
    {
      id: 1,
      icon: Smartphone,
      title: '¡Bienvenido a ASO RankGuard!',
      description: 'Te ayudaremos a configurar tu primera app y empezar a trackear rankings en minutos.',
      color: 'blue',
    },
    {
      id: 2,
      icon: Search,
      title: 'Añade tus Keywords',
      description: 'Una vez creada tu app, añade las keywords que quieres monitorear. Puedes importar listas completas.',
      color: 'green',
    },
    {
      id: 3,
      icon: TrendingUp,
      title: 'Monitorea en Tiempo Real',
      description: 'Ve tus rankings actualizados, recibe alertas cuando cambien y analiza tendencias históricas.',
      color: 'purple',
    },
  ]

  const currentStep = steps.find((s) => s.id === step)!

  const handleNext = () => {
    if (step < steps.length) {
      setStep(step + 1)
    } else {
      onComplete()
    }
  }

  const handleSkip = () => {
    onComplete()
  }

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-3xl shadow-2xl max-w-2xl w-full p-8 md:p-12">
        {/* Progress Bar */}
        <div className="flex items-center gap-2 mb-8">
          {steps.map((s) => (
            <div
              key={s.id}
              className={`flex-1 h-2 rounded-full transition-all ${
                s.id <= step ? 'bg-blue-600' : 'bg-slate-200'
              }`}
            />
          ))}
        </div>

        {/* Icon */}
        <div
          className={`w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6 ${
            currentStep.color === 'blue'
              ? 'bg-blue-100'
              : currentStep.color === 'green'
              ? 'bg-green-100'
              : 'bg-purple-100'
          }`}
        >
          <currentStep.icon
            className={`w-10 h-10 ${
              currentStep.color === 'blue'
                ? 'text-blue-600'
                : currentStep.color === 'green'
                ? 'text-green-600'
                : 'text-purple-600'
            }`}
          />
        </div>

        {/* Content */}
        <div className="text-center mb-8">
          <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
            {currentStep.title}
          </h2>
          <p className="text-lg text-slate-600 max-w-lg mx-auto">
            {currentStep.description}
          </p>
        </div>

        {/* Step-specific content */}
        {step === 1 && (
          <div className="bg-slate-50 rounded-xl p-6 mb-8">
            <h3 className="font-semibold text-slate-900 mb-3">¿Qué puedes hacer con ASO RankGuard?</h3>
            <ul className="space-y-2 text-sm text-slate-700">
              <li className="flex items-start gap-2">
                <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                <span>Trackea rankings de keywords en App Store y Google Play</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                <span>Analiza competidores y descubre nuevas oportunidades</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                <span>Recibe alertas instantáneas en Telegram cuando cambien tus rankings</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                <span>Ve históricos completos y tendencias de tus keywords</span>
              </li>
            </ul>
          </div>
        )}

        {step === 2 && (
          <div className="bg-slate-50 rounded-xl p-6 mb-8">
            <h3 className="font-semibold text-slate-900 mb-3">Consejos para elegir keywords</h3>
            <ul className="space-y-2 text-sm text-slate-700">
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold">1.</span>
                <span><strong>Relevancia:</strong> Elige keywords relacionadas con tu app</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold">2.</span>
                <span><strong>Volumen:</strong> Busca keywords con buen tráfico de búsqueda</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold">3.</span>
                <span><strong>Competencia:</strong> Mezcla keywords genéricas y específicas</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold">4.</span>
                <span><strong>Long-tail:</strong> No olvides keywords de cola larga (3-4 palabras)</span>
              </li>
            </ul>
          </div>
        )}

        {step === 3 && (
          <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 mb-8 border border-green-200">
            <h3 className="font-semibold text-green-900 mb-3 flex items-center gap-2">
              <CheckCircle className="w-5 h-5" />
              ¡Todo listo para empezar!
            </h3>
            <p className="text-sm text-green-800">
              Ahora puedes crear tu primera app, añadir keywords y empezar a trackear tus rankings. 
              Los datos se actualizarán automáticamente cada hora.
            </p>
          </div>
        )}

        {/* Buttons */}
        <div className="flex gap-3">
          {step < steps.length && (
            <button
              onClick={handleSkip}
              className="px-6 py-3 text-slate-600 hover:text-slate-900 font-semibold transition"
            >
              Saltar
            </button>
          )}
          <button
            onClick={handleNext}
            className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold hover:shadow-lg transition flex items-center justify-center gap-2"
          >
            {step < steps.length ? (
              <>
                Siguiente
                <ArrowRight className="w-5 h-5" />
              </>
            ) : (
              <>
                Empezar
                <CheckCircle className="w-5 h-5" />
              </>
            )}
          </button>
        </div>

        {/* Step indicator */}
        <div className="text-center mt-6 text-sm text-slate-500">
          Paso {step} de {steps.length}
        </div>
      </div>
    </div>
  )
}
