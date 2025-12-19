"""
Sistema Simple de Almacenamiento de Resultados
Guarda resultados de backtests sin necesidad de base de datos
"""
import json
import os
from datetime import datetime
import pandas as pd
from typing import Dict, Any


class ResultsLogger:
    """
    Guarda y recupera resultados de backtests de forma simple
    """
    
    def __init__(self, results_dir: str = 'data/backtest_results'):
        """
        Inicializa el logger de resultados
        
        Args:
            results_dir: Directorio donde guardar resultados
        """
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
    
    def save_backtest(
        self,
        strategy_name: str,
        symbol: str,
        results: Dict[str, Any],
        params: Dict[str, Any] = None
    ) -> str:
        """
        Guarda resultados de un backtest
        
        Args:
            strategy_name: Nombre de la estrategia
            symbol: Activo (BTC/USDT, etc.)
            results: Diccionario con resultados
            params: Parámetros usados
            
        Returns:
            Ruta del archivo guardado
        """
        # Crear timestamp para nombre único
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{strategy_name}_{symbol.replace('/', '_')}_{timestamp}.json"
        filepath = os.path.join(self.results_dir, filename)
        
        # Preparar datos para guardar
        data = {
            'timestamp': datetime.now().isoformat(),
            'strategy': strategy_name,
            'symbol': symbol,
            'params': params or {},
            'results': {
                'initial_capital': results.get('initial_capital'),
                'final_capital': results.get('final_capital'),
                'total_return': results.get('total_return'),
                'sharpe_ratio': results.get('sharpe_ratio'),
                'max_drawdown': results.get('max_drawdown'),
                'total_trades': results.get('total_trades'),
                'win_rate': results.get('win_rate')
            },
            'trades': results.get('trades', [])
        }
        
        # Guardar como JSON
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"✓ Resultados guardados en: {filepath}")
        return filepath
    
    def load_backtest(self, filename: str) -> Dict[str, Any]:
        """Carga resultados de un backtest"""
        filepath = os.path.join(self.results_dir, filename)
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def list_backtests(self, strategy: str = None, symbol: str = None) -> list:
        """
        Lista todos los backtests guardados
        
        Args:
            strategy: Filtrar por estrategia (opcional)
            symbol: Filtrar por símbolo (opcional)
            
        Returns:
            Lista de archivos de backtests
        """
        files = []
        for filename in os.listdir(self.results_dir):
            if not filename.endswith('.json'):
                continue
            
            # Filtros opcionales
            if strategy and strategy not in filename:
                continue
            if symbol and symbol.replace('/', '_') not in filename:
                continue
            
            files.append(filename)
        
        return sorted(files, reverse=True)  # Más recientes primero
    
    def get_best_result(
        self,
        metric: str = 'total_return',
        strategy: str = None,
        symbol: str = None
    ) -> Dict[str, Any]:
        """
        Encuentra el mejor resultado según una métrica
        
        Args:
            metric: 'total_return', 'sharpe_ratio', 'win_rate', etc.
            strategy: Filtrar por estrategia (opcional)
            symbol: Filtrar por símbolo (opcional)
            
        Returns:
            Mejor resultado encontrado
        """
        files = self.list_backtests(strategy, symbol)
        
        if not files:
            return None
        
        best_result = None
        best_value = float('-inf')
        
        for filename in files:
            result = self.load_backtest(filename)
            value = result['results'].get(metric, float('-inf'))
            
            if value > best_value:
                best_value = value
                best_result = result
                best_result['filename'] = filename
        
        return best_result
    
    def create_summary_report(self) -> pd.DataFrame:
        """
        Crea un resumen de todos los backtests
        
        Returns:
            DataFrame con resumen de todos los backtests
        """
        files = self.list_backtests()
        
        if not files:
            return pd.DataFrame()
        
        summaries = []
        for filename in files:
            data = self.load_backtest(filename)
            
            summaries.append({
                'Fecha': data['timestamp'][:10],
                'Hora': data['timestamp'][11:19],
                'Estrategia': data['strategy'],
                'Símbolo': data['symbol'],
                'Retorno (%)': data['results']['total_return'],
                'Sharpe': data['results']['sharpe_ratio'],
                'Drawdown (%)': data['results']['max_drawdown'],
                'Trades': data['results']['total_trades'],
                'Win Rate (%)': data['results']['win_rate'],
                'Archivo': filename
            })
        
        df = pd.DataFrame(summaries)
        return df.sort_values('Fecha', ascending=False)
    
    def clean_old_results(self, days: int = 30):
        """
        Elimina resultados más antiguos que N días
        
        Args:
            days: Días de antigüedad
        """
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        deleted = 0
        
        for filename in os.listdir(self.results_dir):
            if not filename.endswith('.json'):
                continue
            
            filepath = os.path.join(self.results_dir, filename)
            data = self.load_backtest(filename)
            
            file_date = datetime.fromisoformat(data['timestamp'])
            
            if file_date < cutoff:
                os.remove(filepath)
                deleted += 1
        
        print(f"✓ Eliminados {deleted} resultados antiguos (>{days} días)")


# ============================================================================
# EJEMPLOS DE USO
# ============================================================================

def ejemplo_uso():
    """Ejemplos de cómo usar el sistema"""
    
    logger = ResultsLogger()
    
    print("=" * 70)
    print("SISTEMA SIMPLE DE ALMACENAMIENTO DE RESULTADOS")
    print("=" * 70)
    print()
    
    # 1. GUARDAR resultados
    print("1️⃣  GUARDAR RESULTADOS:")
    print("-" * 70)
    
    resultados_ejemplo = {
        'initial_capital': 10000,
        'final_capital': 11937.50,
        'total_return': 19.37,
        'sharpe_ratio': 0.54,
        'max_drawdown': -19.57,
        'total_trades': 4,
        'win_rate': 100.0,
        'trades': [
            {'type': 'BUY', 'price': 103.10, 'shares': 96},
            {'type': 'SELL', 'price': 94.23, 'shares': 96}
        ]
    }
    
    logger.save_backtest(
        strategy_name='MA Crossover',
        symbol='BTC/USDT',
        results=resultados_ejemplo,
        params={'fast_period': 20, 'slow_period': 50}
    )
    print()
    
    # 2. LISTAR backtests guardados
    print("2️⃣  LISTAR BACKTESTS:")
    print("-" * 70)
    backtests = logger.list_backtests()
    print(f"Total de backtests guardados: {len(backtests)}")
    for i, bt in enumerate(backtests[:5], 1):
        print(f"   {i}. {bt}")
    print()
    
    # 3. ENCONTRAR el mejor resultado
    print("3️⃣  MEJOR RESULTADO:")
    print("-" * 70)
    mejor = logger.get_best_result(metric='total_return')
    if mejor:
        print(f"   Estrategia: {mejor['strategy']}")
        print(f"   Símbolo: {mejor['symbol']}")
        print(f"   Retorno: {mejor['results']['total_return']:.2f}%")
        print(f"   Fecha: {mejor['timestamp'][:10]}")
    print()
    
    # 4. RESUMEN de todos
    print("4️⃣  RESUMEN DE TODOS LOS BACKTESTS:")
    print("-" * 70)
    df = logger.create_summary_report()
    if not df.empty:
        print(df.head(10).to_string(index=False))
    else:
        print("   No hay backtests guardados aún")
    print()
    
    print("=" * 70)
    print("✅ VENTAJAS DE ESTE SISTEMA:")
    print("=" * 70)
    print("""
    ✓ Simple (solo archivos JSON)
    ✓ No requiere configuración
    ✓ Fácil de debuggear (abre el JSON con cualquier editor)
    ✓ Portable (copia la carpeta y listo)
    ✓ Suficiente para 99% de casos de principiantes
    ✓ Migrar a DB más adelante es fácil
    """)
    print()


if __name__ == '__main__':
    ejemplo_uso()
