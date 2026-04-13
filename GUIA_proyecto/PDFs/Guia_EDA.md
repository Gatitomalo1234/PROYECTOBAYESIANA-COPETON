# Bitácora de Análisis: Clustering de Actividad Sísmica en Colombia

## Fase 1: Business Understanding (Comprensión del Negocio)

**Pregunta de investigación:** ¿Es posible identificar automáticamente zonas sísmicas diferenciadas en Colombia utilizando únicamente las características instrumentales de los sismos?

### 1. Definición del problema y Propuesta de Valor
El Servicio Geológico Colombiano (SGC) monitorea miles de sismos anualmente, pero enfrenta un problema crónico de **asignación de recursos (Resource Allocation)**. Instalar y mantener sensores sismológicos de banda ancha es excesivamente costoso. Históricamente, estas estaciones se ubican donde "siempre ha temblado" o cerca de grandes ciudades por prevención política.

**Nuestra propuesta de valor:** El problema no es saber *que* tiembla, sino *dónde* invertir para medir mejor la amenaza real. Utilizando clustering no supervisado, no buscaremos "manchas" en el mapa, sino los **Centroides Matemáticos Reales** de liberación de energía sísmica. Le entregaremos al SGC las coordenadas 3D exactas de los "corazones" tectónicos de Colombia. La directriz de negocio es: *"Si ubicas tus sensores más precisos e inviertes el 80% de tu presupuesto en un radio de 10km de nuestros centroides matemáticos, capturarás la mayor cantidad de energía liberada del país optimizando drásticamente tu presupuesto de monitoreo"*.

### 2. Por qué el clustering es apropiado (y no aprendizaje supervisado)
El clustering es la técnica idónea porque **no tenemos datos etiquetados**. El catálogo sísmico del USGS no incluye una variable que nos diga "este sismo pertenece a la zona sísmica A" o "pertenece a la falla B". Si tuviéramos esas etiquetas, usaríamos clasificación (aprendizaje supervisado) para predecir a qué zona entra un sismo futuro. Al carecer de ellas, necesitamos un algoritmo no supervisado (K-Means) que agrupe los eventos midiendo qué tan "cerca" o similares son entre sí en términos físicos y geográficos.

### 3. Stakeholders (Usuarios y Uso de los Resultados)
*Observación Crítica:* Los geólogos del SGC y los expertos territoriales **ya conocen empíricamente** la sismicidad del país. Nuestro modelo transforma ese "conocimiento empírico" en una herramienta estricta de **optimización financiera y tecnológica**.

1. **Ministerio de Hacienda y SGC (Optimización de Presupuesto):** Al pasar de la intuición a la validación estadística de los *centroides de energía*, estas entidades pueden justificar matemáticamente ante el gobierno central la reubicación de la Red Sismológica Nacional o la compra de nuevos sensores hiper-precisos. Ya no ubicarán estaciones por inercia histórica, sino en los radios de mayor captura energética.
2. **Unidad Nacional para la Gestión del Riesgo de Desastres (UNGRD):** Usarán las coordenadas exactas de los clústeres para focalizar sus simulacros y sistemas de alerta temprana (sirenas, telecomunicaciones) en los epicentros matemáticos de mayor amenaza recurrente, maximizando el retorno de inversión en prevención.
3. **Equipos de Telemetría y Mantenimiento:** Los ingenieros de campo del SGC utilizarán los centroides descubiertos por nuestro algoritmo como "blancos" geográficos (latitud y longitud exacta) para desplegar sus cuadrillas logísticas y priorizar el mantenimiento de la red en esas zonas de alto estrés energético.

### 4. Hipótesis: Zonas sísmicas esperadas
La dinámica sísmica de Colombia está impulsada fuertemente por su posición en el Cinturón de Fuego, siendo un punto de convergencia crítico entre la **Placa de Nazca** (subduciendo bajo la costa pacífica), la **Placa del Caribe** (chocando por el norte) y la **Placa Sudamericana**.

Con este contexto, la hipótesis central es que el algoritmo K-Means identificará **entre 4 y 6 zonas (clústeres) claramente diferenciadas**, que probablemente correspondan a:
1. **Zona de Subducción del Pacífico:** Concentración de sismos a lo largo de la costa occidental, originados por el choque Nazca-Sudamericana.
2. **Nido Sísmico de Bucaramanga:** Un clúster con alta densidad de eventos pero con una característica particular: una **profundidad intermedia/profunda muy constante** concentrada geográficamente en Santander. Es fundamental que el modelo logre aislar este fenómeno sin ayuda.
3. **Fallas Corticales Andinas:** Eventos predominantemente superficiales distribuidos a lo largo del sistema montañoso de los Andes.
4. **Zona de influencia del Caribe:** Sismicidad en la región norte por la interacción con la placa del Caribe.

## Fase 2: Data Understanding (Comprensión de los Datos / EDA Profundo)

En esta fase exploramos el dataset en bruto (`earthquakes.csv`) para entender las dimensiones, calidad de datos y empalmar el comportamiento estadístico con la geología del país antes de aplicar el clustering.

### 1. Dimensiones del Dataset y Contexto Espacial
- **Total de registros:** 2,791 sismos en el bounding box de la región andina norte.
- **Sismos en Colombia:** Al filtrar la columna `place` buscando la palabra "Colombia", validamos que **1,412 sismos** ocurren dentro de los límites políticos del país. Sin embargo, nuestro análisis debe incluir el bounding box completo, pues las estructuras tectónicas (como la subducción de Nazca) no respetan fronteras políticas, y la sismicidad fronteriza (Pacífico y Ecuador) afecta directamente al territorio nacional.

### 2. Calidad de Datos (Valores Nulos)
Las variables físicas principales que determinan el clúster están **100% completas (0 nulos)** para todos los 2,791 registros: `latitude`, `longitude`, `depth` y `mag`. No habrá necesidad de imputación sintética que sesgue nuestros centroides geográficos. 

Por otro lado, las variables instrumentales tienen alta carencia: `nst` (60.41% nulos), `horizontalError` (18.77%), `magError` (16.41%). Esto confirma teóricamente que nuestro clustering debe basarse netamente en las **coordenadas tridimensionales y magnitud**.

### 3. Análisis de Atípicos (Outliers)
Utilizando el Rango Intercuartílico (IQR), analizamos si existen valores anómalos que puedan arrastrar los centroides de K-Means (un algoritmo muy sensible a outliers):
- **Profundidad (Depth):** Sorprendentemente, **0% de atípicos**. Todo el rango de 0 a 200+ km está bien poblado y distribuido geológica y geográficamente.
- **Magnitud (Mag):** Encontramos **286 eventos atípicos (10.25% del total)**. El rango "normal" esperado estadísticamente está entre 3.9 y 5.0. Todos los sismos por encima de magnitud 5.0 son formalmente atípicos en este conjunto (llegando a un máximo de 7.8). Esto tiene pleno sentido sismológico ya que la magnitud sigue una distribución exponencial de Gutenberg-Richter: hay miles de microsismos por cada gran terremoto. Dejaremos estos atípicos porque son *anomalías físicas reales*, no errores de medición, pero los estandarizaremos en la Fase 3.

![Atípicos Boxplot](assets/outliers_boxplot.png)

### 4. Matriz de Correlaciones (Spearman)
Dado que nuestras variables (especialmente magnitud y profundidad) **no se distribuyen de forma normal/gaussiana**, aplicar correlación de Pearson sería un error metodológico. Empleamos la **Correlación de Rangos de Spearman (No Paramétrica)** encontrando:
- **Correlación Profundidad vs. Magnitud (ρ = -0.145):** Existe una correlación inversa, pero extremadamente débil. Esto desmiente el mito popular de que "a mayor profundidad, mayor magnitud". Son variables esencialmente independientes.
- **Correlación Latitud vs. Longitud (ρ = 0.566):** Existe una correlación positiva fuerte, lo cual tiene todo el sentido geológico: la cordillera de los Andes y la costa del Pacífico tienen una orientación diagonal (Sur-Oriente a Nor-Occidente), forzando a que las coordenadas (x,y) sigan este patrón lineal.

![Correlaciones Spearman](assets/correlaciones.png)

### 5. Análisis Granular de Profundidades (Depth)
Categorizar la profundidad binariamente oscurece la estructura tectónica de Colombia. Implementamos un _binning_ granular basado en las capas de la corteza:
- **Corteza Superior (<30km):** 37.9%. (Fallas locales y superficiales).
- **Corteza Inferior (30-70km):** 19.3%.
- **Zona de Transición (70-130km):** 11.0%. (Tensión por subducción).
- **Zona Intermedia-Nido (130-200km):** **31.6%**. (Un porcentaje masivo e inusual para una franja tan profunda).
- **Profunda (>200km):** 0.2%. 

Este análisis granular revela numéricamente lo que el mapa confirmará: la inmensa mayoría de la sismicidad está polarizada entre choques netamente superficiales cortícales y un "súper-nodo" en la franja de los 130-200km.

### 6. Historia Visual: El Poder de la Coordenada Z
El mapa de dispersión plano (Latitud vs Longitud) coloreado por magnitud arroja mucho "ruido" visual. Vemos magnitudes dispersas a lo largo del país, sin fronteras claras más allá de la silueta andina.

Sin embargo, al re-colorear el mismo mapa usando la **profundidad**, el ruido desaparece y emerge la estructura oculta:
1. **La Costa Pacífica:** Muestra un gradiente superficial a lo largo del margen, consistente con el inicio de la zona de subducción.
2. **El "Fenómeno Oculto" (Nido Sísmico de Bucaramanga):** A los 73°W, 6.8°N aproximadamente, salta a la vista un cúmulo extremadamente denso de sismos con una coloración (profundidad intermedia) drásticamente constante, que corrobora exactamente ese **31.6%** que encontramos en el _binning_ del bloque anterior.

Visualmente, ya sabemos que un K-Means bien parametrizado **debe** ser capaz de aislar matemáticamente este Nido como su propio cluster.

![Scatter de Profundidad](assets/scatter_depth.png)

### 7. Análisis de Variables Secundarias e Ingeniería de Características (Feature Engineering)
Analizamos el resto del dataset (columnas no geográficas) para evaluar si nos aportan valor o ruido para nuestro modelo K-Means:

**1. Limpieza Paramétrica**
- Variable `type`: El 100% de los 2,791 registros son del tipo `earthquake`. No hay contaminación por explosiones mineras o pruebas nucleares. Nos despreocupamos.
- Variables Instrumentales (`nst`, `gap`, `dmin`, `rms`, `errores`): El nivel de nulos ronda entre el 15% al 60%. Imputar el "número de estaciones" (`nst`) o el "error horizontal" aportaría cero información sismológica a K-Means, ya que son medidas de *calidad de registro humano*, no de las propiedades térmicas o tectónicas de la placa. **Se descartan del modelo.**

**2. Feature Engineering: Energía Sísmica (Joules) y su Impacto en el Modelo**
Transformamos la variable `mag` (Magnitud) en la **Energía Sísmica Liberada (E)** en Joules usando la fórmula física de Gutenberg-Richter: $E = 10^{(4.8 + 1.5M)}$.

¿Por qué este paso es fundamental y cambia completamente nuestro modelo de negocio?
- **El Problema Geométrico:** La magnitud que todo el mundo conoce (escala de Richter/Momento) es **logarítmica**. Un sismo de 5.0 no es "un punto más fuerte" que uno de 4.0, sino que **32 veces más fuerte** en energía destructiva (y uno de 6.0 es 1,000 veces más fuerte). K-Means agrupa utilizando distancias geométricas estrictamente lineales (Distancia Euclidiana). Si le damos la magnitud "cruda", el algoritmo será ciego a esta realidad física y asumirá equivocadamente que la distancia entre un sismo 2.0 y 3.0 es igual a la distancia entre 6.0 y 7.0, subestimando brutalmente la fuerza real de los grandes sismos y juntando peras con manzanas.
- **La Solución (Valor Agregado para el SGC):** Al convertir la magnitud a Joules (energía real, medida física pura y lineal), obligamos a K-Means a respetar el verdadero tamaño e impacto de cada sismo al calcular sus distancias. 

**Descubrimiento Colosal con esta variable:** Aunque los sismos de profundidad intermedia (como el Nido de Bucaramanga) son menores en cantidad de eventos que los superficiales andinos, concentran una cantidad de energía devastadora equivalente a casi **$1.88 \times 10^{16}$ Joules**. 

**Redefinición del Valor de Negocio:**
Gracias a esta transformación, nuestra solución pasa de simplemente identificar "dónde ocurren más sismos", a identificar **cuáles son las fuentes de mayor amenaza energética tectónica de Colombia**. Esto permite al SGC y a la UNGRD enfocar sus recursos financieros y logísticos (como sensores de alta precisión) en los clústeres que liberan auténticas "bombas" de energía (como la zona del Nido o de Subducción profunda), en lugar de distraerse con zonas corticales que presentan muchísima "basura sísmica" (miles de temblores diminutos que no liberan casi nada de energía). Alimentaremos K-Means con `energy_joules`.

**3. Análisis Temporal (Tiempo)**
Las capturas muestran un ritmo muy estable en los últimos 5 años (~200 sismos registrados/año en nuestro bounding box). Sin embargo, incluir el tiempo como variable en K-Means obligaría al algoritmo a agrupar "sismos que pasaron cerca de tiempo" y no "sismos que geológicamente están en la misma cuenca". Decidimos realizar el agrupamiento espacial/físico independiente del tiempo, para garantizar que la estructura responda a la tierra, no al calendario humano. Jugaremos con la variable tiempo solo después en el dashboard.

### 8. Resumen Ejecutivo del EDA y Directriz para la Fase 3
Tras un análisis exhaustivo de la base de datos, hemos transformado el enfoque del proyecto. Nuestro plan de acción para la Fase de Modelamiento queda definido así:
1. **Limpieza Quirúrgica:** Nos quedaremos **únicamente** con variables físicas puras. El ruido instrumental (`nst`, `gap`, `errores`) e histórico (`time`, `year`) queda descartado para K-Means porque no aportan geología estructural.
2. **El Peligro de la Redundancia Geométrica (Multicolinealidad Perfecta):** Ahora que creamos `energy_joules` usando una fórmula matemática directa sobre `mag`, tenemos dos variables que representan exactamente el mismo fenómeno (Fuerza destructiva). Si le entregamos a K-Means ambas columnas simultáneamente, estamos creando *redundancia artificial*. K-Means usa la suma de las distancias en todas las dimensiones; al poner las dos, la influencia de la fuerza del sismo valdrá "doble" en la suma matemática euclidiana, desbalanceando totalmente a la Latitud, Longitud y Profundidad. Por lo tanto, **es un imperativo matemático eliminar `mag` y conservar únicamente `energy_joules`** en nuestro dataset final para evitar que la matriz de distancias se "enamore" de este rasgo repetido.
3. **Respeto por la Geofísica (Outliers):** Hemos comprobado que los sismos potentes (> 5.0) son estadísticamente atípicos según el IQR, pero son la norma geofísica de Richter. Se mantienen en el modelo; la energía en Joules se asegurará de darles el peso protagónico sin tratarlos como "errores".
4. **Misión de K-Means (Scaling Inminente):** Comprobamos visualmente que la profundidad esconde el mayor secreto del país (El Nido de Bucaramanga). Para que K-Means no sea aplastado por las escalas planas de Lat/Lon (que van de -80 a 10) frente a los trillones de Joules, la **Fase 3 obligatoriamente empleará un escalado (StandardScaler)** para equilibrar los 4 ejes cartesianos ($x, y, z, energía$) y hallar los ansiados Centroides Matemáticos del SGC.

## Fase 3: Data Preparation (Impacto Matemático del Scaling)

En esta fase preparamos los 4 _features_ definitivos para el algoritmo: `latitude`, `longitude`, `depth`, y `energy_joules`. El paso crítico, como estipula el enfoque, es lidiar con el algoritmo de Distancia Euclidiana de K-Means utilizando **StandardScaler** (Z-score normalization).

### Comparativa: K-Means Sin Escalar vs. Escalado

Realizamos un experimento corriendo K-Means ($k=5$) sobre los datos crudos y luego sobre los datos procesados por `StandardScaler`. Respondiendo a las directrices críticas:

**1. ¿Cuál es la escala cartográfica de Latitude vs. Depth vs. Energy? ¿Qué feature domina si no escalas?**
Extrajimos los rangos matemáticos reales (Max - Min) de las variables en nuestro bounding box:
- **Rango de Latitud:** 17.7 unidades (grados).
- **Rango de Profundidad:** 239.4 unidades (kilómetros).
- **Rango de Energía:** $3.16 \times 10^{16}$ unidades (Joules).

**Respuesta:** Si no escalamos, la variable **Energía aplasta absurdamente a todas las demás**. Un cambio de $10^{16}$ hace que la distancia pitagórica en Latitud (17 unidades) sea matemáticamente invisible ("cero" estadístico). Si excluyéramos la energía, la **Profundidad** dominaría 13 veces más que la geografía plana. Para K-Means crudo, moverse 1 grado de latitud (111 km en la vida real) "cuesta" exactamente lo mismo que moverse 1 km de profundidad. Esta distorsión matemática arruina cualquier análisis espacial.

**2. ¿Cambian los clusters al escalar? ¿Por qué?**
**Respuesta:** Cambian drásticamente.
- *Sin escalar:* El algoritmo se vuelve unidimensional, separando los clusters casi exclusivamente basándose en cortes rectos generados por la variable de trillones de unidades (Joules/Profundidad), ignorando por completo el mapa político y geográfico.
- *Con Scaling (Z-Score):* Todas las variables pasan a tener media $\mu = 0$ y varianza $\sigma^2 = 1$. ¿Por qué cambia el resultado? Porque ahora el algoritmo puede hallar esferas multidimensionales donde **cada variable pesa equitativamente 25%**. Un desvío estándar de latitud "pesa" lo mismo que un desvío estándar de profundidad o energía.

**3. ¿Cuál versión produce clusters más interpretables para el SGC?**
**Respuesta:** La versión **Con Scaling (StandardScaler)**. Al permitir que todas las variables compitan en igualdad de varianza, emergen los verdaderos patrones sismotectónicos 3D. El scaling permite que la profundidad "entre en juego sin aplastar", lo que logra que veamos zonas geográficas que se superponen en el mapa 2D (ej. sismos superficiales en Bucaramanga junto al Nido profundo), pero que el modelo logra segregar como clústeres geológicamente independientes.

![Comparativa de Scaling (K-Means k=5)](assets/scaling_comparison.png)

## Fase 4: Modeling (Modelamiento y Selección de K)

Habiendo escalado las 4 variables físicas puras ($x, y, z, energía$), procedemos a buscar el número óptimo de zonas sísmicas ($k$) para entregarle los centroides matemáticos al gobierno. Simulamos K-Means desde $k=2$ hasta $k=10$.

![Método del Codo y Silhouette](assets/elbow_silhouette.png)

### Argumentación y Selección del $K$ ptimo

Para decidir cuántos centroides (y por ende, cuántas bases de monitoreo) le recomendaremos al SGC, analizamos las tres directrices:

**1. ¿Qué dice el Método del Codo (Inercia)?**
La curva de inercia (suma de las distancias cuadradas intra-cluster) muestra un descenso continuo esperado. El "codo" geométrico más prominente ocurre en **$k=4$** y **$k=5$**. A partir de $k=5$, la reducción de la varianza marginal cae muy lentamente, lo que indica que agregar un 6to o 7mo clúster ya no aporta cohesión matemática medible, sino que empieza a sobre-segmentar grupos que pertenecen a la misma dinámica.

**2. ¿Qué dice el Silhouette Score?**
El Silhouette Score (que evalúa qué tan bien separado está cada clúster de sus vecinos) nos cuenta una historia interesantísima:
- **$k=2$ a $k=4$**: Presentan Scores estables alrededor de ~0.55 / 0.58.
- **$k=5$**: Marca el último punto de alta cohesión estructural antes de empezar a deteriorarse con fluctuaciones u oscilaciones rítmicas hacia $k=10$.

**3. ¿Tiene sentido geológico/geográfico? (La decisión de Negocio)**
*El "mejor" k no es necesariamente el que tiene mayor silhouette.* Si eligiéramos a ciegas $k=2$, el algoritmo simplemente partiría a Colombia en "oriente y occidente", obteniendo buen puntaje pero cero valor de negocio.

**Decisión Final:** Elegimos **$k=5$** como el número óptimo de clústeres.
Esta selección sintoniza perfectamente la matemática con la geología tectónica y la optimización de presupuesto, porque nos aísla las 5 dinámicas energéticas independientes de Colombia:
1. Zona de Subducción (Placa de Nazca superficial).
2. Zona del Caribe (Falla frontal norte).
3. Eje Cafetero y Cordillera Central (Andes superficiales).
4. Sismicidad Sur-Ecuador (Nudo de los Pastos).
5. **El Nido Sísmico de Bucaramanga** (El súper-nodo aislado en 150km de profundidad).

*Valor de negocio:* Decirle al MinHacienda que nos apruebe presupuesto para "5 mega-estaciones centrales" (una por cada centroide matemático) es un Resource Allocation preciso, sustentado en el codo de inercia y en la distribución real de las placas de Colombia, ni más ni menos. Iterar a $k=6$ o superior fragmentaría estas placas en sub-zonas redundantes y encarecería el presupuesto logístico sin añadir mayor detección de amenaza real.

## Fase 5: Interpretación Inteligente de Clústeres (K=5)

Esta es la base argumentativa para entregar la consultoría y responder las directrices técnicas obligatorias. Ejecutamos el modelo final, obteniendo el mapa sismotectónico de Colombia y perfilando el comportamiento de cada Centroide.

![Mapa de Clústeres K=5](assets/clusters_k5_map.png)

### 5.1 Perfil de Cada Clúster (Estadística y Geología)

Basados en los centroides extraídos por K-Means usando (Latitud, Longitud, Profundidad y Energía):

- **Cluster 0 (Nudo de los Pastos / Frontera Ecuador):**
  - **Sismos:** 1,056 | **Profundidad Media:** 62.4 km (Intermedia) | **Magnitud Media:** 4.5
  - **Ubicación:** Sur del país (Lat: -1.5, Lon: -79.0). Zona de altísima fricción tectónica compartida geológicamente (no políticamente) entre Nariño y Ecuador.
- **Cluster 1 (El Nido de Bucaramanga):**
  - **Sismos:** 773 | **Profundidad Media:** 152.6 km (Súper Profundo) | **Magnitud Media:** 4.39
  - **Ubicación:** Nororiente andino (Lat: 6.6, Lon: -73.3). El volumen de roca bajo Santander.
- **Cluster 2 (Sistema de Fallas Andinas y Caribe):**
  - **Sismos:** 382 | **Profundidad Media:** 18.7 km (Muy Superficial) | **Magnitud Media:** 4.44
  - **Ubicación:** Noroccidente y Norte (Lat: 8.1, Lon: -71.7). Captura la sismicidad cortical de la región andina norte y la interacción incipiente con la placa del Caribe.
- **Cluster 3 (El Evento Aislado / Anomalía Extrema):**
  - **Sismos:** ¡Solo 1! | **Profundidad:** 20.5 km | **Magnitud:** 7.8
  - **Ubicación:** Muisne, Ecuador (Terremoto de Pedernales 2016). 
  - **Interpretación:** Por haber convertido la magnitud a Joules, K-Means entendió que este sismo ($E \approx 10^{16}$ J) liberó tanta energía por sí solo que matemáticamente obligó al algoritmo a aislarlo como su propia dimensión destructiva. ¡K-Means haciendo detección de anomalías!
- **Cluster 4 (Zona de Subducción Pacífica):**
  - **Sismos:** 579 | **Profundidad Media:** 28.9 km (Superficial) | **Magnitud Media:** 4.57
  - **Ubicación:** Costa Pacífica / Chocó (Lat: 6.5, Lon: -78.0).

### 5.2 y 5.3 Hallazgos y Respuestas Directas al SGC

**¿Los clusters tienen sentido geográfico?**
Absolutamente. Al estandarizarlos (Z-score), K-Means respetó la distribución norte-sur de los Andes y la franja occidental del Pacífico, agrupando sismos contiguos. Pero, más brillante aún, respetó la coordenada Z (Profundidad) de tal forma que agrupó el Nido Sísmico, aislando su identidad.

**¿Hay algún cluster de sismicidad profunda concentrada en una zona específica? ¿Cuál?**
Sí, el **Cluster 1**. Tiene un promedio de 152 km de profundidad, con una desviación estándar muy apretada (16 km), centrado en las coordenadas de Santander. Este es inequívocamente el "Nido Sísmico de Bucaramanga", validado estadísticamente (ya no es un mito empírico, es una zona de agrupación matemática real).

**¿Hay clusters que coincidan con la zona de subducción del Pacífico?**
Por supuesto, el **Cluster 4**. Se dibuja paralelamente a lo largo de toda la costa de Chocó y Valle del Cauca, a una baja profundidad (28 km), que es exactamente la zona somera donde la Placa de Nazca choca y raspa superficialmente a la placa Sudamericana antes de hundirse.

**¿Algún cluster captura los sismos de mayor magnitud?**
Sí. De forma espectacular, K-Means generó el **Cluster 3** con 1 solo sismo absoluto. Alimentar al modelo con "Energía en Joules" hizo que la monstruosidad física del Terremoto del 2016 en Ecuador se desmarque a trillones de unidades de distancia geométrica del resto. Actuó como un algoritmo de *Outlier Detection*.

**¿Qué cluster recomendarías priorizar para alertas tempranas y por qué? (Consejo de Negocio)**
Recomiendo priorizar el **Cluster 4 (Subducción del Pacífico)** para alertas tempranas inmediatas y redes de sirenas costeras. 
- *Razón 1:* Su centroide es superficial (28 km), lo que significa que el 100% de la energía destructiva llega íntegra y sin atenuación a las ciudades del Pacífico.
- *Razón 2:* Riesgo de Tsunami. Al estar situado sobre el nivel costero, la disrupción tectónica aquí genera desplazamiento de masas de agua. 
*(El Cluster 1 -Nido de Bucaramanga- libera mucha energía constante, pero al ocurrir a 150 km de profundidad, la corteza terrestre actúa como amortiguador térmico, reduciendo la letalidad en superficie. Por tanto, el presupuesto de Prevención de Desastres debe inyectarse en el Clúster 4).*

