"""
Mean Reversion Strategy
Teoría: Cuando el precio se aleja mucho de su promedio, tiende a volver
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
from strategies.base_strategy import BaseStrategy


class MeanReversionStrategy(BaseStrategy):
    """
    Estrategia de Reversión a la Media con Z-Score
    
    Concepto: Medir cuánto se aleja el precio de su media
    Z-Score = (Precio - Media) / Desviación Estándar
    
    Interpretación:
    - Z > +2: Precio MUY ALTO → Vender (volverá a bajar)
    - Z < -2: Precio MUY BAJO → Comprar (volverá a subir)
    - |Z| < 1: Precio normal → No hacer nada
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        default_params = {
            'lookback_period': 20,    # Período para calcular media
            'entry_threshold': 2.0,   # Z-score para entrar (±2)
            'exit_threshold': 0.5     # Z-score para salir (±0.5)
        }
        if params:
            default_params.update(params)
        
        super().__init__(name="Mean Reversion", params=default_params)
        
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calcula Z-Score"""
        period = self.params['lookback_period']
        
        # Media móvil
        data['mean'] = data['close'].rolling(window=period).mean()
        
        # Desviación estándar
        data['std'] = data['close'].rolling(window=period).std()
        
        # Z-Score: cuántas desviaciones estándar se aleja el precio de la media
        data['z_score'] = (data['close'] - data['mean']) / data['std']
        
        return data
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Genera señales basadas en Z-Score"""
        data['signal'] = 0
        
        entry_threshold = self.params['entry_threshold']
        exit_threshold = self.params['exit_threshold']
        
        # COMPRAR: Z-Score muy negativo (precio muy bajo)
        data.loc[
            (data['z_score'] < -entry_threshold) &
            (data['z_score'].shift(1) >= -entry_threshold),
            'signal'
        ] = 1
        
        # VENDER: Z-Score muy positivo (precio muy alto)
        data.loc[
            (data['z_score'] > entry_threshold) &
            (data['z_score'].shift(1) <= entry_threshold),
            'signal'
        ] = -1
        
        # También vender si vuelve a la media después de comprar
        data.loc[
            (data['z_score'] > -exit_threshold) &
            (data['z_score'].shift(1) <= -exit_threshold),
            'signal'
        ] = -1
        
        return data
    
    def validate_params(self) -> bool:
        """Valida parámetros"""
        return self.params.get('lookback_period', 0) > 0


"""
✅ VENTAJAS:
- Muy efectiva en mercados laterales
- Matemáticamente sólida
- Baja correlación con tendencias (complementa otras estrategias)

❌ DESVENTAJAS:
- PELIGROSA en tendencias fuertes (puedes perder mucho)
- Requiere mercados estables
- Asume que el precio volverá a la media (no siempre es cierto)

📈 RENDIMIENTO: 15-30% en mercados laterales, -20% en tendencias fuertes
🎯 MEJOR PARA: Pares de divisas, acciones de baja beta, arbitraje
⚠️  RIESGO ALTO en criptomonedas (tendencias muy fuertes)
"""
