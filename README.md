# Agente de Monitoreo del Boletín Oficial

Este proyecto implementa un Agente de Inteligencia Artificial utilizando **Google Agent Development Kit (ADK)** y el modelo **Gemini 2.0 Flash**. Su objetivo es asistir en el análisis y monitoreo de archivos PDF del Boletín Oficial, identificando temas específicos de interés definidos en una hoja de cálculo.

## 🚀 Descripción del Proyecto

El agente actúa como un analista especializado que:
1.  **Carga y Analiza** documentos PDF (Boletín Oficial).
2.  **Monitorea** una lista de "Temas de Interés" definidos en un archivo Excel (`.xlsx`).
3.  **Responde** consultas del usuario en dos modos:
    *   **Modo Estricto (JSON)**: Cuando la consulta coincide con un tema de monitoreo, devuelve información estructurada (Tema, Resumen, Página) citando las fuentes.
    *   **Modo General (Conversacional)**: Cuando la consulta es genérica (fechas, resumen general), responde en lenguaje natural basado en el contenido del PDF.

## 🛠️ Estructura del Proyecto

```text
Boletin/
├── .env.example          # Plantilla de variables de entorno (API Keys)
├── .gitignore            # Archivos ignorados por Git
├── README.md             # Documentación del proyecto
├── requirements.txt      # Dependencias de Python
├── Sources/              # Carpeta para documentos de entrada (.pdf, .xlsx)
│   └── README.md         # Guía de formatos esperados en Sources
└── src/                  # Código fuente
    ├── agent.py          # Lógica principal del Agente (ADK Wrapper)
    ├── loader.py         # Módulos para cargar PDF y Excel
    ├── main.py           # Punto de entrada (CLI Asíncrono)
    └── scorer.py         # Lógica de puntaje para ruteo (Strict vs General)
```

## ⚙️ Requisitos e Instalación

1.  **Python 3.10+** instalado.
2.  Crear entorno virtual:
    ```bash
    python -m venv venv
    .\venv\Scripts\Activate  # Windows
    ```
3.  Instalar dependencias:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configurar **.env**:
    Copiar la plantilla `.env.example` como `.env` y configurar tu API Key de Google Gemini:
    ```bash
    copy .env.example .env
    ```
    Y dentro de `.env`:
    ```text
    GOOGLE_API_KEY=tu_api_key_aqui
    ```
5.  **Cargar documentos en `Sources/`**:
    Colocar los PDFs del Boletín Oficial y el archivo `Temas de interes para monitorear.xlsx` dentro de la carpeta `Sources/` (esta carpeta se encuentra ignorada en Git para no versionar documentos pesados).

## ▶️ Ejecución

Para iniciar el agente en modo consola:

```powershell
.\venv\Scripts\python src\main.py
```

El sistema cargará los PDFs (puede tardar unos segundos dependiendo del tamaño) y quedará listo para recibir preguntas.

## 🤖 Funcionamiento Interno

### Arquitectura
*   **Modelo**: Gemini 2.0 Flash (Optimizado para velocidad y ventanas de contexto de 1M tokens).
*   **Framework**: Google ADK (Agent Development Kit).
*   **Gestión de Contexto**: El contenido de los PDFs (~160k tokens) se inyecta en la **Instrucción del Sistema** (System Prompt) al inicio. Esto evita re-enviar el texto completo en cada turno, previniendo errores de límite de tokens.

### Routing (Enrutamiento)
El agente decide cómo responder basándose en un sistema de puntaje (`scorer.py`):
*   Si la pregunta contiene palabras clave del Excel (ej: "SIRADIG", "Resolución General"): **Score Alto (>=4)** -> **Modo Estricto**.
*   Si la pregunta es genérica: **Score Bajo** -> **Modo General**.

## 🧪 Set de Preguntas de Prueba

Para validar el funcionamiento, puedes usar estas preguntas:

### Preguntas de Monitoreo (Modo Estricto)
*   *"¿Hay alguna información sobre SIRADIG?"*
*   *"¿Qué dice el boletín acerca de Fiscalización Digital?"*
*   *"¿Se menciona algo sobre el 'Aplicativo Ganancias Ajuste por Inflación'?"*
*   *"Buscame novedades sobre el 'Régimen de Retención y Percepción'."*
*   *"Listame las resoluciones generales de la jurisdicción Nacional."*

### Preguntas Generales (Modo Conversacional)
*   *"¿Cuál es la fecha de publicación de este boletín?"*
*   *"¿Cuántas páginas tiene el documento en total?"*
*   *"Hacé un resumen breve de la Primera Sección"*

## 📝 Logs y Depuración

Todas las interacciones se guardan automáticamente en `interaction_logs.jsonl`. Cada línea es un objeto JSON con:
*   Timestamp
*   Query del usuario
*   Score calculado
*   Modo de routing (STRICT/GENERAL)
*   Respuesta del agente
*   Errores (si los hubo)

---
**Nota**: Para salir del agente escribe `exit` o presiona `Ctrl+C`.
## 🚧 Pendientes de Desarrollo y Cómo Llevarlos a Cabo

1. **Ingesta Automatizada Diaria (Scraper / RSS)**:
   - *Objetivo*: Descargar automáticamente los nuevos ejemplares del Boletín Oficial publicados cada medianoche sin requerir carga manual de archivos.
   - *Procedimiento*:
     - Crear un job programado (`src/ingestion_job.py`) que consulte el sitio oficial del Boletín Oficial o su feed RSS.
     - Descargar el PDF de la Primera Sección y ubicarlo en la carpeta `Sources/`.
     - Actualizar la fecha de procesamiento en `state.json`.

2. **OCR Avanzado y Extracción de Tablas Complejas (Document AI)**:
   - *Objetivo*: Procesar anexos escaneados, resoluciones tarifarias o tablas complejas que la extracción directa de texto no recupera adecuadamente.
   - *Procedimiento*:
     - En `src/loader.py`, incorporar un fallback a Google Cloud Document AI cuando la extracción de texto arroje baja densidad o páginas escaneadas.
     - Normalizar el texto y tablas antes de calcular los puntajes de coincidencia.

3. **Sistema de Alertas Proactivas (Webex Teams / Correo Corporativo)**:
   - *Objetivo*: Notificar de forma inmediata a los equipos de auditoría y legales cuando se identifique una normativa crítica con Score Alto (>=4).
   - *Procedimiento*:
     - Agregar un módulo `src/notifications.py` configurable en `.env` con Webhooks de Webex o SMTP.
     - Emitir la ficha JSON estructurada con el resumen ejecutivo y la página citada.

4. **Exposición como API Microservicio y Despliegue en Cloud Run**:
   - *Objetivo*: Permitir que otros sistemas de la organización consulten el agente de forma programática.
   - *Procedimiento*:
     - Exponer `src/agent.py` mediante endpoints FastAPI (`POST /analyze`, `POST /chat`).
     - Empaquetar con `Dockerfile` y desplegar en Cloud Run asegurando credenciales vía Google Secret Manager.
