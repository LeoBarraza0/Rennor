'use client'

import { Card } from '@/components/ui/card'

export function RNNExplanation() {
  const sections = [
    {
      title: 'Qué es una Red Neuronal Recurrente (RNN)',
      content: 'Una RNN es un tipo de red neuronal artificial diseñada para procesar datos secuenciales. A diferencia de las redes neuronales tradicionales, las RNNs tienen conexiones que se realimentan a sí mismas, lo que les permite mantener un "estado" o "memoria" del pasado. Esto las hace ideales para series temporales, donde el valor actual depende fuertemente de los valores anteriores.',
    },
    {
      title: 'Arquitectura de la RNN',
      content: 'La arquitectura utilizada en RENNOR consta de capas LSTM (Long Short-Term Memory) que mejoran la capacidad de la red para aprender dependencias a largo plazo. Las LSTM resuelven el problema del "vanishing gradient" mediante celdas de memoria especializadas.',
      formula: 'h_t = tanh(W_h * [h_{t-1}, x_t] + b_h)',
    },
    {
      title: 'Función de Activación: ReLU',
      content: 'La función de activación ReLU (Rectified Linear Unit) es utilizada en las capas ocultas de RENNOR. Esta función es simple pero efectiva: retorna 0 para valores negativos y el valor original para valores positivos. Permite que la red aprenda representaciones no lineales complejas.',
      formula: 'ReLU(x) = max(0, x)',
    },
    {
      title: 'Función de Activación: Tanh',
      content: 'En la capa de salida se utiliza Tanh (tangente hiperbólica) que normaliza los valores entre -1 y 1. Esta función es simétrica alrededor del origen y facilita el aprendizaje al centrar los datos.',
      formula: 'tanh(x) = (e^x - e^{-x}) / (e^x + e^{-x})',
    },
    {
      title: 'Optimización: Adam',
      content: 'El optimizador Adam (Adaptive Moment Estimation) es un método de descenso de gradiente adaptativo que combina las ventajas de AdaGrad y RMSProp. Ajusta automáticamente la tasa de aprendizaje para cada parámetro durante el entrenamiento.',
    },
    {
      title: 'Métrica de Pérdida: MSE',
      content: 'Se utiliza Mean Squared Error (MSE) como función de pérdida. Calcula el promedio de los errores al cuadrado entre las predicciones y los valores reales. MSE penaliza más los errores grandes, lo que es ideal para predicciones de humedad.',
      formula: 'MSE = (1/n) * Σ(ŷ_i - y_i)²',
    },
  ]

  return (
    <div className="space-y-4">
      {sections.map((section, idx) => (
        <Card key={idx} className="glass-effect p-6 rounded-lg border-white/10 hover:border-white/20 transition-all duration-300 animate-fade-in-up" style={{ animationDelay: `${idx * 100}ms` }}>
          <h3 className="text-lg font-semibold text-accent mb-3">{section.title}</h3>
          <p className="text-neutral-light/80 leading-relaxed mb-4">{section.content}</p>
          {section.formula && (
            <div className="bg-black/30 rounded-lg p-4 font-mono text-sm text-accent/80 overflow-x-auto">
              {section.formula}
            </div>
          )}
        </Card>
      ))}

      <Card className="glass-effect p-6 rounded-lg border-white/10 bg-gradient-to-br from-primary/10 to-accent/10">
        <h3 className="text-lg font-semibold text-neutral-light mb-3">Cómo funciona RENNOR</h3>
        <ol className="space-y-3 text-neutral-light/80">
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary text-white flex items-center justify-center text-xs font-bold">1</span>
            <span>Los datos históricos de humedad relativa se normalizan y preparan para el entrenamiento</span>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary text-white flex items-center justify-center text-xs font-bold">2</span>
            <span>La RNN aprende patrones temporales en los datos a través de múltiples epochs</span>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary text-white flex items-center justify-center text-xs font-bold">3</span>
            <span>Los últimos datos históricos se utilizan como entrada para predecir el futuro</span>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary text-white flex items-center justify-center text-xs font-bold">4</span>
            <span>La red predice valores secuenciales de humedad para los días solicitados</span>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary text-white flex items-center justify-center text-xs font-bold">5</span>
            <span>Los resultados se visualizan en un gráfico interactivo para análisis</span>
          </li>
        </ol>
      </Card>
    </div>
  )
}
