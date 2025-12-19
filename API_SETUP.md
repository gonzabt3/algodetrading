# 🚀 Trading Dashboard - API y Database Setup Completo

## ✅ Lo que YA está funcionando:

1. **PostgreSQL 16** corriendo en Docker (puerto 5433)
2. **Redis 7** corriendo en Docker  
3. **SQLAlchemy Models** creados y migrados
4. **Alembic** configurado
5. **CRUD Operations** implementadas
6. **FastAPI estructura** lista (falta fix de imports)

## 🔧 Para iniciar el sistema:

```bash
# Terminal 1: Levantar base de datos
sudo docker start trading_postgres trading_redis

# Terminal 2: Levantar API
cd /home/gonza/Develop/algodetraiding
source venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## 📊 Base de datos:

```
URL: postgresql://trading_user:trading_pass@localhost:5433/trading_db

Tablas creadas:
- strategies (estrategias de trading)
- backtests (resultados de backtests)
- trades (trades individuales)
- equity_points (curva de equity)
- market_data (caché de datos de mercado)
```

## 🌐 API Endpoints (cuando esté corriendo):

- http://localhost:8000/docs - Documentación interactiva (Swagger)
- http://localhost:8000/api/strategies - Lista estrategias
- http://localhost:8000/api/backtests - Lista backtests
- POST http://localhost:8000/api/backtests/run - Ejecutar backtest

## ⏭️ Próximos pasos:

1. Arreglar imports en `api/main.py` (2 min)
2. Probar API con Swagger UI
3. Crear frontend React
4. Migrar datos JSON existentes

**Estado actual**: Backend ~90% completo 🎉
