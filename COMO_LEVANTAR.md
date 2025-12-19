# 🚀 Cómo Levantar el Dashboard

## Opción Rápida

**Ya están ambos servidores corriendo!** ✅

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **Swagger**: http://localhost:8000/docs

## Comandos para Levantar (si los cerraste)

### Terminal 1 - Backend:
```bash
cd /home/gonza/Develop/algodetraiding
source venv/bin/activate
uvicorn api.main:app --reload --port 8000
```

### Terminal 2 - Frontend:
```bash
cd /home/gonza/Develop/algodetraiding/web/frontend
npm run dev
```

## ✅ Listo para usar!

1. Abre http://localhost:3000
2. Selecciona una estrategia (ej: MA Crossover)
3. Configura el backtest
4. Click en "🚀 Run Backtest"
5. Los resultados aparecen automáticamente

---

Ver `DASHBOARD_README.md` para documentación completa.
