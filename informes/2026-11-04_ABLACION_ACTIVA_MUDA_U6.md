# U6 — ablación controlada de filas ACTIVA_MUDA

**Fecha:** 2026-11-04  
**Repositorio:** marcojpad-hash/motor-u6-storage  
**Rama:** experimental/u6-unificado-activo-20261104  
**Commit probado:** 335d2afbd365fd193d73e4ae35c1c30eeb65d741  
**Workflow:** U6 unificado experimental — smoke y suite completa  
**Run:** [41881474178](https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/41881474178) — SUCCESS  
**Artifact:** U6_ACTIVA_MUDA_ABLATION_EVIDENCE — ID 13349688124

## Resultado

Se ejecutaron 41 ablaciones individuales: 21 sobre Courbet y 20 sobre Haber.

| Medida | Resultado |
|---|---:|
| Casos | 2 |
| Filas registradas como ACTIVA_MUDA | 84 |
| Ablaciones con switch confirmado | 41/41 |
| Ablaciones con errores críticos | 0 |
| Cambios en H1/H2 | 0 |
| Cambios en el conjunto u orden de candidatas | 0 |
| Cambios en puntajes rank_fusion | 0 |
| Máxima variación absoluta de rank_fusion | 0.0 |
| Filas sin switch independiente | 27 |

**Resultado acotado:** en estos dos casos, ninguno de los componentes desactivados cambió H1, H2, el orden de candidatas ni sus puntajes rank_fusion. No demuestra que nunca aporten en otros casos ni que no tengan valor diagnóstico, de control o de trazabilidad.

## Método

1. Se ejecutó una búsqueda viva por caso con ddgs: 8 resultados en Courbet y 8 en Haber.
2. Se congeló la lista de fuentes devuelta por cada búsqueda.
3. Cada ablación reutilizó la lista correspondiente como fixture estático; no volvió a consultar la web.
4. Se desactivó un switch por corrida. Cada ejecución tuvo un identificador distinto y ledger CEB propio.
5. Se compararon H1, H2, candidatas, orden y puntajes rank_fusion.
6. Se verificó que el switch solicitado quedara efectivamente apagado y que la corrida terminara sin errores críticos.

Fuentes congeladas:
- Courbet: query SHA-256 deda23a39cdff964f798108b3ac18e05839a3fc8d16408cfaa5c565c5e57f3e8; 8 fuentes; fixture SHA-256 4f407b9dc96b24fbf3b789ffe707560b35694363cbcda27244b90e46cdfc6252.
- Haber: query SHA-256 559cda1b30aa05e76c383a439545fedbade2b29d02124016e26e1d67a3dcee84; 8 fuentes; fixture SHA-256 a4ba3b5d2f83765f2f55fcc8f716241790e5960b81e6cbaf87169f493533f38f.

Los 41 recibos de replay fueron EXECUTED_FIXTURE. Las 41 corridas quedaron en EXECUTION_CONFIRMED. Los ledgers CEB de las ablaciones contienen 919,025 eventos en conjunto.

## Caso Courbet

**Base:** H1 30_ambicion; H2 20_sacrificio_por_un_ideal.

| Componente desactivado | Switch | H1/H2 | Orden | Puntajes |
|---|---:|---:|---:|---:|
| trayectoria_hosteleria | confirmado | sin cambio | sin cambio | sin cambio |
| plugin_metodo_rigor (alimentado) | confirmado | sin cambio | sin cambio | sin cambio |
| plugin_arquetipos_dinamicos | confirmado | sin cambio | sin cambio | sin cambio |
| plugin_pregunta_dirigida (verificado) | confirmado | sin cambio | sin cambio | sin cambio |
| predictor_vecinos_prefijo | confirmado | sin cambio | sin cambio | sin cambio |
| sombrero_blanco_entrada | confirmado | sin cambio | sin cambio | sin cambio |
| familias_tokens_puente | confirmado | sin cambio | sin cambio | sin cambio |
| guardian_entrada_autoevidencia | confirmado | sin cambio | sin cambio | sin cambio |
| resolucion* | confirmado | sin cambio | sin cambio | sin cambio |
| area_tokens | confirmado | sin cambio | sin cambio | sin cambio |
| luces_gemini_packs | confirmado | sin cambio | sin cambio | sin cambio |
| amantes_arquetipos | confirmado | sin cambio | sin cambio | sin cambio |
| cuerpo_arco | confirmado | sin cambio | sin cambio | sin cambio |
| alias_reactivacion | confirmado | sin cambio | sin cambio | sin cambio |
| familias_gloria_sacro | confirmado | sin cambio | sin cambio | sin cambio |
| tusi_par | confirmado | sin cambio | sin cambio | sin cambio |
| schrodinger_transport | confirmado | sin cambio | sin cambio | sin cambio |
| filtro_identidad_zoom | confirmado | sin cambio | sin cambio | sin cambio |
| protocolo_orden0 (verificado) | confirmado | sin cambio | sin cambio | sin cambio |
| aquiles_ancla_estricto | confirmado | sin cambio | sin cambio | sin cambio |
| sombrero_blanco_salida | confirmado | sin cambio | sin cambio | sin cambio |

## Caso Haber

**Base:** H1 30_ambicion; H2 schwartz_07_logro.

| Componente desactivado | Switch | H1/H2 | Orden | Puntajes |
|---|---:|---:|---:|---:|
| trayectoria_hosteleria | confirmado | sin cambio | sin cambio | sin cambio |
| plugin_metodo_rigor (alimentado) | confirmado | sin cambio | sin cambio | sin cambio |
| plugin_arquetipos_dinamicos | confirmado | sin cambio | sin cambio | sin cambio |
| plugin_pregunta_dirigida (verificado) | confirmado | sin cambio | sin cambio | sin cambio |
| predictor_vecinos_prefijo | confirmado | sin cambio | sin cambio | sin cambio |
| sombrero_blanco_entrada | confirmado | sin cambio | sin cambio | sin cambio |
| familias_tokens_puente | confirmado | sin cambio | sin cambio | sin cambio |
| guardian_entrada_autoevidencia | confirmado | sin cambio | sin cambio | sin cambio |
| resolucion* | confirmado | sin cambio | sin cambio | sin cambio |
| area_tokens | confirmado | sin cambio | sin cambio | sin cambio |
| luces_gemini_packs | confirmado | sin cambio | sin cambio | sin cambio |
| amantes_arquetipos | confirmado | sin cambio | sin cambio | sin cambio |
| cuerpo_arco | confirmado | sin cambio | sin cambio | sin cambio |
| alias_reactivacion | confirmado | sin cambio | sin cambio | sin cambio |
| familias_gloria_sacro | confirmado | sin cambio | sin cambio | sin cambio |
| schrodinger_transport | confirmado | sin cambio | sin cambio | sin cambio |
| filtro_identidad_zoom | confirmado | sin cambio | sin cambio | sin cambio |
| protocolo_orden0 (verificado) | confirmado | sin cambio | sin cambio | sin cambio |
| aquiles_ancla_estricto | confirmado | sin cambio | sin cambio | sin cambio |
| sombrero_blanco_salida | confirmado | sin cambio | sin cambio | sin cambio |

*t* La desactivación de resolucion se incluyó como control adicional: su estado crudo es RESUELTO_OPERACIONALMENTE y no debería contarse como ACTIVA_MUDA.

## Qué representan las 42 filas por caso

No son 42 componentes decisores independientes.

- 13 filas proceden del registro del motor y 29 del hub lateral.
- Las 13 filas de origen motor declaran alimenta_predictor=false y alimenta_H=false.
- Las 42 filas tienen can_decide_H=false.
- Ocho registros de verificación del motor se agruparon con el switch del componente lateral correspondiente; no se contaron como ablaciones separadas.
- Las filas restantes sin switch independiente son registros de auditoría, controles manuales, declaraciones, inventario o componentes absorbidos/no aplicables.

### Cuatro estados crudos mal clasificados

El registro asignó ACTIVA_MUDA por el fallback de _MAPA_ESTADO a cuatro estados crudos que tienen otro significado:

| Pieza | Estado crudo |
|---|---|
| plugin_guardia_no_cruce.py | ABSORBIDO_EN_GUARDIA_TRANSVERSAL |
| cameo_to_244_adapter_v1.py | NOT_APPLICABLE |
| matriz_clases | PRESENTE |
| resolucion_operativa_terminal_017 | RESUELTO_OPERACIONALMENTE |

Por tanto, las 42 filas por caso están infladas: cuatro no son ACTIVA_MUDA en sentido estricto. El mapa de estados pertenece al motor V15.3 protegido por el protocolo CEB; no se modificó. Se deja registrada la inconsistencia para una corrección autorizada.

### Filas sin ablación independiente

Se excluyeron de la matriz individual porque no representan un módulo independiente con switch propio:

- plugin_guardia_no_cruce.py: absorbido en la guardia transversal.
- cameo_to_244_adapter_v1.py: no aplicable; falta el mapeo correspondiente.
- matriz_clases: registro de inventario/presencia.
- plugin_sombrero_blanco_token.py: declaración, no una ejecución independiente.
- traza_campo_244_dedupe, plugin_sombrero_blanco_token (declaración) y n_piezas (verificado): controles/manuales.
- Las filas verificado:* son recibos de auditoría de piezas ya representadas; no son ejecuciones nuevas.

Haber contiene una fila de auditoría adicional: verificado:sidecar_caldero_busqueda_arquetipos.py.

## Trazabilidad e integridad

- Artifact: 45 ledgers CEB y 45 archivos StinkBox, correspondientes a 2 smokes, 2 baselines de matriz y 41 ablaciones.
- Se verificaron 45 case_id únicos y coincidencia entre cada case_id y su archivo StinkBox.
- Los directorios StinkBox quedaron anidados por acumulación de la variable de entorno entre llamadas; cada corrida escribió un archivo propio y no se detectó reutilización de archivo. Es una cuestión de higiene del runner, no una variación observada en las salidas.
- Suite posterior a la matriz: 159 passed, 2 skipped.
- Smokes Courbet y Haber: 52/52 componentes presentes y 0 errores críticos.
- Engine V5 SHA-256: 665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082.
- Catálogo 244 SHA-256: d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1.

No se modificaron Engine V5, el motor V15.3 ni el catálogo 244. La matriz, el runner experimental y su workflow permanecen en la rama experimental; no se promovieron a main.
