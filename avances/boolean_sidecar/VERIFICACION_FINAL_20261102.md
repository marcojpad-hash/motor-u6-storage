# Verificación final del experimento Booleano — 2026-11-02

## Ejecución final desde el módulo lateral
- Workflow: [41418728898](https://github.com/marcojpad-hash/motor-u6-storage/actions/runs/41418728898)
- Estado: success.
- Commit probado: `ccd0bb0cfa203b3b4bb5ac431fe318d4dc944ad7`.
- Pasos exitosos: ejecutar el sidecar, verificar 244 familias y los candados del motor/catálogo, verificar F007 y publicar el artefacto.

## F007: prueba de rechazo
Se ejecutó realmente:
`python -B casos/fabrica/fabrica.py preparar-z casos/fabrica/semillas_lote_F007.py casos/fabrica/destinos_lote_F007.py`

Resultado: rechazo esperado, código 1, sin escribir directorios de casos en la cola. Se detectó `familias` ausente en los ocho destinos:
- F007_01_VAN_GOGH
- F007_02_GAUGUIN
- F007_03_CURIE
- F007_04_ROOSEVELT
- F007_05_CHAPLIN
- F007_06_FORD
- F007_07_LENIN
- F007_08_PICASSO

No se inventaron familias ni se abrió el desenlace para el motor. F007 queda bloqueado hasta que el custodio complete esa clasificación y la compuerta Z acepte el lote.

## Resultado experimental que permanece vigente
La comparación justa se hizo sobre 40 casos sellados con `returncode=0` de F001–F005. Cinco casos pausados/no sellados quedaron fuera. F006 es una reevaluación de Courbet ya incluido en F005, no una observación independiente.

- Cobertura Booleano: 40/40 casos (100%).
- Reducción media del espacio de candidatas: 5.96%.
- Candidatas que permanecen: 229.47 de 244 en promedio.
- Familias reales selladas: 158; excluidas por el filtro: 11.
- Motor base, mismos 40 casos: H1 20%; H2 12.5%; set abierto 30%; apuesta de escenario principal 25%.

Conclusión: no integrar. El filtro reduce poco y puede eliminar etiquetas reales; no demuestra mejora predictiva. Mantener aislado y no usarlo para descartar familias del motor principal.

## Integridad
Los SHA-256 de `motor/motor/Engine_V5_CANONICO_SOLO.py` y `motor/motor/patterns_final_v14.json` se comprobaron en CI contra los candados declarados. Ambos permanecieron intactos.
