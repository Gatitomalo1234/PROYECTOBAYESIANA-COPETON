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

## 2. Paso a Paso de la Construcción

### Paso 1: Definir la Likelihood del Sistema Completo
En un modelo de ocupación, tenemos dos tipos de parámetros: $\beta$ (para ocupación) y $\alpha$ (para detección), además de un estado latente $z$ (presencia real).

La **Likelihood Total** es la probabilidad conjunta de observar lo que vimos en eBird ($y$) dado el estado de ocupación ($z$) bajo los parámetros $\alpha$ y $\beta$:

$$L(y, z | \beta, \alpha) = \prod_{i=1}^N \underbrace{P(z_i | \beta)}_{\text{Ocupación}} \cdot \underbrace{\prod_{j=1}^{K_i} P(y_{i,j} | z_i, \alpha)}_{\text{Detección}}$$

- **Ocupación**: $z_i \sim \text{Bernoulli}(\text{logit}^{-1}(X_i\beta))$. Si el sitio está contaminado, $\psi_i$ baja.
- **Detección**: $y_{i,j} \sim \text{Bernoulli}(z_i \cdot \text{logit}^{-1}(W_{i,j}\alpha))$. Si no hay ave ($z_i=0$), no detectamos nada.

### Paso 2: Especificación de las Priors (No Informativas / Débilmente Informativas)
Para cada coeficiente de nuestras regresiones, asignaremos una distribución previa, asumiendo ignorancia pero permitiendo que el muestreo converja y deje a los datos regir.

**1. Estructura y Variables Específicas:**
Según nuestro análisis previo de datos (EDA), los hiperparámetros se configuran sobre dos componentes aislados:
- **Ecuación de Ocupación Ecológica ($\psi$):** Estructurada por $\beta_0$ (Intercepto base), $\beta_{PM10}$ (Efecto del PM$_{10}$) y $\beta_{O3}$ (Efecto del Ozono).
- **Ecuación de Detección/Esfuerzo ($p$):** Estructurada por $\alpha_0$ (Intercepto base), $\alpha_{duracion}$ (Tiempo de búsqueda en minutos), $\alpha_{estacion}$ (Heterogeneidad geográfica) y $\alpha_{protocolo}$.

**2. Distribuciones a Priori:**
Para acoplarse eficientemente al aumento de variables de Pólya-Gamma y la función probabilística logística (Logit), todas nuestras pre-creencias sobre los coeficientes se modelarán usando \textbf{Distribuciones Normales (Gaussianas)}.
$$ \beta \sim \text{Normal}(\mu_\beta, \Sigma_\beta) $$
$$ \alpha \sim \text{Normal}(\mu_\alpha, \Sigma_\alpha) $$

**3. Hiperparámetros Designados:**
Bajo la estadística Bayesiana contemporánea, y como garantía para prevenir problemas numéricos letales dentro de la transformación de probabilidades (Logit), se establece el bloque iterativo bajo los siguientes parámetros uniformes para todos los $\beta$ y $\alpha$:
- **Media ($\mu$):** $0$
- **Desviación Estándar ($\sigma$):** $1.5$ (Equivalente en matriz de varianza $\Sigma$ a $2.25$)

El estado inicial base para toda variable es $\theta_{inicial} \sim \text{Normal}(0, 1.5)$.
*(Nota matemática: Tradicionalmente una varianza inmensa ($\sigma=1000$) se vendía como "no informativa". Sin embargo, sobre funciones Logit, empuja falsamente los pesos hacia topes extremos ($0$ y $1$). Un $\sigma=1.5$ aplana completamente la probabilidad real en la campana permitiendo verdadera imparcialidad).*

**4. Argumento detrás de cada Prior:**
- **Escepticismo y Media Cero $\mu=0$:** Significa que el algoritmo arranca asumiendo categóricamente que ni el polvo ni los gases tienen efecto sobre el Copetón. Si la muestra termina siendo negativa no será por sesgo preconcebido, sino porque la avalancha colosal de los avistamientos empujó de facto el modelo en esa dirección.
- **Amplitud Flexible ($\sigma=1.5$):** Ofrece libertad maleable a tu esquema paramétrico para aislar sin trabas y "absorber" toda la inmensa cantidad de falso-ruido proveniente de las horas invertidas y la geolocalización de las aceras de monitoreo antes de juzgar la polución pura.

### Paso 3: Combinar Likelihood y Prior para la Posterior
Multiplicamos ambos componentes. La distribución posterior conjunta es:

$$P(\beta, \alpha, \mathbf{z} | \mathbf{y}) \propto \left[ \prod_{i=1}^N \text{Bern}(z_i | \psi_i) \prod_{j=1}^{K_i} \text{Bern}(y_{i,j} | z_i p_{i,j}) \right] \cdot P(\beta) \cdot P(\alpha)$$

### Paso 4: El Desafío del Logit y la Solución de Clark (Polya-Gamma)
Como el término logit hace que la posterior no tenga una forma fácil de integrar, Clark introduce variables de aumento **Polya-Gamma ($\omega$)**. 

Esto transforma la Likelihood Bernoulli en una forma que parece una Normal. El paso a paso computacional (Gibbs Sampling) sería:
1.  **Actualizar $z$**: Estimar si el ave estaba presente en sitios donde no se vio.
2.  **Actualizar $\omega$**: Generar las variables latentes de Polya-Gamma.
3.  **Actualizar $\beta$ y $\alpha$**: Al usar $\omega$, la posterior de los coeficientes se convierte en una **Normal**, que es muy fácil de calcular:
    $$\theta_{post} \sim \text{Normal}(\text{Media Ponderada}, \text{Varianza Actualizada})$$

---

## 3. Resultado Final: Los Parámetros Posteriores
Al final del proceso, el modelo te devuelve miles de muestras de la "Posterior". Para cada contaminante tendrás:
1.  **Estimación puntual**: La media o mediana de la posterior.
2.  **Incertidumbre**: Intervalos de Credibilidad (p.ej., del 95%). 

**Interpretación Biológica:**
Si el intervalo de credibilidad del coeficiente de `pm25_ugm3` no incluye al cero y es negativo, habrás demostrado que el material particulado reduce significativamente la probabilidad de ocupación de esa especie en Bogotá.
