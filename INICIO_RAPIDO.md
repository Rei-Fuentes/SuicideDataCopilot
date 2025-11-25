# 🚀 Guía de Inicio Rápido - CUIDAR IA

## ⚡ Empieza en 5 minutos

---

## 📋 Pre-requisitos

Asegúrate de tener:
- ✅ MacBook Pro M2 (o superior)
- ✅ macOS Sequoia 15.3 (o compatible)
- ✅ VS Code instalado
- ✅ Python 3.11+ instalado

---

## 🎯 Instalación en 3 Pasos

### Paso 1: Descargar el Proyecto

```bash
# Navega a tu carpeta de proyectos
cd ~/Documents/proyectos

# (Si tienes el proyecto en una carpeta, navega a ella)
cd cuidar-ia
```

### Paso 2: Ejecutar Instalación Automática

```bash
# Dar permisos al script
chmod +x setup_mac.sh

# Ejecutar instalación (toma 5-10 minutos)
./setup_mac.sh
```

**Toma un café ☕ mientras se instala todo automáticamente**

### Paso 3: Activar Entorno y Abrir Notebook

```bash
# Activar entorno virtual
source venv_cuidar/bin/activate

# Abrir VS Code
code .
```

**En VS Code:**
1. Abre el archivo: `CUIDAR_IA_MVP.ipynb`
2. Selecciona el kernel: **"CUIDAR IA (Python 3)"**
3. Ejecuta la primera celda: `Shift + Enter`

---

## 🎓 Tu Primera Evaluación

### Ejecuta las celdas en orden:

**Celda 1:** Importar librerías
```python
# Se cargan pandas, plotly, etc.
✅ Verás: "Librerías básicas cargadas correctamente"
```

**Celda 2:** Definir estructura del cuestionario
```python
# Se define el CUIDAR Index con 22 ítems
✅ Verás: "Estructura del cuestionario CUIDAR definida"
```

**Celda 3:** Crear clases de gestión
```python
# Clases para evaluaciones
✅ Verás: "Clases de gestión de evaluaciones creadas"
```

**Celda 4:** Funciones de visualización
```python
# Gráficos radar, gauge, etc.
✅ Verás: "Funciones de visualización creadas"
```

**Celda 5:** Ejemplo de evaluación
```python
# Simulación completa con resultados
✅ Verás un informe completo con:
   - Puntaje total
   - Nivel de madurez
   - Brechas identificadas
   - Fortalezas
```

**Celda 6:** Visualizaciones
```python
# Gráficos interactivos
✅ Verás 3 gráficos:
   - Radar por dimensiones
   - Gauge de madurez
   - Análisis de brechas
```

---

## 🎨 Personaliza tu Evaluación

### Cambia los datos de ejemplo:

```python
# En la Celda 5, modifica:

evaluacion_ejemplo = EvaluacionCUIDAR(
    respondiente_tipo='A',
    municipio='TU_MUNICIPIO',  # ← Cambia aquí
    respondiente_nombre='TU_NOMBRE'  # ← Cambia aquí
)

# Modifica las respuestas (escala 1-5):
respuestas_ejemplo = {
    'ACC_1': 3,  # ← Cambia los números
    'ACC_2': 2,
    # ... etc
}
```

### Escala Likert:
- **1** = Ausente / Nunca
- **2** = Muy incipiente / Rara vez
- **3** = Parcialmente / A veces
- **4** = Bueno / Casi siempre
- **5** = Completo / Siempre

---

## 📊 Interpretando Resultados

### Niveles de Madurez:

| Puntaje | Nivel | Descripción |
|---------|-------|-------------|
| 0-25 | 🔴 **Inicial** | Sin capacidad real |
| 26-50 | 🟠 **Básico** | Fragmentado, datos parciales |
| 51-75 | 🔵 **Intermedio** | Funcional pero con brechas |
| 76-100 | 🟢 **Avanzado** | Uso sistemático de datos |

### Brechas y Fortalezas:

- **Brechas** (< 50): Áreas prioritarias de mejora
- **Fortalezas** (≥ 75): Capacidades destacadas

---

## 🔄 Sistema Multi-usuario

Para triangular respuestas de 3 respondientes:

```python
# Ejecuta la Celda 7 del notebook
# Verás comparación entre respondientes A, B, C
# Y detección de discrepancias
```

**Respondientes recomendados:**
- **A**: Coordinador de prevención del suicidio
- **B**: Responsable técnico de datos
- **C**: Jefe de salud municipal

---

## 💾 Guardar tu Evaluación

```python
# Al final del notebook (Celda 8):
exportar_evaluacion_json(evaluacion_ejemplo)

# Se guarda en:
# evaluaciones/TuMunicipio_A_20251110_1430.json
```

---

## 🤖 Próximos Pasos (Fases Futuras)

Una vez domines el notebook básico:

### FASE 2: Agregar Papers Científicos (RAG)
```bash
# Copia tus PDFs:
cp tus_papers/*.pdf data/pdf_papers/
```

### FASE 3: Configurar IA para Recomendaciones
```bash
# Opción 1: Usar Ollama (gratis, local)
# Ya está listo!

# Opción 2: Usar Anthropic Claude (pago)
# Edita .env con tu API key
code .env
```

Ver: [CONFIGURACION_API_KEYS.md](CONFIGURACION_API_KEYS.md)

---

## 🆘 Problemas Comunes

### ❌ Error: "Module not found"
```bash
# Asegúrate de activar el entorno:
source venv_cuidar/bin/activate

# Reinstala dependencias:
pip install -r requirements.txt
```

### ❌ Error: "Kernel not found"
```bash
# Reinstala el kernel:
python -m ipykernel install --user --name=cuidar_ia
```

### ❌ Ollama no funciona
```bash
# Verifica instalación:
ollama list

# Descarga el modelo:
ollama pull llama3.2
```

### ❌ Gráficos no se muestran
```bash
# Reinstala plotly:
pip install --upgrade plotly
```

---

## 📚 Recursos Adicionales

- **README completo**: [README.md](README.md)
- **Configuración APIs**: [CONFIGURACION_API_KEYS.md](CONFIGURACION_API_KEYS.md)
- **Notebook principal**: `CUIDAR_IA_MVP.ipynb`

---

## 💬 Comandos Útiles

```bash
# Activar entorno
source venv_cuidar/bin/activate

# Desactivar entorno
deactivate

# Abrir notebook en Jupyter
jupyter notebook CUIDAR_IA_MVP.ipynb

# Abrir notebook en VS Code
code CUIDAR_IA_MVP.ipynb

# Ver librerías instaladas
pip list

# Actualizar librerías
pip install --upgrade -r requirements.txt
```

---

## ✅ Checklist de Validación

Verifica que todo funciona:

- [ ] ✅ Script de instalación ejecutado sin errores
- [ ] ✅ Entorno virtual activado
- [ ] ✅ Notebook abre en VS Code
- [ ] ✅ Kernel "CUIDAR IA" seleccionado
- [ ] ✅ Celda 1 ejecuta sin errores
- [ ] ✅ Celda 5 muestra resultados de evaluación
- [ ] ✅ Celda 6 muestra gráficos interactivos
- [ ] ✅ Ollama instalado y funcionando
- [ ] ✅ Evaluación se exporta a JSON correctamente

---

## 🎉 ¡Listo!

Ya tienes CUIDAR IA funcionando. 

**Ahora puedes:**
1. Experimentar con diferentes puntajes
2. Probar el sistema multi-usuario
3. Prepararte para la FASE 2 (RAG)

**Próximo paso:** Conseguir papers científicos en PDF sobre prevención del suicidio para alimentar el RAG.

---

**¿Preguntas? Revisa el README.md completo o los logs en `logs/`**

¡Éxito con tu postulación a IAtecUV! 🚀
