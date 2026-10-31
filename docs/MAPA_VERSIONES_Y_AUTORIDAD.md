# Mapa de versiones y autoridad — Motor U6 / V15.3 / U7

Corte: 2026-10-31. Fuente operativa: este repositorio en \`main\`.

## Componentes y nombres

| Capa | Identificador | Autoridad/estado |
|---|---|---|
| Motor canónico | \`motor/Engine_V5_CANONICO_SOLO.py\` | Activo y protegido. SHA-256 \`665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082\`, 30,507 bytes. |
| Catálogo canónico | \`motor/patterns_final_v14.json\` | Activo y protegido. 244 patrones; SHA-256 \`d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1\`. |
| Selección física | \`motor/ACTIVE_ENGINE_SELECTION.json\` y \`motor/CANDADO_ENGINE.json\` | Identifican Engine V5 como el componente canónico que corre. El hash antiguo \`e5d9...\` (24,944 bytes) no está presente y está expresamente prohibido. |
| Runner integrado | V15.3 / \`MOTOR_V15_3_UNICO_20260927.py\` | Capa de orquestación/ejecución, distinta del motor canónico V5. En F006 el módulo ejecutado tuvo SHA-256 \`23cd6749a2cce0da555fec3306c6ab7a44cedef429c319673d29fae6468b1f19\`. |
| Módulo nativo | \`MOTOR_V15_3_NATIVO_V0_9_UNICO.py\` | Módulo de la misma corrida F006; SHA-256 \`dac5599921d2f5629bfc15f3468a23f2390b931204752dfe99417fe84482b841\`. |
| Harness U6 | \`motor/u6/run_u6.sh\` | Ejecución de paquete con dependencias del workspace; conserva rutas absolutas específicas. No es un runner portátil para Android ni para cualquier máquina sin el workspace. |
| Herramienta U7 | \`u7/confianza_apuesta_u7.py\` | Herramienta lateral de confianza; no reemplaza ni decide el motor canónico. |

## Cómo interpretar los hashes

- \`665c39a2...\` es el SHA-256 del archivo físico del motor canónico V5.
- \`d827dcc3...\` es el SHA-256 del catálogo de 244 patrones.
- \`48333cd11b9234f1\` es el \`hash_candado/CANON_HASH\` usado por la capa V15.3 en los registros históricos; **no** es el SHA-256 del archivo Engine V5.
- El hash antiguo \`e5d9ab3a...\` corresponde a una compilación de 24,944 bytes ausente del paquete y no debe confundirse con el motor activo.

## Reglas

1. No modificar el motor V5 canónico ni \`patterns_final_v14.json\`.
2. Toda experimentación va en runner/sidecar/lateral con nombre nuevo y commit propio.
3. No llamar “Motor V15.3” al archivo canónico ni “Engine V5” al runner integrado: son capas distintas.
4. Un resultado de V15.3 debe registrar también los hashes del Engine V5 y del catálogo usados.
5. El soporte relativo, porcentaje de relleno y rank_fusion no son probabilidades calibradas.
6. Las páginas antiguas de Notion que describen V15.1 o el hash \`e5d9...\` son referencias históricas; prevalecen los archivos de selección/candado de este repositorio.

## Fuentes de verificación

- \`motor/ACTIVE_ENGINE_SELECTION.json\`
- \`motor/CANDADO_ENGINE.json\`
- \`motor/REGLAS.md\`
- Recibo de ejecución F006 R7 y \`F006_TRAZA_V2_R7_MANIFIESTO_ARTIFACTO.json\`
