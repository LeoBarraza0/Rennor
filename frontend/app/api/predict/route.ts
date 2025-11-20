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

    const flaskUrl = process.env.FLASK_BACKEND_URL || 'http://localhost:5000';

    const response = await fetch(`${flaskUrl}/api/prediccion`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ dias_futuros }),
    });

    // Debug / diagnóstico: leer body aunque status !== 200
    const text = await response.text();
    let data;
    try {
      data = text ? JSON.parse(text) : {};
    } catch (e) {
      // si no es JSON, dejar el texto crudo
      data = { raw: text };
    }

    // Registrar para debugging en servidor Next
    console.log('Flask response status:', response.status);
    console.log('Flask response body:', data);

    // Reenviar exactamente lo que devolvió Flask (status + body)
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Prediction error (route.ts):', error);
    return NextResponse.json(
      { error: 'Error al generar predicción' },
      { status: 500 }
    );
  }
}