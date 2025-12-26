# Refactorización SOLID - Arquitectura Modular

## Principios Aplicados

### 1. Single Responsibility Principle (SRP)
**Antes**: `api/main.py` tenía 947 líneas con múltiples responsabilidades  
**Después**: Separado en módulos especializados

- `api/services/strategy_registry.py`: Gestión de registro de estrategias
- `api/services/backtest_service.py`: Lógica de ejecución de backtests
- `api/routers/strategies.py`: Endpoints de estrategias
- `api/routers/pair_data.py`: Endpoints de datos de pares
- `api/routers/backtests.py`: Endpoints de historial de backtests
- `api/routers/market_data.py`: Endpoints de datos de mercado
- `api/main_v2.py`: Solo configuración y arranque de la aplicación (75 líneas)

### 2. Open/Closed Principle (OCP)
**Antes**: Agregar estrategias requería modificar el diccionario `STRATEGIES` en `main.py`  
**Después**: Sistema de registro extensible

```python
# Agregar nueva estrategia sin modificar código existente
from api.services import registry

registry.register(
    'my_strategy',
    MyStrategyClass,
    'My Strategy',
    'Description',
    {'param1': 10}
)
```

### 3. Liskov Substitution Principle (LSP)
Todas las estrategias heredan de `BaseStrategy` o `MultiSymbolStrategy` y son intercambiables:

```python
# Cualquier estrategia funciona igual
strategy = registry.get_strategy_class(strategy_id)(params=params)
backtester = Backtester(strategy=strategy)
```

### 4. Interface Segregation Principle (ISP)
**Antes**: Un solo archivo con todos los endpoints  
**Después**: Routers separados por dominio

- `/api/strategies` → strategies.py
- `/api/pair-data` → pair_data.py
- `/api/backtests` → backtests.py
- `/api/fetch-data` → market_data.py
- `/api/brokers` → brokers.py

### 5. Dependency Inversion Principle (DIP)
**BacktestService** depende de abstracciones, no de implementaciones concretas:

```python
class BacktestService:
    def __init__(self, db_session: Session, data_fetcher: DataFetcher):
        self.db = db_session  # Abstracción (Session)
        self.data_fetcher = data_fetcher  # Abstracción (DataFetcher)
```

## Estructura de Archivos

```
api/
├── main_v2.py                    # 75 líneas - Solo configuración
├── services/
│   ├── __init__.py
│   ├── strategy_registry.py     # SRP: Gestión de estrategias
│   └── backtest_service.py      # SRP: Ejecución de backtests
└── routers/
    ├── strategies.py             # ISP: Endpoints de estrategias
    ├── pair_data.py              # ISP: Endpoints de pares
    ├── backtests.py              # ISP: Endpoints de historial
    ├── market_data.py            # ISP: Endpoints de datos
    └── brokers.py                # ISP: Endpoints de brokers
```

## Migración

Para usar la nueva arquitectura:

### Opción 1: Reemplazo directo
```bash
mv api/main.py api/main_old.py
mv api/main_v2.py api/main.py
```

### Opción 2: Prueba lado a lado
```bash
# Terminal 1 - Arquitectura vieja
uvicorn api.main:app --reload --port 8000

# Terminal 2 - Arquitectura nueva
uvicorn api.main_v2:app --reload --port 8001
```

## Beneficios

1. **Mantenibilidad**: Cada archivo tiene <200 líneas y una responsabilidad clara
2. **Testabilidad**: Servicios pueden ser testeados independientemente
3. **Extensibilidad**: Agregar estrategias sin modificar código existente
4. **Escalabilidad**: Fácil agregar nuevos routers/servicios
5. **Legibilidad**: Estructura clara y navegable

## Testing

```bash
# Test de servicios
pytest tests/test_strategy_registry.py
pytest tests/test_backtest_service.py

# Test de routers
pytest tests/test_strategy_router.py
pytest tests/test_pair_data_router.py
```

## Próximos Pasos

1. Crear tests unitarios para servicios
2. Migrar frontend a arquitectura similar
3. Agregar dependency injection container
4. Implementar patrones de diseño (Factory, Observer)
