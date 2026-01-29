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
├── .env                  # Variables de entorno (API Keys) - NO COMPARTIR
├── .gitignore            # Archivos ignorados por Git
├── interaction_logs.jsonl # Log de todas las interacciones (historial)
├── README.md             # Documentación del proyecto
├── requirements.txt      # Dependencias de Python
├── Sources/              # Carpeta de entrada de datos
│   ├── Primera.pdf       # Archivo PDF a analizar
│   ├── Segunda.pdf       # Archivo PDF a analizar
│   └── Temas de interes para monitorear.xlsx  # Lineamientos
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
    Crea un archivo `.env` en la raíz con tu API Key de Google:
    ```text
    GOOGLE_API_KEY=tu_api_key_aqui
    ```

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
