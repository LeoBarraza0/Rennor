import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { dias_futuros } = await request.json();

    if (!dias_futuros || dias_futuros < 1 || dias_futuros > 30) {
      return NextResponse.json(
        { error: 'Número de días debe estar entre 1 y 30' },
        { status: 400 }
      );
    }

    // Llamar a tu backend Flask
    const flaskUrl = process.env.FLASK_BACKEND_URL || 'http://localhost:5000';
    
    const response = await fetch(`${flaskUrl}/api/prediccion`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dias_futuros }),
    });

    if (!response.ok) {
      throw new Error(`Flask error: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      predicciones: data.predicciones,
      metricas: data.metricas,
    });
  } catch (error) {
    console.error('Prediction error:', error);
    return NextResponse.json(
      { error: 'Error al generar predicción' },
      { status: 500 }
    );
  }
}
