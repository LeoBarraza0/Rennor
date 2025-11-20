"use client"

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"

interface ComparisonChartProps {
  fechas: string[]
  valoresReales: number[]
  valoresPredichos: number[]
}

export default function ComparisonChart({ fechas, valoresReales, valoresPredichos }: ComparisonChartProps) {
  // Preparar datos para el gráfico
  const data = fechas.map((fecha, index) => ({
    fecha: new Date(fecha).toLocaleDateString("es-CO", { month: "short", day: "numeric" }),
    real: Number.parseFloat(valoresReales[index]?.toFixed(2)) || 0,
    predicho: Number.parseFloat(valoresPredichos[index]?.toFixed(2)) || 0,
  }))

  return (
    <div className="w-full h-full flex flex-col">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-foreground mb-2">Comparación: Datos Reales vs Predicciones</h3>
        <p className="text-sm text-muted-foreground">Visualización del desempeño del modelo en datos de prueba</p>
      </div>

      <div className="flex-1 min-h-[350px] w-full">
        {/* Usar una altura fija para evitar que el contenedor responsive tenga 0px
            si el layout flex colapsa; 350px es consistente con otros gráficos */}
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 50 }}>
            <defs>
              <linearGradient id="colorReal" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#5a7f8f" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#5a7f8f" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorPredicho" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#7eb3d9" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#7eb3d9" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(90, 127, 143, 0.1)" />
            <XAxis dataKey="fecha" stroke="#5a7f8f" angle={-45} textAnchor="end" height={80} tick={{ fontSize: 12 }} />
            <YAxis
              stroke="#5a7f8f"
              label={{ value: "Humedad Relativa (%)", angle: -90, position: "insideLeft" }}
              domain={[0, 100]}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "rgba(30, 30, 35, 0.95)",
                border: "1px solid #5a7f8f",
                borderRadius: "8px",
              }}
              labelStyle={{ color: "#f5f5f0" }}
              formatter={(value) => (value == null ? '-' : Number(value).toFixed(2))}
            />
            <Legend wrapperStyle={{ paddingTop: "20px" }} iconType="line" />
            <Line
              type="monotone"
              dataKey="real"
              stroke="#5a7f8f"
              strokeWidth={2.5}
              dot={false}
              fillOpacity={1}
              fill="url(#colorReal)"
              name="Datos Reales"
              isAnimationActive={true}
            />
            <Line
              type="monotone"
              dataKey="predicho"
              stroke="#7eb3d9"
              strokeWidth={2.5}
              dot={false}
              fillOpacity={1}
              fill="url(#colorPredicho)"
              name="Predicciones del Modelo"
              isAnimationActive={true}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
