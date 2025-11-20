"use client"

import { Card } from "@/components/ui/card"
import type { Metrics } from "@/lib/api"

interface MetricsDisplayProps {
  metrics: Metrics | null
}

export function MetricsDisplay({ metrics }: MetricsDisplayProps) {
  if (!metrics) {
    return null
  }

  const metricsData = [
    {
      label: "MSE",
      value: metrics.mse.toFixed(2),
      description: "Error Cuadrático Medio",
      color: "from-blue-400 to-blue-600",
      icon: "📊",
    },
    {
      label: "RMSE",
      value: metrics.rmse.toFixed(2),
      description: "Raíz del Error Cuadrático",
      color: "from-purple-400 to-purple-600",
      icon: "📈",
    },
    {
      label: "MAE",
      value: metrics.mae.toFixed(2),
      description: "Error Absoluto Medio",
      color: "from-orange-400 to-orange-600",
      icon: "📉",
    },
    {
      label: "R²",
      value: (metrics.r_squared * 100).toFixed(1) + "%",
      description: "Coeficiente de Determinación",
      color: "from-green-400 to-green-600",
      icon: "✓",
    },
  ]

  return (
    <div>
      <h3 className="text-lg font-semibold text-neutral-light mb-4 flex items-center gap-2">
        <span className="text-xl">📊</span>
        Métricas del Modelo
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
        {metricsData.map((metric) => (
          <Card
            key={metric.label}
            className="glass-effect p-4 rounded-lg border-white/10 hover:border-white/20 transition-all duration-300 group cursor-pointer"
          >
            <div className="flex items-start justify-between mb-2">
              <p className="text-xs text-neutral-light/70 font-medium">{metric.label}</p>
              <span className="text-lg opacity-60 group-hover:opacity-100 transition-opacity">{metric.icon}</span>
            </div>
            <p className={`text-2xl font-bold bg-gradient-to-r ${metric.color} bg-clip-text text-transparent mb-1`}>
              {metric.value}
            </p>
            <p className="text-xs text-neutral-light/50">{metric.description}</p>
          </Card>
        ))}
      </div>
    </div>
  )
}