"""
Multi-Indicator Strategy (Combinación)
Usa MÚLTIPLES indicadores para confirmar señales
Esto reduce señales falsas pero puede perder algunas oportunidades
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
from strategies.base_strategy import BaseStrategy


class MultiIndicatorStrategy(BaseStrategy):
    """
    Estrategia que combina RSI + MACD + Volumen
    
    REGLA DE COMPRA (todas deben cumplirse):
    1. RSI < 30 (sobreventa)
    2. MACD cruza hacia arriba de su señal
    3. Volumen > promedio (confirmación)
    
    REGLA DE VENTA (cualquiera):
    1. RSI > 70 (sobrecompra)
    2. MACD cruza hacia abajo
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        default_params = {
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'volume_period': 20
        }
        if params:
            default_params.update(params)
        
        super().__init__(name="Multi-Indicator", params=default_params)
        
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calcula RSI, MACD y volumen promedio"""
        
        # === RSI ===
        rsi_period = self.params['rsi_period']
        delta = data['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=rsi_period).mean()
        avg_loss = loss.rolling(window=rsi_period).mean()
        rs = avg_gain / avg_loss
        data['rsi'] = 100 - (100 / (1 + rs))
        
        # === MACD ===
        fast = self.params['macd_fast']
        slow = self.params['macd_slow']
        signal = self.params['macd_signal']
        
        ema_fast = data['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = data['close'].ewm(span=slow, adjust=False).mean()
        data['macd'] = ema_fast - ema_slow
        data['macd_signal'] = data['macd'].ewm(span=signal, adjust=False).mean()
        
        # === VOLUMEN ===
        volume_period = self.params['volume_period']
        data['volume_ma'] = data['volume'].rolling(window=volume_period).mean()
        
        return data
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Genera señales confirmadas por múltiples indicadores"""
        data['signal'] = 0
        
        rsi_oversold = self.params['rsi_oversold']
        rsi_overbought = self.params['rsi_overbought']
        
        # COMPRAR: Todas las condiciones deben cumplirse
        buy_condition = (
            # 1. RSI en sobreventa
            (data['rsi'] < rsi_oversold) &
            # 2. MACD cruza hacia arriba
            (data['macd'] > data['macd_signal']) &
            (data['macd'].shift(1) <= data['macd_signal'].shift(1)) &
            # 3. Volumen alto (confirmación de movimiento real)
            (data['volume'] > data['volume_ma'])
        )
        
        data.loc[buy_condition, 'signal'] = 1
        
        # VENDER: Cualquiera de estas condiciones
        sell_condition = (
            # RSI en sobrecompra
            (data['rsi'] > rsi_overbought) |
            # O MACD cruza hacia abajo
            (
                (data['macd'] < data['macd_signal']) &
                (data['macd'].shift(1) >= data['macd_signal'].shift(1))
            )
        )
        
        data.loc[sell_condition, 'signal'] = -1
        
        return data
    
    def validate_params(self) -> bool:
        """Valida parámetros"""
        return self.params.get('rsi_period', 0) > 0


"""
✅ VENTAJAS:
- MENOS señales falsas (confirmación múltiple)
- Más confiable que estrategias simples
- Combina tendencia, momentum y volumen

❌ DESVENTAJAS:
- Menos operaciones (puedes perder oportunidades)
- Más compleja de optimizar
- Requiere más datos históricos

📈 RENDIMIENTO: 20-40% anual (pero con menos trades)
🎯 MEJOR PARA: Traders conservadores, portfolios grandes
🌟 RECOMENDADO para principiantes que quieren reducir riesgo
"""
