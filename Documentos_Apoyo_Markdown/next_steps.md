# Plan para la Siguiente Sesión (Data Augmentation)

## Contexto de la Decisión
- Nos dimos cuenta de que la base unificada actual de eBird + OpenAQ (910 datos) sufrirá un bajón sustancial cuando descartemos los nulos (\textasciitilde 40% de falta de datos referenciales en mediciones como $SO_2$ y $NO_2$). 
- Con pocos datos biológicos filtrados y distribuidos sobre 19 estaciones ambientales, perderíamos representatividad geográfica clave.
- **La solución aprobada es exprimir la API de OpenAQ.**

## Estado de las APIs y Límites

1. **RMCAB/OpenAQ:** Los datos de Bogotá en esa API solo están históricos desde el `06 de mayo de 2020`. No existen antes de eso.
2. **eBird:** Tenemos avistamientos disponibles hasta el `31 de enero de 2026`.
3. **Limitaciones OpenAQ:** Tienen un estricto `Rate limit` de 60 peticiones por minuto.

## Paso 1: Acción Inmediata (Para realizarse después)

Al regresar, yo (la inteligencia artificial) me encargaré estrictamente de:

1. **Reescribir el script `fetch_bogota_pollution_hourly.py`:**
   - La nueva versión usará la ventana completa disponible: `2020-05-01` hasta `2026-02-01`.
   - Incluirá un "controlador de tiempo" (sleep): de este modo, cuando la API amenace con bloquear por pasarnos de las 60 peticiones por minuto, el script esperará el tiempo justo (60seg) y continuará extrayendo sin que se pierda la data, el avance quedará local.
   
2. Volveremos a lanzar el `cross_join_birds_pollution.py` para fusionar toda esta enorme nueva base, lo que podría aumentar nuestros $N$ biológicos y compensar exitosamente los nulos atmosféricos faltantes. 

*Nos vemos en la próxima sesión para la programación computacional.*
