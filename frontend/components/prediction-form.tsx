'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'

interface PredictionFormProps {
  onSubmit: (dias: number) => Promise<void>
  isLoading: boolean
}

export function PredictionForm({ onSubmit, isLoading }: PredictionFormProps) {
  const [dias, setDias] = useState(7)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (dias >= 1) {
      await onSubmit(dias)
    }
  }

  return (
    <Card className="glass-effect p-6 rounded-2xl border-white/10">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div>
          <label className="block text-sm font-medium text-neutral-light mb-2">
            Días a predecir
          </label>
          <div className="flex gap-3 items-end">
            <Input
              type="number"
              min="1"
              value={dias}
              onChange={(e) => setDias(Math.max(1, parseInt(e.target.value) || 1))}
              className="flex-1 bg-white/5 border-white/20 text-neutral-light placeholder-neutral-light/50 rounded-lg"
              placeholder="7"
              disabled={isLoading}
            />
            <span className="text-xs text-neutral-light/70">días</span>
          </div>
          <p className="text-xs text-neutral-light/60 mt-2">
            Valor recomendado: 7 días
          </p>
        </div>

        <Button
          type="submit"
          disabled={isLoading}
          className="bg-primary hover:bg-primary-light text-neutral-light font-semibold py-2 rounded-lg transition-all duration-300 disabled:opacity-50"
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <span className="inline-block w-4 h-4 border-2 border-neutral-light/30 border-t-neutral-light rounded-full animate-spin" />
              Generando predicción...
            </span>
          ) : (
            'Generar Predicción'
          )}
        </Button>
      </form>
    </Card>
  )
}
