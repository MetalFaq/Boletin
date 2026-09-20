# Carpeta de Entrada de Fuentes (Sources)

Esta carpeta almacena los documentos de entrada que el agente analiza.
Por motivos de privacidad y tamaño, los archivos binarios (.pdf y .xlsx) están ignorados en el control de versiones (.gitignore).

### Archivos esperados:
1. **Documentos PDF**: Uno o más archivos `.pdf` (por ejemplo, `Primera.pdf`, `Segunda.pdf`) correspondientes a las ediciones del Boletín Oficial.
2. **Matriz de Monitoreo (`Temas de interes para monitorear.xlsx`)**: Archivo Excel con las siguientes columnas recomendadas:
   - `Título` (e.g. SIRADIG, Régimen de Retención)
   - `Subtítulo`
   - `Tipo de Norma` (e.g. Resolución General, Decreto)
   - `Jurisdicción` (e.g. Nacional, Provincial)
