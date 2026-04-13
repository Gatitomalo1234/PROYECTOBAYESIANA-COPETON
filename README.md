# Proyecto: Modelo de Ocupación Bayesiano para Aves en Bogotá

Este proyecto tiene como objetivo estimar la probabilidad de ocupación y detección de especies de aves urbanas en Bogotá, Colombia, en relación con los niveles de contaminación del aire. Utilizamos datos de avistamientos de **eBird** y mediciones de calidad del aire de la **Red de Monitoreo de Calidad del Aire de Bogotá (RMCAB)** a través de la API de **OpenAQ**.

## Objetivos
1.  **Adquisición de Datos**: Descargar mediciones horarias históricas **(2021-2026)** de contaminantes clave (PM2.5, PM10, O3, NO2, CO, SO2) para las estaciones de monitoreo operativas en Bogotá.
2.  **Integración de Datos**: Cruzar los avistamientos de aves de eBird con la estación de monitoreo más cercana, considerando la fecha y hora exacta del registro.
3.  **Modelado Bayesiano**: Implementar un modelo de ocupación jerárquico siguiendo la metodología de **Clark (2019)**, utilizando un enlace logit y variables latentes de Pólya-Gamma para una inferencia eficiente.

## Estructura del Proyecto
- 📂 `data/`: Contiene los datasets de contaminación y observación de aves.
  - `birds_pollution_merged.csv`: **Dataset consolidado** para el modelo (Aves + Contaminación).
  - `copeton_occupancy_ready.csv`: Base estructurada para el modelo de ocupación del Copetón.
  - `bogota_pollution_hourly.csv`: *(Excluido de Git por tamaño)* Datos horarios limpios expandidos **(2021-2026)**.
  - `bogota_stations_coords.csv`: Ubicación de las 19 estaciones.
- 📂 `scripts/`: Scripts de Python para procesamiento.
  - `prepare_occupancy_data.py`: Prepara la matriz de historial de detección.
  - `cross_join_birds_pollution.py`: Script de cruce espacial y temporal.
  - `fetch_bogota_pollution_hourly.py`: Descarga de datos de OpenAQ.
- 📂 `eda_copeton/`: Análisis Específico para el modelo del Copetón.
  - `copeton_report.md`: Hallazgos sobre el dataset final (910 listas).
  - `plots/`: Visualizaciones de balance de clases y por estación.
- 📂 `Documentos_Apoyo_Markdown/`: Informes técnicos y notas.
  - `bayesian_model_logic.md`: Explicación matemática del modelo.
  - `data_pipeline_logic.md`: Lógica del cruce de bases.
  - `next_steps.md`: Notas de avance iterativo.
  - `copeton_report.md`: Copia de los hallazgos de métricas Bayesianas.
- 📂 `GUIA_proyecto/PDFs/`: Carpeta centralizada que consolida todos los formatos .pdf de literatura y guías (como Clark 2019).

## Proceso de Destilación de Datos (Control de Calidad)

Es normal observar una reducción drástica desde la base cruda hasta el dataset final. Esto no es una pérdida de información, sino una **destilación de alta fidelidad** basada en rigor científico:

| Etapa | Registros / Eventos | Razón del Filtrado |
| :--- | :--- | :--- |
| **1. Datos Crudos (eBird)** | ~2,500,000 filas | Base total histórica para Cundinamarca. |
| **2. Match RMCAB (2021-2026)** | **17,247 filas** | Solo registros con match de estación y hora exacta. |
| **3. Eventos Únicos (Listas)** | **1,072 eventos** | Colapso de especies en unidades de muestreo únicas. |
| **4. Dataset Final (Modelo)** | **910 listas** | Filtro de **Listas Completas** (para ausencias reales). |

> [!IMPORTANT]
> Este proceso asegura que el modelo aprenda de datos donde la ausencia del ave es una **ausencia científica** y no un descuido del observador.

## Diccionario de Variables (Dataset Consolidado)

| Variable | Descripción | Rol en el Modelo |
| :--- | :--- | :--- |
| **`y_copeton`** | Detección (1) o Ausencia inferida (0). | Variable dependiente ($y$) |
| **`co_ppm`, `no2_ppb`, `o3_ppb`** | Contaminantes gaseosos. | Covariables de Ocupación ($\psi$) |
| **`pm10_ugm3`, `pm25_ugm3`** | Material particulado. | Covariables de Ocupación ($\psi$) |
| **`DURATION MINUTES`** | Tiempo de observación. | Covariable de Detección ($p$) |
| **`EFFORT DISTANCE KM`** | Distancia recorrida. | Covariable de Detección ($p$) |
| **`NUMBER OBSERVERS`** | Cantidad de personas. | Covariable de Detección ($p$) |
| **`PROTOCOL NAME`** | Tipo de censo (Traveling/Stationary). | Covariable de Detección ($p$) |
| **`month`** | Mes del año. | Estacionalidad ($\psi/p$) |

## Análisis Específico: Zonotrichia capensis (Copetón)

El dataset final para el modelo (`copeton_occupancy_ready.csv`) fue validado mediante un EDA específico que arrojó:
- **Balance de Clases**: 76% presencias / 24% ausencias (ideal para Bayesiana).
- **Estaciones con más datos**: Bolivia y MinAmbiente.
- **Calidad**: 0 nulos y 0 duplicados tras el proceso de destilación.

Para más detalle, ver el [Informe EDA Copetón](file:///c:/Users/Miguel%20Camargo/Desktop/Proyecto_Bayesiana/eda_copeton/copeton_report.md).

## Opciones de Avances y Actualizaciones (Historial)

**Sesión Anterior & Actual (Abril 2026): Data Augmentation y Metodología**
- **Metodología (Documentación):** Se re-escribió el Taller 04 (`taller_04.tex`) para asegurar un lenguaje académico, sencillo y reproducible, enfatizando la solicitud formal de datos a eBird.
- **Refactorización del Extractor (`fetch_bogota...`):** Se migró el script a la línea de comandos usando `argparse` para permitir descargas interactivas por rango de fechas interrumplibles.
- **Resiliencia API:** Se logró el manejo explícito de errores HTTP 429 *(Rate Limit)* de OpenAQ, incorporando pausas dinámicas de 60 segundos y evitando cortes de script.
- **Inyección Temporal Estructurada:** Se descargaron exitosamente más de 270,000 datos horarios desde 2022 hasta Abril de 2026. 
- **Recuperación del N Estadístico:** Ante la drástica caída de muestra, se recuperó estratégicamente el histórico del 2021 para recuperar la robustez estadística, obteniendo finalmente una muestra validada de **910 eventos completos**.
- **Reorganización Estructural:** Se introdujeron centralizaciones de información moviendo guías en PDF a `GUIA_proyecto/PDFs/` y el inventario de reportes MarkDown a `Documentos_Apoyo_Markdown/`.

---
*Desarrollado para el Proyecto de Bayesiana - 2026*
