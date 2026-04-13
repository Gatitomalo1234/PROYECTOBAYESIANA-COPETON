# Guía Teórica: Construcción de la Posterior en Modelos de Ocupación

Esta guía detalla el proceso matemático y logístico para construir un modelo Bayesiano de ocupación jerárquico, enfocado en el cruce de datos de aves y contaminación.

## 1. El Fundamento: El Teorema de Bayes

La meta de cualquier análisis Bayesiano es hallar la **Distribución Posterior** de los parámetros ($\theta$), dado que hemos observado ciertos datos ($D$):

$$P(\theta | D) = \frac{P(D | \theta) P(\theta)}{P(D)}$$

Donde:
- $P(D | \theta)$ es la **Likelihood** (Verosimilitud): ¿Qué tan probables son los datos según mis parámetros?
- $P(\theta)$ es la **Prior**: Mi conocimiento o suposición inicial sobre los parámetros.
- $P(D)$ es la evidencia (una constante de normalización que suele ignorarse en el muestreo).

---

## 2. Especificación de las Priors (No Informativas)

Para cada coeficiente de nuestras regresiones, asignaremos una distribución previa, asumiendo ignorancia pero permitiendo que el muestreo converja y deje a los datos regir.

### 2.1 Estructura y Variables Específicas

Según nuestro análisis previo de datos (EDA), los hiperparámetros se configuran sobre dos componentes aislados:

- **Ecuación de Ocupación Ecológica ($\psi$):** Estructurada por $\beta_0$ (Intercepto base), $\beta_{PM10}$ (Efecto del PM$_{10}$) y $\beta_{O3}$ (Efecto del Ozono).
- **Ecuación de Detección/Esfuerzo ($p$):** Estructurada por $\alpha_0$ (Intercepto base), $\alpha_{duracion}$ (Tiempo en minutos), $\alpha_{estacion}$ (Heterogeneidad geográfica) y $\alpha_{protocolo}$.

### 2.2 Distribuciones a Priori
Para acoplarse eficientemente al aumento de variables de Pólya-Gamma y la función probabilística logística (Logit), todas nuestras pre-creencias sobre los coeficientes se modelarán usando **Distribuciones Normales** con hiperparámetros estandarizados no informativos. Cada coeficiente distribuye de manera independiente así:

**Eje Ecológico ($\psi$):**
$$ \beta_0 \sim \text{Normal}(0, 1) $$
$$ \beta_{PM10} \sim \text{Normal}(0, 1) $$
$$ \beta_{O3} \sim \text{Normal}(0, 1) $$

**Eje de Detección ($p$):**
$$ \alpha_0 \sim \text{Normal}(0, 1) $$
$$ \alpha_{duracion} \sim \text{Normal}(0, 1) $$
$$ \alpha_{estacion} \sim \text{Normal}(0, 1) $$
$$ \alpha_{protocolo} \sim \text{Normal}(0, 1) $$

**Eje Fantasma de Aplanamiento ($\omega$):**
$$ \omega \sim \mathcal{PG}(b=1, c=0) $$
*(Nota teórica: La distribución Pólya-Gamma formalizada por P.G. Polson requiere dos propiedades. El parámetro de sucesos se blinda en $b=1$ al estar condicionado individualmente a la verosimilitud de la variable binaria eBird. Por convergencia a posteriori, su media es neutra, anclada base $c=0$, comportándose como un tensor universal neutro ideal).*

### 2.3 Justificación Metodológica de la Prior "No Informativa"
El uso estricto de una prior neutra $\text{Normal}(0, 1)$ se fundamenta enteramente en una **premisa de objetividad por falta de experticia a priori**. 
- Como equipo, no somos ornitólogos expertos absolutos como para asegurar prematuramente qué tanto (en una tasa puntual exacta) un microgramo de Ozono va a diezmar matemáticamente la población estacionaria de unas aves. Al no saberlo certeramente, nos declaramos ignorantes ante el sistema fijando toda expectativa central en cero ($\mu=0$). 
- Intentar cambiar nosotros mismos la media o jugar con la varianza para "ajustar" el modelo, así fuera moviéndolo tan solo un mísero $0.01$, implicaría insertar conocimientos falsos o pre-concebidos, sesgando irreparablemente el diseño algorítmico.
- Por ende, la única manera robusta y transparente de proceder es lavar nuestras manos forzando una distribución plana y no informativa al $100\%$. Si el modelo en su simulación final decreta que la polución sí arrasa con la ocupación, sabremos indudablemente que dicho descubrimiento fue producido **única y exclusivamente** por la presión abrumadora de los datos silentes que aportó eBird sobreponiéndose a nuestra hoja en blanco empírica.

---

## 3. La Likelihood (Verosimilitud)

### 3.1 Separación de Parámetros (Beta vs Alpha)
En los modelos jerárquicos de ocupación, se independiza matemáticamente el ecosistema real del error humano. El modelo se fractura en dos mundos que actúan como válvulas:
- **Mundo Ecológico ($\beta$):** Modelan la Biología (Ocupación latente - $\psi$). ¿El ecosistema permite que el ave viva allí?
- **Mundo Humano ($\alpha$):** Modelan el Error Observacional (Detección - $p$). ¿El humano reportó al ave, asumiendo que esta sí estaba ahí?

### 3.2 La Likelihood Aumentada y el Origen de la Pólya-Gamma
Entender de dónde sale este "truco" es la clave para defender la metodología. El proceso sigue una lógica de tres escalones:

**Paso 1: La Naturaleza Binaria (Bernoulli)**
En cada evento de observación, capturamos un éxito o un fracaso. La verosimilitud (Likelihood) de un solo dato $y$ (presencia/ausencia) se define como:
$$ P(y | \psi) = \psi^y (1 - \psi)^{1-y} $$

**Paso 2: El Enlace Logístico (Inverse-Logit)**
Para vincular nuestra probabilidad biológica $\psi$ con las variables ambientales $X\beta$, usamos la función Inverse-Logit:
$$ \psi = \frac{e^{X\beta}}{1 + e^{X\beta}} $$
Al sustituir esta "curva" en la fórmula de la Bernoulli del Paso 1, llegamos a la expresión que el computador encuentra difícil de procesar:
$$ P(y | X\beta) = \frac{(e^{X\beta})^y}{1 + e^{X\beta}} $$

**Paso 3: El Acondicionamiento Estocástico (Identidad de Pólya-Gamma)**

Para romper ese denominador intratable, aplicamos la identidad de Polson et al. (2013). Esta identidad nos permite ver la probabilidad como una integral de una distribución Normal ponderada por la variable fantasma $\omega$:

$$ \underbrace{\frac{(e^\psi)^y}{(1+e^\psi)}}_{\text{Inverse-Logit}} = \underbrace{\frac{1}{2} \exp \left( (y - 1/2)\psi \right)}_{\text{Capa Lineal}} \int_0^\infty \underbrace{\exp \left( -\frac{\omega \psi^2}{2} \right)}_{\text{Capa Cuadrática (Normal)}} p(\omega | 1, 0) d\omega $$

- **El Transformador Latente ($\omega$):** En lugar de pelear con la curva, "condicionamos" nuestra creencia a la existencia de $\omega$. Su función es analizar el valor de la polución y generar un peso que "enderece" la curva.
- **La Linealización:** Al observar el resultado (dentro de la integral), vemos que la arquitectura se ha transformado en una **Estructura Cuadrática (una Parábola)** de la forma $\exp(-\omega \psi^2 / 2)$.

**¿Por qué es esto "magia"?**

Porque en estadística, una parábola en el exponente es sinónimo de una **Distribución Normal**. Al usar la Pólya-Gamma, hemos "engañado" al sistema: tomamos una Bernoulli difícil y la convertimos en una Normal fácil, permitiendo que el modelo se engrane perfectamente con nuestras Priors de "no expertos" para dar una solución exacta y ultrarrápida.

---

## 4. Construcción de la Posterior Paso a Paso

Aquí es donde se junta todo el conocimiento previo con la evidencia de los datos.

### 4.1 La Fórmula de la Posterior Conjunta
Siguiendo la regla de Bayes aplicada al modelo aumentado, la **Distribución Posterior Conjunta** es proporcional al producto de la Likelihood Aumentada por todas nuestras Priors:

$$ P(\beta, \alpha, \mathbf{z}, \boldsymbol{\omega} | \mathbf{y}) \propto \underbrace{L(\mathbf{y}, \mathbf{z}, \boldsymbol{\omega} | \beta, \alpha)}_{\text{Datos (Likelihood)}} \times \underbrace{\pi(\beta) \pi(\alpha) \pi(\boldsymbol{\omega})}_{\text{Ignorancia (Priors)}} $$

Al sustituir los componentes, vemos la unión total:
$$ P(\beta, \alpha, \mathbf{z}, \boldsymbol{\omega} | \mathbf{y}) \propto \prod_{i=1}^N \left[ P(z_i, \omega^\psi_i | \beta) \prod_{j=1}^{K_i} P(y_{i,j}, \omega^p_{i,j} | z_i, \alpha) \right] \times \text{Normal}(\beta|0,1) \times \text{Normal}(\alpha|0,1) \times \mathcal{PG}(\omega|1,0) $$

### 4.2 El Desafío del Logit y la "Magia" de Pólya-Gamma
El Logit es "intratable" porque no encaja en una campana de Gauss normal. La variable fantasma **Pólya-Gamma ($\omega$)** transforma la Likelihood Bernoulli en una forma cuadrática. Esto permite usar el **Muestreo de Gibbs (Gibbs Sampling)**, rompiendo la ecuación gigante en 4 bloques iterativos:

1.  **Bloque Z (Estado Latente):** Imputar el ecosistema latente donde no hubo detección.
2.  **Bloque $\omega$ (Aplanamiento):** Generar las variables latentes para "enderezar" el Logit.
3.  **Bloque $\beta$ (Ecología):** Calcular los efectos de la polución (ahora es una distribución **Normal**).
4.  **Bloque $\alpha$ (Humano):** Calcular los efectos del esfuerzo pajarero (ahora es una distribución **Normal**).

### 4.3 La Convergencia
Tras miles de vueltas (Cadenas de Markov), los valores se estabilizan alrededor de la "verdad estadística". Esa nube de puntos finales es nuestra **Posterior**.

### 4.4 La Mecánica de la Solución Cerrada (Conjugación)
Gracias a la inyección de la variable fantasma $\omega_i$, el modelo logra lo que parecía imposible: una **solución cerrada**. En cada paso del muestreador, la Posterior de los coeficientes ($\beta$ y $\alpha$) se calcula directamente mediante una suma de matrices (conjugación Normal-Normal).

**¿Qué es exactamente $\omega$?**
$\omega_i$ no es un parámetro fijo, sino una **variable latente estocástica**. Es el resultado de preguntarle a la distribución Pólya-Gamma en cada iteración: *"¿Qué peso necesito para que este dato de eBird se vea lineal?"*. $\omega$ actúa como una **Varianza Local** que endereza la curva.

**Las Fórmulas de Actualización:**
Con la Likelihood "aplanada", la Posterior de los coeficientes en cada paso del MCMC se define por una nueva distribución Normal con los siguientes parámetros:

1.  **Varianza Posterior Actualizada ($V_n$):** 
    $$ V_n = (X^T \Omega X + V_0^{-1})^{-1} $$
    *(Donde $\Omega = \text{diag}(\omega_{1 \dots N})$ es la matriz de pesos fantasmas y $V_0^{-1}$ es la precisión de nuestra Prior).*

2.  **Media Posterior Actualizada ($\mu_n$):**
    $$ \mu_n = V_n (X^T \kappa + V_0^{-1}\mu_0) $$
    *(Donde $\kappa_i = y_i - 1/2$ son los datos de eBird centrados, y $\mu_0$ es nuestra media inicial de cero).*

Este proceso convierte un problema de optimización curvo y lento en una serie de **operaciones algebraicas directas y exactas**, garantizando que el modelo converja a la respuesta real del impacto del $PM_{10}$ y el $O_3$ de forma eficiente.

---

## 5. Resultado Final: Los Parámetros Posteriores

Al final, el modelo devuelve miles de muestras de la Posterior. Para cada contaminante obtendremos:
1.  **Estimación puntual**: La media o mediana de la posterior.
2.  **Incertidumbre**: Intervalos de Credibilidad (p.ej., del 95%). 

**Interpretación Biológica:**
Si el intervalo de credibilidad del coeficiente de una variable ambiental (ej. $PM_{10}$) no incluye al cero y es totalmente negativo, habremos demostrado que dicho contaminante reduce significativamente la probabilidad de ocupación del Copetón en Bogotá, habiendo controlado todo el ruido de detección humana.
