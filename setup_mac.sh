#!/bin/bash

# ============================================================================
# CUIDAR IA - Script de Instalación para MacBook Pro M2
# ============================================================================
# Este script instala todas las dependencias necesarias para el MVP
# Ejecutar en la terminal de VS Code
# ============================================================================

echo "🚀 Iniciando instalación de CUIDAR IA MVP"
echo "=========================================="
echo ""

# Verificar que estamos en Mac
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Este script es solo para macOS"
    exit 1
fi

echo "✅ Sistema operativo: macOS detectado"
echo ""

# ============================================================================
# PASO 1: Instalar Ollama (Modelo Local)
# ============================================================================
echo "📦 PASO 1: Instalando Ollama..."
echo "----------------------------------------"

if command -v ollama &> /dev/null; then
    echo "✅ Ollama ya está instalado"
else
    echo "⏳ Descargando e instalando Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    
    if [ $? -eq 0 ]; then
        echo "✅ Ollama instalado correctamente"
    else
        echo "❌ Error al instalar Ollama"
        exit 1
    fi
fi

echo ""
echo "⏳ Descargando modelo Llama 3.2 (optimizado para M2)..."
ollama pull llama3.2

if [ $? -eq 0 ]; then
    echo "✅ Modelo Llama 3.2 descargado correctamente"
else
    echo "⚠️  Advertencia: Error al descargar el modelo"
fi

echo ""
echo "📋 Modelos disponibles en Ollama:"
ollama list

echo ""

# ============================================================================
# PASO 2: Crear Entorno Virtual de Python
# ============================================================================
echo "🐍 PASO 2: Configurando entorno virtual de Python..."
echo "----------------------------------------"

# Verificar Python 3
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python detectado: $PYTHON_VERSION"
else
    echo "❌ Python 3 no encontrado. Instala Python 3.11+ desde python.org"
    exit 1
fi

# Crear entorno virtual
if [ -d "venv_cuidar" ]; then
    echo "⚠️  El entorno virtual ya existe"
    read -p "¿Deseas recrearlo? (s/n): " recrear
    if [ "$recrear" = "s" ]; then
        rm -rf venv_cuidar
        python3 -m venv venv_cuidar
        echo "✅ Entorno virtual recreado"
    fi
else
    python3 -m venv venv_cuidar
    echo "✅ Entorno virtual creado: venv_cuidar"
fi

# Activar entorno virtual
echo "⏳ Activando entorno virtual..."
source venv_cuidar/bin/activate

if [ $? -eq 0 ]; then
    echo "✅ Entorno virtual activado"
else
    echo "❌ Error al activar entorno virtual"
    exit 1
fi

echo ""

# ============================================================================
# PASO 3: Actualizar pip
# ============================================================================
echo "📦 PASO 3: Actualizando pip..."
echo "----------------------------------------"
python -m pip install --upgrade pip

if [ $? -eq 0 ]; then
    echo "✅ pip actualizado correctamente"
else
    echo "❌ Error al actualizar pip"
    exit 1
fi

echo ""

# ============================================================================
# PASO 4: Instalar Dependencias de Python
# ============================================================================
echo "📦 PASO 4: Instalando dependencias de Python..."
echo "----------------------------------------"
echo "⏳ Esto puede tomar varios minutos..."
echo ""

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        echo "✅ Todas las dependencias instaladas correctamente"
    else
        echo "❌ Error al instalar algunas dependencias"
        exit 1
    fi
else
    echo "❌ Archivo requirements.txt no encontrado"
    exit 1
fi

echo ""

# ============================================================================
# PASO 5: Configurar Jupyter Kernel
# ============================================================================
echo "📓 PASO 5: Configurando Jupyter Kernel..."
echo "----------------------------------------"

python -m ipykernel install --user --name=cuidar_ia --display-name "CUIDAR IA (Python 3)"

if [ $? -eq 0 ]; then
    echo "✅ Kernel de Jupyter configurado"
else
    echo "⚠️  Advertencia: Error al configurar kernel"
fi

echo ""

# ============================================================================
# PASO 6: Crear Estructura de Carpetas
# ============================================================================
echo "📁 PASO 6: Creando estructura de carpetas..."
echo "----------------------------------------"

mkdir -p data/pdf_papers
mkdir -p data/vectorstore
mkdir -p evaluaciones
mkdir -p reportes
mkdir -p logs

echo "✅ Estructura de carpetas creada:"
echo "   📂 data/pdf_papers/     - Para papers científicos"
echo "   📂 data/vectorstore/    - Base de datos vectorial"
echo "   📂 evaluaciones/        - Evaluaciones guardadas"
echo "   📂 reportes/            - Reportes PDF generados"
echo "   📂 logs/                - Logs del sistema"

echo ""

# ============================================================================
# PASO 7: Crear archivo .env
# ============================================================================
echo "🔑 PASO 7: Configurando archivo de variables de entorno..."
echo "----------------------------------------"

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Archivo .env creado"
    echo "⚠️  IMPORTANTE: Edita el archivo .env con tus API keys"
else
    echo "⚠️  El archivo .env ya existe (no se sobrescribió)"
fi

echo ""

# ============================================================================
# PASO 8: Verificar Instalación
# ============================================================================
echo "🔍 PASO 8: Verificando instalación..."
echo "----------------------------------------"

echo "Verificando librerías instaladas:"
python -c "import pandas; print('✅ pandas:', pandas.__version__)"
python -c "import langchain; print('✅ langchain:', langchain.__version__)"
python -c "import chromadb; print('✅ chromadb:', chromadb.__version__)"
python -c "import plotly; print('✅ plotly:', plotly.__version__)"
python -c "import streamlit; print('✅ streamlit:', streamlit.__version__)"

echo ""

# ============================================================================
# RESUMEN FINAL
# ============================================================================
echo ""
echo "=========================================="
echo "✨ INSTALACIÓN COMPLETADA ✨"
echo "=========================================="
echo ""
echo "📋 Resumen de lo instalado:"
echo "   ✅ Ollama con modelo Llama 3.2"
echo "   ✅ Entorno virtual Python (venv_cuidar)"
echo "   ✅ Todas las dependencias de Python"
echo "   ✅ Jupyter Kernel configurado"
echo "   ✅ Estructura de carpetas creada"
echo "   ✅ Archivo .env creado"
echo ""
echo "🚀 Próximos pasos:"
echo ""
echo "1. Activar el entorno virtual:"
echo "   source venv_cuidar/bin/activate"
echo ""
echo "2. Editar el archivo .env con tus API keys (si usarás APIs):"
echo "   code .env"
echo ""
echo "3. Abrir el notebook en VS Code:"
echo "   code CUIDAR_IA_MVP.ipynb"
echo ""
echo "4. Seleccionar el kernel 'CUIDAR IA (Python 3)' en VS Code"
echo ""
echo "5. Ejecutar las celdas del notebook"
echo ""
echo "📚 Para agregar papers científicos:"
echo "   - Copia tus PDFs a: data/pdf_papers/"
echo ""
echo "💡 Para iniciar Jupyter Notebook (alternativa):"
echo "   jupyter notebook CUIDAR_IA_MVP.ipynb"
echo ""
echo "=========================================="
echo "¡Listo para desarrollar CUIDAR IA! 🎉"
echo "=========================================="
