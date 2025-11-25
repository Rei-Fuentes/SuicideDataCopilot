# 🔑 Guía de Configuración de API Keys

## CUIDAR IA - Configuración de Proveedores de IA

---

## 📋 Opciones Disponibles

Tienes 3 opciones para usar IA en CUIDAR IA:

### 1. **Ollama (Local - GRATIS)** ⭐ Recomendado para desarrollo
- ✅ Completamente gratis
- ✅ Privacidad total (datos no salen de tu Mac)
- ✅ Ideal para desarrollo y pruebas
- ✅ Ya instalado con el script setup
- ⚠️ Menos potente que APIs comerciales

### 2. **Anthropic Claude (API - PAGO)** ⭐ Recomendado para producción
- ✅ Mejor calidad para análisis contextual
- ✅ Excelente para textos científicos
- ✅ Explicabilidad superior
- 💰 ~$0.003 por recomendación (~$3 por 1000 evaluaciones)
- 🌐 Requiere conexión a internet

### 3. **OpenAI GPT-4 (API - PAGO)**
- ✅ Alta calidad
- ✅ Ampliamente usado
- 💰 ~$0.01 por recomendación (~$10 por 1000 evaluaciones)
- 🌐 Requiere conexión a internet

---

## 🚀 Configuración Paso a Paso

### Opción 1: Usar Ollama (Local - Sin API keys)

Ya está listo! Solo asegúrate de que Ollama esté corriendo:

```bash
# Verificar que Ollama está corriendo
ollama list

# Si no está corriendo, iniciarlo
ollama serve
```

En tu archivo `.env`:
```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
```

✅ ¡Listo para usar!

---

### Opción 2: Configurar Anthropic Claude (Recomendado)

#### Paso 1: Crear cuenta en Anthropic
1. Ve a: https://console.anthropic.com
2. Crea una cuenta con tu email
3. Verifica tu email

#### Paso 2: Obtener API Key
1. Una vez en el dashboard, ve a "API Keys"
2. Click en "Create Key"
3. Dale un nombre: "CUIDAR_IA_Development"
4. Copia la key (empieza con `sk-ant-...`)

#### Paso 3: Configurar créditos
1. Ve a "Billing" en el dashboard
2. Agrega una tarjeta de crédito
3. Anthropic cobra solo por uso real
4. Precio: ~$3 por 1M tokens de entrada (~0.003 por recomendación)

#### Paso 4: Configurar en .env
Edita tu archivo `.env`:

```env
# Configurar Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-tu_api_key_aqui
LLM_PROVIDER=anthropic
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

#### Verificar que funciona:
```python
from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=100,
    messages=[{"role": "user", "content": "Hola, ¿funcionas?"}]
)
print(message.content[0].text)
```

✅ Si ves una respuesta, está funcionando!

---

### Opción 3: Configurar OpenAI

#### Paso 1: Crear cuenta en OpenAI
1. Ve a: https://platform.openai.com
2. Crea una cuenta
3. Verifica tu email

#### Paso 2: Obtener API Key
1. Ve al dashboard: https://platform.openai.com/api-keys
2. Click en "Create new secret key"
3. Dale un nombre: "CUIDAR_IA"
4. Copia la key (empieza con `sk-...`)

#### Paso 3: Configurar créditos
- Cuentas nuevas tienen $5 de crédito gratis
- Después necesitas agregar tarjeta
- Precio: ~$10 por 1M tokens de entrada

#### Paso 4: Configurar en .env
```env
# Configurar OpenAI
OPENAI_API_KEY=sk-tu_api_key_aqui
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4-turbo-preview
```

#### Verificar que funciona:
```python
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[{"role": "user", "content": "Hola, ¿funcionas?"}],
    max_tokens=100
)
print(response.choices[0].message.content)
```

✅ Si ves una respuesta, está funcionando!

---

## 🔄 Estrategia Híbrida Recomendada

Para optimizar costos y desarrollo:

**Durante Desarrollo:**
```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
```

**Para Demos/Producción:**
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=tu_key
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

**Cambiar entre proveedores:**
Solo necesitas cambiar el valor de `LLM_PROVIDER` en `.env`

---

## 💰 Estimación de Costos

### Para el MVP de CUIDAR IA:

**Anthropic Claude (Recomendado):**
- Costo por evaluación: ~$0.003
- 100 evaluaciones: ~$0.30
- 1,000 evaluaciones: ~$3.00
- 10,000 evaluaciones: ~$30.00

**OpenAI GPT-4:**
- Costo por evaluación: ~$0.01
- 100 evaluaciones: ~$1.00
- 1,000 evaluaciones: ~$10.00
- 10,000 evaluaciones: ~$100.00

**Ollama (Local):**
- Costo: $0 (GRATIS)
- Ilimitado

---

## ⚠️ Seguridad de API Keys

### ❌ NUNCA hagas esto:
- Subir tu `.env` a GitHub
- Compartir tus API keys públicamente
- Hardcodear keys en el código

### ✅ SIEMPRE haz esto:
- Mantén `.env` en `.gitignore`
- Usa variables de entorno
- Regenera keys si se exponen
- Monitorea el uso en los dashboards

---

## 🔧 Troubleshooting

### Error: "API key not found"
```bash
# Verificar que el archivo .env existe
ls -la .env

# Verificar que las variables se cargan
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('ANTHROPIC_API_KEY'))"
```

### Error: "Rate limit exceeded"
- Has excedido el límite de requests
- Espera unos minutos o actualiza tu plan

### Error: "Invalid API key"
- Verifica que copiaste la key completa
- Regenera la key en el dashboard
- Verifica que no hay espacios extra

---

## 📊 Monitoreo de Uso

### Anthropic:
- Dashboard: https://console.anthropic.com
- Ve a "Usage" para ver tu consumo

### OpenAI:
- Dashboard: https://platform.openai.com/usage
- Gráficos detallados de uso

---

## 🎯 Recomendación Final

Para tu MVP de CUIDAR IA:

1. **Empieza con Ollama** (gratis) para desarrollar
2. **Cuando tengas el RAG listo**, prueba con Anthropic
3. **Para la demo de IAtecUV**, usa Anthropic Claude
4. **Presupuesto inicial**: $10-20 es suficiente para el MVP

---

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs en `logs/`
2. Verifica las variables de entorno
3. Consulta la documentación oficial:
   - Anthropic: https://docs.anthropic.com
   - OpenAI: https://platform.openai.com/docs
   - Ollama: https://ollama.com/docs

---

**¡Listo para usar IA en CUIDAR IA! 🚀**
