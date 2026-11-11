# Geometría del giro: diseño numérico previo a simulación

Solo matemática descriptiva. Misma proyección: centrado, scores PC1/PC2 SVD, rotación de cuerda C1→Cn, unwrap atan2. Giro=abs(fase_final−fase_inicial), no suma de módulos. Fuera del motor/H/ranking/apuesta. Se excluye matemáticamente un vértice en origen y se explicita ambigüedad antipodal.

Grid n=3..30, 500 réplicas por celda, 244 familias gaussianas independientes con escala común, seed202611110537. Benchmarks NO emparejados a varianzas familiares de casos: iid; RW; RW suavizada por kernel Gauss ancho físico0.08 del intervalo; cuatro modos cos(k*pi*(i+.5)/n), coeficientes gaussianos por familia y amplitudes1/k (LF1) o1/k² (LF2), k≤min(4,n−1) para evitar alias. Cada falsa recibe su propio PCA. Se guardan giro/rho, mediana y bandas2.5–97.5%; sin elegir muestras por resultado.

Aceleración algebraica permitida para magnitudes invariantes: top2 eigen de Gram centrada CC^T, o de C^T C si F<N. Se verifica contra SVD fiel, error<=1e-7 en giro/ratio para muestras no degeneradas. No se usa orientación para definir otra forma.

Verificaciones deterministas: n3 no colineal giro180..360; n4 contraejemplo con giro arbitrariamente pequeño; n≥5 giro0; familia binomial centrada que aproxima180*(n−1); cos1/cos2 y parábola con fórmula finita; ejemplos mismo conjunto/rho pero otro orden/giro, incluidos caminos suaves. Comparar giro vs curvatura mediante identidad integral donde r>0.

Límites: no existe único límite universal n→∞. Separar densificar una curva fija de crear muestras iid nuevas. Referencia iid angular isotrópica sin centrado estimado: CLT de incrementos uniformes. Verificar numéricamente escala sqrt(n) tras proyección en2D y244D sin vender esa simulación como demostración general. Para RW el centro y PCA se recalculan sobre intervalo completo; no usar sin más teoremas de winding alrededor de un origen fijo. Con origen evitado y subespacio estable, densificación converge al giro de la curva límite; puede ser aleatorio.

Población F→∞ de RW: covarianza centrada inversa del Laplaciano de cadena, modos cos(k*pi*(i+.5)/n), razón eigen2/eigen1=1/[4*cos²(pi/2n)]. Comparar numéricamente fórmula y límite n∞ 180+2atan(1/2)=233.130°. No confundir límite conjunto F∞ con fijo F244. Para LF1/LF2 límites233/208 dependen del espectro. Kernel suavizado: aproximación determinista F∞ en n30,64,128,256,512.

Asintótico numérico: iid2D n30,60,120,240,480,960,1920 con1000réplicas; iid244D n30,60,120,240 con120réplicas; RW244D acopladas por refinamiento n17,33,65,129,257,100caminos. No se afirma que esto demuestre todo límite.

Casos: cinco crudo_P existentes más Napoleón CSV y Hawking7 CSV: siete trazas, seis personas, no independientes. Ratio lambda2/lambda1 desde scores proyectados, no amplitud; amplitud=sqrt(ratio). CSV no permiten varianza explicada respecto a244 familias. Rangos frente a los benchmarks isotrópicos; además guardar rangos RW/iid previos emparejados para los cinco raw. Fórmulas cos/parábola son modelos restringidos, no una ley rho→giro. Autoresponder sin push.
