import { Geist, Geist_Mono } from 'next/font/google'
import './global.css'

const geistSans = Geist({ subsets: ['latin'] })
const geistMono = Geist_Mono({ subsets: ['latin'] })

export const metadata = {
  title: 'RENNOR - RNN Humidity Prediction',
  description: 'Predicción de humedad relativa usando Redes Neuronales Recurrentes',
  icons: {
    icon: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" fontSize="90">💧</text></svg>',
  },
}

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#5a7f8f',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body className={`${geistSans.className} ${geistMono.className}`}>
        {children}
      </body>
    </html>
  )
}
