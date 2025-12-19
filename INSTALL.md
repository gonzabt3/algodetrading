# Guía de Instalación Completa

## Paso 1: Instalar pip (si no está instalado)

### En Ubuntu/Debian:
```bash
sudo apt update
sudo apt install python3-pip
```

### En Fedora:
```bash
sudo dnf install python3-pip
```

### En macOS:
```bash
# Si tienes Homebrew instalado
brew install python3
```

### En Windows:
Python 3.8+ generalmente incluye pip. Si no:
- Descarga Python desde python.org
- Asegúrate de marcar "Add Python to PATH" durante la instalación

## Paso 2: Verificar la instalación

```bash
python3 --version
pip3 --version
```

## Paso 3: Instalar dependencias del proyecto

```bash
cd /home/gonza/Develop/algodetraiding
pip3 install -r requirements.txt
```

O para instalación de usuario (sin sudo):
```bash
pip3 install --user -r requirements.txt
```

## Paso 4: Verificar la instalación

```bash
python3 -c "import pandas; import numpy; import matplotlib; print('¡Dependencias instaladas correctamente!')"
```

## Paso 5: Ejecutar el ejemplo

```bash
# Ejemplo simple con datos sintéticos
python3 example.py

# O el programa principal (requiere conexión a internet)
python3 main.py --strategy ma_crossover --symbol BTC/USDT --days 30
```

## Solución de Problemas

### Error: "No module named 'ccxt'"
```bash
pip3 install ccxt
```

### Error: "No module named 'pandas'"
```bash
pip3 install pandas numpy matplotlib
```

### Permisos denegados
```bash
# Usar instalación de usuario
pip3 install --user -r requirements.txt
```

### Entorno virtual (recomendado)
```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
# En Linux/macOS:
source venv/bin/activate
# En Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## Configuración Adicional

### Para usar exchanges reales:

1. Edita `config/settings.py`
2. Agrega tus claves API (¡NUNCA las compartas!)
3. Comienza con pequeñas cantidades en modo de prueba

### Para desarrollo:

```bash
# Instalar herramientas de desarrollo
pip3 install pytest black flake8

# Ejecutar tests
pytest tests/

# Formatear código
black .

# Verificar estilo
flake8 .
```

## Recursos

- Documentación de Python: https://docs.python.org/3/
- Tutorial de pip: https://pip.pypa.io/en/stable/getting-started/
- CCXT Documentation: https://docs.ccxt.com/
- Pandas Docs: https://pandas.pydata.org/docs/
