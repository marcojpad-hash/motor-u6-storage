# Implementación lateral — Continuidad TORTUGAS U6

**Fecha:** 2026-10-24  
**Base:** `U6_MOTOR_TRABAJO_ABIERTO_20261020_R1.zip`  
**Alcance:** copia de trabajo U6; no modifica el motor canónico ni el catálogo de 244 patrones.

## Cambios aplicados

1. El serializador ya no convierte un `null` genérico en `TORTUGAS`. Los datos ausentes quedan clasificados como `DATO_AUSENTE_REQUIERE_CLASIFICACION`; las huellas de origen faltantes como `HUELLA_ORIGEN_NO_DISPONIBLE`; los no finitos como `VALOR_NO_FINITO_REQUIERE_REMEDICION`.
2. El recibo distingue `COMPLETED`, `COMPLETED_WITH_METADATA_GAP`, `INCOMPLETE_OUTPUT_DATA`, `INCOMPLETE_NONFINITE_OUTPUT` e `INCOMPLETE_REQUIRED_EXTERNAL_SEARCH`.
3. Se añadió una compuerta de continuidad: cuando la resolución terminal sigue en latencia/empate o la ruta exige TORTUGAS y esta falló/no se ejecutó, la salida pasa a `PAUSADA_REANUDABLE`, la apuesta final no se autoriza y se escribe un checkpoint con input, hashes, snapshot de resultado, hipótesis y contrato de reanudación. Código de salida 6.
4. La CLI no informa `ok=true` si existen faltantes, no finitos o pausa de continuidad. Los defectos de datos devuelven código no cero.
5. Se añadieron pruebas unitarias para distinguir ausencia de datos y TORTUGAS, clasificación de recibos, compuerta de pausa y cierre operativo validado.

## Verificación

- Suite completa: **99 passed, 2 skipped, 0 failed**. Los dos skips son referencias históricas ausentes (motor 0.5.0 y fixture histórico Bezos); no se sustituyeron con datos inventados.
- Preflight de integridad: **OK**.
- Hash motor canónico: `665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082` (sin cambios).
- Hash catálogo 244 patrones: `d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1` (sin cambios).

## Corrida real de humo

Caso: `CASO_NUEVO_20261013_01_CATALOG_REPAIR_R2`, tres cortes.  
H1: `13_enemistad_de_parientes`.  
H2: `social_08_girard_mimesis_y_chivo_expiatorio`.  
TORTUGAS: ejecutado.  
JSON final: 0 `null`, 0 valores no finitos.  
Recibo: `COMPLETED_WITH_METADATA_GAP`; código de salida **5**, `ok=false`.

Único faltante detectado: `$.matriz_mortalidad_z90.data_table_sha256`. Se conserva como incidencia de procedencia, no se convierte en TORTUGAS ni se oculta. La decisión operativa se produjo, pero el artefacto no se declara íntegramente limpio hasta resolver esa huella.

## Límites de esta entrega

- La compuerta de pausa y el formato del checkpoint están cubiertos por pruebas unitarias; la corrida real disponible no activó la pausa porque TORTUGAS sí se ejecutó. Por tanto, el camino de reanudación en un caso real de fallo de TORTUGAS aún requiere una prueba de integración que provoque esa condición y compruebe la reapertura desde el checkpoint.
- La corrección no afirma que TORTUGAS siempre pueda producir evidencia discriminante. Si la vectorización adicional falla, se pausa y conserva el estado en vez de inventar una apuesta.
- No se alteraron `Engine_V5_CANONICO_SOLO.py` ni `patterns_final_v14.json`.
