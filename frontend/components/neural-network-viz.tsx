'use client'

import { useEffect, useRef } from 'react'
import { Card } from '@/components/ui/card'

export function NeuralNetworkViz() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    canvas.width = canvas.offsetWidth
    canvas.height = canvas.offsetHeight

    const neurons = {
      input: 5,
      hidden1: 8,
      hidden2: 6,
      output: 1,
    }

    const positions = {
      input: Array.from({ length: neurons.input }, (_, i) => ({
        x: 50,
        y: (canvas.height / (neurons.input + 1)) * (i + 1),
      })),
      hidden1: Array.from({ length: neurons.hidden1 }, (_, i) => ({
        x: 250,
        y: (canvas.height / (neurons.hidden1 + 1)) * (i + 1),
      })),
      hidden2: Array.from({ length: neurons.hidden2 }, (_, i) => ({
        x: 450,
        y: (canvas.height / (neurons.hidden2 + 1)) * (i + 1),
      })),
      output: [
        {
          x: 650,
          y: canvas.height / 2,
        },
      ],
    }

    let animationTime = 0

    const animate = () => {
      animationTime += 0.005

      ctx.clearRect(0, 0, canvas.width, canvas.height)
      ctx.globalAlpha = 0.6

      // Draw connections with gradient
      const layers = [
        [positions.input, positions.hidden1],
        [positions.hidden1, positions.hidden2],
        [positions.hidden2, positions.output],
      ]

      layers.forEach((layer, layerIdx) => {
        const [from, to] = layer
        from.forEach((fromPos) => {
          to.forEach((toPos) => {
            const gradient = ctx.createLinearGradient(fromPos.x, fromPos.y, toPos.x, toPos.y)
            gradient.addColorStop(0, 'rgba(100, 181, 246, 0.3)')
            gradient.addColorStop(1, 'rgba(90, 127, 143, 0.3)')

            ctx.strokeStyle = gradient
            ctx.lineWidth = 1.5
            ctx.beginPath()
            ctx.moveTo(fromPos.x, fromPos.y)
            ctx.lineTo(toPos.x, toPos.y)
            ctx.stroke()
          })
        })
      })

      ctx.globalAlpha = 1

      // Draw neurons
      const allNeurons = [...positions.input, ...positions.hidden1, ...positions.hidden2, ...positions.output]

      allNeurons.forEach((pos, idx) => {
        const pulse = Math.sin(animationTime + idx * 0.3) * 0.5 + 0.5

        const gradient = ctx.createRadialGradient(pos.x, pos.y, 0, pos.x, pos.y, 8)
        gradient.addColorStop(0, `rgba(100, 181, 246, ${0.8 + pulse * 0.2})`)
        gradient.addColorStop(1, `rgba(90, 127, 143, ${0.4 + pulse * 0.1})`)

        ctx.fillStyle = gradient
        ctx.beginPath()
        ctx.arc(pos.x, pos.y, 6 + pulse * 2, 0, Math.PI * 2)
        ctx.fill()

        ctx.strokeStyle = 'rgba(245, 245, 240, 0.5)'
        ctx.lineWidth = 2
        ctx.stroke()
      })

      requestAnimationFrame(animate)
    }

    animate()
  }, [])

  return (
    <Card className="glass-effect p-6 rounded-lg border-white/10">
      <h3 className="text-lg font-semibold text-neutral-light mb-4">Visualización de la Red Neuronal</h3>
      <canvas
        ref={canvasRef}
        className="w-full h-64 rounded-lg bg-black/20"
      />
      <p className="text-xs text-neutral-light/60 mt-3 text-center">
        Arquitectura RNN: 5 entrada → 8 oculta → 6 oculta → 1 salida
      </p>
    </Card>
  )
}
