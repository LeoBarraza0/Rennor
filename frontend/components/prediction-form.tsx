"use client"

import type React from "react"

import { useState } from "react"

interface PredictionFormProps {
  onSubmit: (dias: number) => void
  isLoading: boolean
}

export function PredictionForm({ onSubmit, isLoading }: PredictionFormProps) {
  const [dias, setDias] = useState("7")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const diasNum = Number.parseInt(dias, 10)
    if (diasNum > 0) {
      onSubmit(diasNum)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 hover:border-white/20 transition-all duration-300"
    >
      <div className="space-y-4">
        <div>
          <label htmlFor="dias" className="block text-sm font-medium text-neutral-light mb-2">
            Días a Predecir
          </label>
          <input
            type="number"
            id="dias"
            value={dias}
            onChange={(e) => setDias(e.target.value)}
            min="1"
            className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-neutral-light placeholder-neutral-light/50 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
            placeholder="Ingresa número de días"
          />
          <p className="text-xs text-neutral-light/50 mt-2">Recomendado: 7 días</p>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full px-6 py-3 bg-gradient-to-r from-primary to-primary-light text-neutral-dark font-semibold rounded-lg hover:shadow-lg hover:shadow-primary/50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
        >
          {isLoading ? "Generando Predicción..." : "Generar Predicción"}
        </button>
      </div>
    </form>
  )
}
