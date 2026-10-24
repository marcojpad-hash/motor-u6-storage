# Historial evolutivo U6 — compacto

Fecha de corte: 2026-10-20. Este documento sustituye la carga rutinaria de resultados JSON completos. Conserva cambios, motivos, salidas principales y huellas de origen; los ZIP originales siguen siendo la evidencia bruta de archivo.

## Evolución

1. **Base U6_PARCHE V2.** Se conservan el espectro V2 y el guardián de sesgo.
2. **Parche de publicación V0.4.** El motor nativo publica los tableros P/A/C que utilizó para calcular R732, en vez de recalcularlos con una nueva llamada Monte Carlo. La comparación de valores internos puede variar en decimales derivados, pero no cambió H1/H2, el orden de candidatos ni el régimen de la apuesta en los dos casos comparados.
3. **Unificación lateral.** Se incorporan cuatro laterales de solo lectura: espectro/guardián de sesgo, factores latentes, convergencia entre tableros y geometría recursiva/diagnóstico helicoidal. No deciden H ni reordenan candidatos.
4. **Compactación 2026-10-20.** Se separan el motor ejecutable, el código y las dependencias laterales, y los reportes de evolución. Se retiran de los paquetes cotidianos resultados completos duplicados, ledgers JSONL voluminosos y salidas históricas; se conservan sus resúmenes y hashes de origen. La evidencia original no se altera.

## Motivo técnico de la compactación

Los resultados grandes repetían campos ajenos al resumen de una corrida: `ceb`, `features`, auditorías terminales, estados de guardianes y metadatos de componentes. Los ledgers de eventos crecían hasta 8–11 MB por archivo. Para consultar evolución no hace falta recargar esos bloques cada vez: bastan las decisiones, las métricas principales, el estado de ejecución, los cambios y las huellas. Los originales se mantienen en los ZIP recibidos como archivo histórico, fuera del paquete operativo.

## Reglas de conservación

- El motor canónico y `patterns_final_v14.json` no se modifican.
- Los laterales no escriben H1/H2 ni el ranking del motor.
- Los fixtures se reducen a los campos que requieren las pruebas, sin cambiar sus datos numéricos usados por el diagnóstico.
- Cada reporte de corrida debe registrar: caso, fecha, versión/hash del motor y catálogo, H1/H2, R732 resumido, Monte Carlo, laterales ejecutados, incidencias y hashes de los artefactos de origen.
- Los resultados completos y ledgers quedan en archivo de evidencia solo cuando se necesitan para auditoría; no se copian a cada entrega de motor.


## 2026-10-20 — StinkBox persistente y candidatos Black Mirror

- Integrado `stinkbox_registry.py` con `correr_estandar.py`: resolución de almacenamiento externo y autoimportación después de corridas estándar y T+1.
- La corrida de humo de un corte escribió el resultado y el recibo; el registro importó 7 eventos y conservó el total de 290 tokens únicos de la línea base porque los eventos ya correspondían a tokens conocidos.
- Añadidos 18 candidatos documentales Black Mirror/ficción de IA a un registro separado, sin contarlos como tokens observados ni incorporarlos al catálogo canónico.
- Corregida equivalencia por subcadena en `MOTOR_V15_3_NATIVO_V0_9_UNICO.py`; una subcadena compartida ya no crea equivalencia.
- Suite: 82 passed, 2 skipped. La prueba de humo no es calibración: búsqueda externa obligatoria sin resultados verificables.

- Conteo del registro afinado: si el mismo caso/corte/token llega por el registro de descubrimiento y por el archivo de StinkBox, conserva ambas evidencias pero cuenta una sola observación.


## 2026-10-20 — Reejecución con puente de búsqueda ciega

- Se ejecutó el caso de Temístocles con tres cortes y una consulta ciega construida desde los tokens del último corte. La búsqueda web conectada aportó cinco fuentes; no se incluyó identidad del caso en la consulta.
- Resultado de esta variante: H1 `13_enemistad_de_parientes`, H2 `30_ambicion`, cierre `RESUELTO_OPERACIONALMENTE`; 7.273 simulaciones Monte Carlo registradas. No es evaluación prospectiva ni calibración porque no existe revelado T+1 asociado.
- La invocación excedió el límite de 200 segundos antes de escribir la etapa automática de StinkBox en el recibo. Se recuperaron e importaron manualmente los artefactos de tokens a la memoria persistente y se guardaron el input, recibo y resumen compacto.
- Se registraron 54 cadenas únicas nuevas, todas vinculadas al vocabulario de la búsqueda externa. No son 54 familias faltantes. No se detectaron nuevos tokens explícitos fuera de catálogo en esa corrida; `oficio` sigue pendiente desde el histórico.

- Añadido checkpoint automático de StinkBox inmediatamente después de la corrida primaria y antes de los análisis retenidos. Esto evita perder el índice de tokens si una etapa posterior excede el tiempo disponible.
