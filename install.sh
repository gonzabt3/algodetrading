#!/bin/bash
# Script de instalación rápida para el proyecto de trading algorítmico

echo "=================================="
echo "Trading Algorítmico - Instalación"
echo "=================================="
echo ""

# Verificar Python
echo "1. Verificando Python..."
if command -v python3 &> /dev/null
then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✓ $PYTHON_VERSION encontrado"
else
    echo "   ✗ Python3 no encontrado"
    echo "   Por favor instala Python 3.8 o superior"
    exit 1
fi

echo ""

# Verificar pip
echo "2. Verificando pip..."
if command -v pip3 &> /dev/null
then
    PIP_VERSION=$(pip3 --version)
    echo "   ✓ pip encontrado"
else
    echo "   ✗ pip no encontrado"
    echo "   Instalando pip..."
    echo "   Ejecuta: sudo apt install python3-pip (Ubuntu/Debian)"
    echo "   O: sudo dnf install python3-pip (Fedora)"
    exit 1
fi

echo ""

# Crear entorno virtual (opcional pero recomendado)
echo "3. ¿Deseas crear un entorno virtual? (recomendado) [s/N]"
read -r response
if [[ "$response" =~ ^([sS][iI]|[sS])$ ]]
then
    echo "   Creando entorno virtual..."
    python3 -m venv venv
    echo "   ✓ Entorno virtual creado"
    echo ""
    echo "   Activando entorno virtual..."
    source venv/bin/activate
    echo "   ✓ Entorno virtual activado"
fi

echo ""

# Instalar dependencias
echo "4. Instalando dependencias..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "   ✓ Dependencias instaladas correctamente"
else
    echo "   ✗ Error al instalar dependencias"
    echo "   Intenta: pip3 install --user -r requirements.txt"
    exit 1
fi

echo ""

# Verificar instalación
echo "5. Verificando instalación..."
python3 -c "import pandas, numpy, matplotlib" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "   ✓ Paquetes principales verificados"
else
    echo "   ✗ Error en la verificación"
    exit 1
fi

echo ""
echo "=================================="
echo "¡Instalación completada!"
echo "=================================="
echo ""
echo "Próximos pasos:"
echo "  1. Ejecuta el ejemplo: python3 example.py"
echo "  2. O prueba: python3 main.py --strategy ma_crossover --symbol BTC/USDT --days 30"
echo ""
echo "Para más información, consulta README.md"
echo ""
