'use client'

import Image from 'next/image'
import { Card } from '@/components/ui/card'

export function Header() {
  return (
    <header className="sticky top-0 z-50 backdrop-blur-lg border-b border-white/10">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center gap-4">
        <div className="relative w-12 h-12">
          <div className="absolute inset-0 bg-gradient-to-br from-primary/30 to-accent/30 rounded-full blur-lg" />
          <div className="relative w-full h-full bg-primary rounded-full flex items-center justify-center font-bold text-white text-lg">
            💧
          </div>
        </div>
        <div>
          <h1 className="text-2xl font-bold text-neutral-light">RENNOR</h1>
          <p className="text-xs text-neutral-light/60">RNN para Predicción de Humedad</p>
        </div>
      </div>
    </header>
  )
}
