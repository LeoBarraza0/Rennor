"use client"

import { useState } from "react"
import { Header } from "@/components/header"
import { PredictionForm } from "@/components/prediction-form"
import { PredictionChart } from "@/components/prediction-chart"
import { StatsDisplay } from "@/components/stats-display"
import { MetricsDisplay } from "@/components/metrics-display"
import { RNNExplanation } from "@/components/rnn-explanation"
import { NeuralNetworkViz } from "@/components/neural-network-viz"
import { getPrediction } from "@/lib/api"
import type { Metrics } from "@/lib/api"

type TabType = "prediccion" | "info"

interface ChartData {
  dia: number
  humedad: number
}

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabType>("prediccion")
  const [predictions, setPredictions] = useState<number[] | null>(null)
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [chartData, setChartData] = useState<ChartData[] | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handlePrediction = async (dias: number) => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await getPrediction(dias)
      const data = response.predicciones
      setPredictions(data)
      setMetrics(response.metricas)

      const formatted = data.map((humedad, idx) => ({
        dia: idx + 1,
        humedad,
      }))

      setChartData(formatted)
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Error al generar predicción"
      setError(errorMsg)
      console.error(errorMsg)
    } finally {
      setIsLoading(false)
    }
  }

  const tabs = [
    { id: "prediccion", label: "Predicción" },
    { id: "info", label: "Información RNN" },
  ] as const

  return (
    <main className="min-h-screen bg-gradient-to-br from-neutral-dark via-neutral-dark to-primary-dark">
      <Header />

      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Tab Navigation */}
        <div className="flex gap-2 mb-8 border-b border-white/10 pb-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => {
                setActiveTab(tab.id)
                setError(null)
              }}
              className={`px-4 py-2 rounded-lg transition-all duration-300 font-medium text-sm ${
                activeTab === tab.id
                  ? "bg-primary text-neutral-light shadow-lg shadow-primary/50"
                  : "text-neutral-light/70 hover:text-neutral-light hover:bg-white/5"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-300 text-sm">{error}</div>
        )}

        {/* Tab Content */}
        {activeTab === "prediccion" && (
          <div className="space-y-6 animate-fade-in-up">
            <PredictionForm onSubmit={handlePrediction} isLoading={isLoading} />

            {chartData && (
              <>
                <PredictionChart data={chartData} isLoading={isLoading} />
                <StatsDisplay data={predictions} />
                <MetricsDisplay metrics={metrics} />
              </>
            )}

            {!chartData && !isLoading && (
              <div className="text-center py-12 text-neutral-light/60">
                <p className="text-lg">Ingresa el número de días para comenzar la predicción</p>
              </div>
            )}
          </div>
        )}

        {activeTab === "info" && (
          <div className="space-y-6 animate-fade-in-up">
            <NeuralNetworkViz />
            <RNNExplanation />
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t border-white/10 mt-12 py-6">
        <div className="max-w-6xl mx-auto px-4 text-center text-neutral-light/50 text-xs">
          <p>RENNOR - Red Neuronal Recurrente para Predicción de Humedad Relativa</p>
          <p>Desarrollado con React, Next.js y TensorFlow</p>
        </div>
      </footer>
    </main>
  )
}
