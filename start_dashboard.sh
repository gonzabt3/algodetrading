#!/bin/bash

# Script para levantar el dashboard completo
echo "🚀 Iniciando Trading Dashboard..."

# 1. Verificar Docker containers
echo ""
echo "📦 Verificando containers de Docker..."
if ! sudo docker ps | grep -q trading_postgres; then
    echo "⚠️  PostgreSQL no está corriendo. Iniciando..."
    sudo docker start trading_postgres
fi

if ! sudo docker ps | grep -q trading_redis; then
    echo "⚠️  Redis no está corriendo. Iniciando..."
    sudo docker start trading_redis
fi

echo "✅ Containers activos"

# 2. Mostrar instrucciones
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Para levantar el dashboard completo, ejecuta en TERMINALES SEPARADAS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "TERMINAL 1 - Backend (FastAPI):"
echo "  cd /home/gonza/Develop/algodetraiding"
echo "  source venv/bin/activate"
echo "  uvicorn api.main:app --reload --port 8000"
echo ""
echo "TERMINAL 2 - Frontend (React):"
echo "  cd /home/gonza/Develop/algodetraiding/web/frontend"
echo "  npm run dev"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 URLs:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Frontend:      http://localhost:3000"
echo "  Backend API:   http://localhost:8000"
echo "  Swagger Docs:  http://localhost:8000/docs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
