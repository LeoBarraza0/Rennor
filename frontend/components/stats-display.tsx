'use client'

import { Card } from '@/components/ui/card'

interface StatsDisplayProps {
  data: number[] | null
}

export function StatsDisplay({ data }: StatsDisplayProps) {
  if (!data || data.length === 0) {
    return null
  }

  const avg = (data.reduce((a, b) => a + b, 0) / data.length).toFixed(2)
  const max = Math.max(...data).toFixed(2)
  const min = Math.min(...data).toFixed(2)

  const stats = [
    { label: 'Promedio', value: `${avg}%`, color: 'from-accent to-blue-600' },
    { label: 'Máximo', value: `${max}%`, color: 'from-warning to-orange-600' },
    { label: 'Mínimo', value: `${min}%`, color: 'from-success to-green-600' },
  ]

  return (
    <div className="grid grid-cols-3 gap-4">
      {stats.map((stat) => (
        <Card
          key={stat.label}
          className="glass-effect p-4 rounded-lg border-white/10 text-center hover:border-white/20 transition-all duration-300"
        >
          <p className="text-xs text-neutral-light/70 mb-2">{stat.label}</p>
          <p className={`text-2xl font-bold bg-gradient-to-r ${stat.color} bg-clip-text text-transparent`}>
            {stat.value}
          </p>
        </Card>
      ))}
    </div>
  )
}
