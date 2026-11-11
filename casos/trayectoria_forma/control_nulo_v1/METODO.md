# Control nulo PC12 — método fijado antes de simular

Cinco matrices crudo_P reales (Mozart10 del gate reproducido, Galileo, Hawking6, Che, MLK); N y 244 familias idénticos a cada caso. Se conservan familias de varianza cero. Seed maestro 202611110503, subsemillas independientes y guardadas por caso/nulo. 1000 muestras por celda, sin reemplazar un fallo con otra muestra.

## Nulos
1. Permutación de FILAS completas (preserva estados/correlaciones entre familias), con reemplazo de órdenes entre réplicas, sobre la misma grilla temporal de control. Las etiquetas de slot no se permutan: se destruye el orden histórico. Se informa número de órdenes únicos (Hawking6 solo tiene 6!=720 posibles).
2. Caminata gaussiana independiente por familia: incrementos N(0,1), acumulados N puntos, multiplicados por sigma_observada/sqrt((N+1)/6), más la media observada. Así la varianza temporal muestral ESPERADA es la observada por familia, no se condiciona cada realización a una varianza exacta. Es un proceso gaussiano; no se fuerza su radio o forma.
3. Ruido iid gaussiano independiente por corte/familia, media y sigma muestral por familia observadas. La varianza temporal esperada coincide. RW/iid NO conservan la covarianza entre familias, la permutación sí.

Son nulos matemáticos geométricos; no son entradas del Engine ni pesos. No se recortan a 0.01–0.999: hacerlo alteraría el nulo. Nada se envía a H/ranking/apuesta, ni se ejecuta el Engine.

## Transformación y métricas
Se llama la misma función PC12 del script fiel generalizado: centrado, scores=U*S, PC1/PC2 y rotación C1→Cn horizontal; r=hypot y fase unwrap. SIN reflejar ejes para favorecer forma.

Se reutilizan forma operacional PC12 y prefijo radial no creciente hasta primer aumento (>=3 puntos), b/R² radio OLS log-r, y seno sobre y con 2048 frecuencias. La grilla temporal observada queda fija también en permutaciones. No se cambian reglas por resultado. El seno se vectoriza con las mismas proyecciones OLS y grilla; se contrasta numéricamente con el ajuste de referencia antes de simular. Ajustes de radio no identificables se conservan N/D, se informa su frecuencia y el percentil b/R² condicionado a ajustes válidos.

Percentil midrank =100*(#nulo<real +0.5*#empates)/n_válidos. No es probabilidad predictiva. p superior Monte Carlo=(1+#nulo>=real)/(1+n_válidos). Se guardan las distribuciones y conteos de no-ajuste. Forma=%réplicas que cumplen el criterio completo. Giro principal=valor ABSOLUTO del cambio neto, no suma de pasos angulares; se guarda asimismo giro firmado.

## Salto y familia
Para el salto elegido por LA MISMA regla: longitud/mediana de longitudes positivas. Familia que sube=mayor delta crudo_P POSITIVO, conservando empates. Se mide también el máximo delta/sigma observada entre TODAS las familias en ese salto; los nulos hacen la misma búsqueda y no comparan una familia preseleccionada con una elegida después.

Se reporta: percentil de fuerza relativa del salto, percentil del máximo aumento estandarizado; frecuencia de elegir el mismo slot y frecuencia de que gane cualquiera de las familias reales (sobre todos los nulos y condicionadas a tener salto). Frecuencias de identidad/slot son descripciones post-hoc, NO p-values de una hipótesis pre-registrada. Para p superiores de fuerza del salto y máximo delta/sigma se aplica Holm por separado a las 12 comparaciones principales (4 casos con salto ×3 nulos). Cualquier ausencia de salto se mantiene como ausencia, no como un valor cero. No se afirma información semántica o causalidad desde rareza numérica.

## Hawking externo de siete cortes, sin años ni crudo_P
Se conserva el CSV recibido; NO se inventa la séptima fila de 244 familias ni años. No puede hacerse su permutación emparejada de crudo_P ni identificar familia del salto. Como control ADICIONAL y explícitamente PROXY, se generan 1000 RW y 1000 iid con N=7 y 244 familias usando las varianzas del Hawking6 disponible; tiempo=índice de corte, b en 1/corte. Se comparan con métricas de las coordenadas externas recibidas. No son controles emparejados propios de Hawking7, no entran en Holm de los cinco casos y no sustituyen el RESULT ausente. La permutación DIRECTA de crudo_P y las familias de Hawking7 quedan NO EVALUABLES; la variante geométrica 2-D se precisa en la ampliación al final. El nuestro tiene seis cortes y giro ~221.4°; el CSV externo siete y ~222.5°.

No cambiar parámetros, selección de prefijo, umbrales, cantidad de muestras ni seed al ver resultados. Sin push.

Apéndice conjunto exploratorio: se informa el número de formas completas entre los cinco casos y su cola bajo réplicas independientes por caso de cada nulo. Esto no vuelve pre-registrados ni independientes los casos reales y no se usa como confirmación de una ley general.

Ampliación Hawking7 ANTES de ejecutar esta variante: sí puede permutarse su geometría 2-D conocida. Al permutar FILAS del crudo_P no cambia la covarianza entre familias, por lo que tampoco cambia el subespacio de las dos PC (hasta orientación). Se calculan 1000 permutaciones de las coordenadas conocidas, se vuelve a centrar/PCA/alinear y se reportan percentiles de las métricas INVARIANTES a reflexión: radio, |giro|, b, R² y seno. La handedness que elegiría el SVD de las 244 familias desconocidas no es recuperable: para forma operacional se dan límites (cumple en ambas orientaciones / en alguna), no un porcentaje familiar exacto. Familias del salto siguen N/D. No se reconstruye crudo_P de siete cortes.

Precisión de la ampliación H7: la equivalencia con permutar filas del subespacio original presupone una brecha PC2/PC3 no degenerada, NO VERIFICABLE sin el crudo_P ausente. Los CSV redondeados añaden error de serialización; métricas invariantes son aproximaciones a esa precisión, no una reproducción del RESULT faltante.
