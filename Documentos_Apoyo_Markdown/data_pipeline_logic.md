# Lógica del Pipeline de Datos (eBird + OpenAQ)

Este documento detalla el procedimiento técnico y matemático con el cual las bases crudas de aves y de calidad del aire se fusionaron para generar el dataset de ocupación (`copeton_occupancy_ready.csv`).

## 1. La Filosofía del Cruce (Spatio-Temporal Join)

El desafío principal del proyecto era unir dos universos inconexos:
1.  **Observaciones Puntuadas (eBird)**: Tienen Latitud y Longitud exacta de un pajarero, en un día y una hora específica, observando la presencia/ausencia de especies.
2.  **Sensores Fijos (RMCAB/OpenAQ)**: Tienen Latitud y Longitud estáticas, y arrojan un promedio de gases (`co_ppm`, `no2_ppb`, etc.) y material particulado (`pm10`, `pm25`) cada hora cronológica en punto.

### ¿Cómo se resolvió matemáticamente?
El script `02_data_processing/cross_join_birds_pollution.py` realiza dos uniones críticas:

#### A. Emparejamiento Temporal
Si un pajarero en eBird anota que su observación empezó a las `07:15 AM` o `07:45 AM`, es imposible hallar un empate perfecto con OpenAQ, ya que esta base agrupa datos por "la hora 7:00". 
-   **Resolución**: Se aplicó una técnica de *redondeo hacia la hora más cercana*. `07:15` se asocia con el bloque de contaminación de las `07:00`, y `07:45` salta a las `08:00`.
-   **Supuesto Principal**: El nivel de contaminación reportado por la estación durante toda esa hora es representativo de la fracción de tiempo exacta en que el ave y el pajarero estuvieron respirándolo en el sitio.

#### B. Emparejamiento Espacial (Fórmula de Haversine)
Un pajarero puede estar en cualquier parque de Bogotá (ej: Parque Simón Bolívar). 
-   **Resolución**: El script calcula la distancia en línea recta (usando la trigonometría esférica de *Haversine* en la Tierra) entre la latitud/longitud del pajarero y **todas** las 19 estaciones de la RMCAB. 
-   **Matching**: El script asigna a ese avistamiento los datos de contaminación exclusiva de la estación de aire cuya distancia en Kilómetros (columna `distance_km`) haya sido la menor de todas. 

---

## 2. Supuestos Críticos del Modelo

Para que el modelo Bayesiano de Ocupación interpreté esto válidamente, estamos confiando implícitamente en:

1.  **Homogeneidad Espacial del Aire (Buffer Zone)**: Asumimos que los gases/partículas medidas por una estación fija cubren de manera idéntica los alrededores en un radio de `X` kilómetros. (Por ejemplo, si la estación "MinAmbiente" detecta humo, asumimos que un Copetón a 3 km de distancia también está respirando niveles equivalentes de humo).
2.  **Cierre Geográfico Temporal (Closure Assumption)**: En modelos de ocupación jerárquicos (MacKenzie et al.), asumimos que *durante el bloque de la temporada* (por ejemplo, entre junio y julio), la población del sitio está "cerrada" a grandes migraciones. Si el ave ocupaba el Parque El Lago, permaneció en su capacidad de ocuparlo, y su no-detección es pura falla del observador ($p$) o efecto agudo de que ese día había polución ($\psi$).

---

## 3. Problemas Potenciales (Caveats) a tener en cuenta

Cuando corras las cadenas MCMC (Markov Chain Monte Carlo), podrías enfrentarte a estos problemas heredados de la base de datos:

1.  **Distancias de Emparejamiento Extremas:** Si observas la columna `distance_km`, el máximo cruce forzado llega a los **26 kilómetros** (generalmente para pajareros en las montañas orientales extremas pero a los que se les asignó una estación urbana central por falta de cobertura periférica de la red RMCAB). 
    *   *Solución futura*: Podrías filtrar el dataset (ej: `df[df['distance_km'] < 5.0]`) limitando el modelo solo a observaciones estrictamente urbanas que ocurrieron muy cerca (a 5 km máximo) de una estación real, para no violar el supuesto de homogeneidad.
2.  **Ausencias Biológicas vs. Ausencias Matemáticas**: Si un pajarero no anota un ave en eBird, ¿significa que no estaba? En nuestro script de preparación, forzaste a quedarse solo con *"Listas Completas"* (`ALL SPECIES REPORTED == 1`). Esto es biológicamente **excelente**, ya que sabemos sin duda que la ausencia del Copetón no fue un error por omisión deliberada, sino real (y es vital para ajustar la detección ($p$)).
3.  **Brechas Temporales de Estaciones (Missing Completely at Random)**: Sensores estropeados generaron nulos. Si corres un modelo Bayesiano sin imputar bien, las cadenas colapsarán por los NA en CO o NO2. (Este problema requerirá o ignorar esos gases, o probar diferentes tipos de imputaciones que consideren la autocorrelación horaria).
