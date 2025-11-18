'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Card } from '@/components/ui/card'

interface ChartData {
  dia: number
  humedad: number
}

interface PredictionChartProps {
  data: ChartData[] | null
  isLoading: boolean
}

export function PredictionChart({ data, isLoading }: PredictionChartProps) {
  if (isLoading) {
    return (
      <Card className="glass-effect p-6 rounded-2xl flex items-center justify-center h-80 border-white/10">
        <div className="text-center">
          <div className="inline-block w-12 h-12 border-3 border-primary/30 border-t-primary rounded-full animate-spin mb-3" />
          <p className="text-neutral-light/70">Procesando predicción...</p>
        </div>
      </Card>
    )
  }

  if (!data || data.length === 0) {
    return (
      <Card className="glass-effect p-6 rounded-2xl flex items-center justify-center h-80 border-white/10">
        <div className="text-center">
          <p className="text-neutral-light/70">Ingresa los días y haz clic en "Generar Predicción"</p>
        </div>
      </Card>
    )
  }

  return (
    <Card className="glass-effect p-6 rounded-2xl border-white/10">
      <h3 className="text-lg font-semibold text-neutral-light mb-4">Predicción de Humedad Relativa</h3>
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis
            dataKey="dia"
            stroke="rgba(255,255,255,0.5)"
            label={{ value: 'Día', position: 'insideBottomRight', offset: -5, fill: 'rgba(255,255,255,0.7)' }}
          />
          <YAxis
            stroke="rgba(255,255,255,0.5)"
            domain={[0, 100]}
            label={{ value: 'Humedad (%)', angle: -90, position: 'insideLeft', fill: 'rgba(255,255,255,0.7)' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(26, 31, 36, 0.95)',
              border: '1px solid rgba(255,255,255,0.2)',
              borderRadius: '8px',
              color: 'rgb(245, 245, 240)',
            }}
            formatter={(value) => [`${value.toFixed(2)}%`, 'Humedad']}
            cursor={{ stroke: 'rgba(100, 181, 246, 0.5)' }}
          />
          <Line
            type="monotone"
            dataKey="humedad"
            stroke="#64b5f6"
            strokeWidth={3}
            dot={{ fill: '#5a7f8f', r: 5 }}
            activeDot={{ r: 7 }}
            isAnimationActive={true}
            animationDuration={800}
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  )
}
