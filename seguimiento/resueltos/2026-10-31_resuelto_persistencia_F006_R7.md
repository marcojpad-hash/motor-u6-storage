# Resuelto: persistencia del artifact F006 TRAZA V2 R7

- **Incidencia:** el run F006 R7 existía en GitHub Actions, pero su evidencia compacta no estaba incorporada al repositorio. \`resultados.jsonl\` terminaba en F005.
- **Causa:** el workflow conservó el ZIP como artifact externo; no persistió los resúmenes al registro versionado.
- **Acción:** descargado artifact 12989457446 del run 41081591816; verificado ZIP SHA-256 \`0ef1887f395e229e77f1ea6b37ae9025fc23d63c6e3789fedfa7489913871ffb\`. Se guardaron compromiso, resumen, evaluación, registro de calibración y manifiesto en \`casos/fabrica/lotes/\`. Se añadió la fila F006 a \`casos/resultados/resultados.jsonl\`.
- **Criterio muestral:** F006 reevalúa el mismo \`CAL_F005_01_COURBET\` con el mismo hash de entrada. No se añadió a los denominadores acumulados; se documentó como reevaluación en \`CALIBRACION_ACUMULADA.md\`.
- **Prueba de integridad:** el ZIP se pudo abrir; sus hashes de miembro se registraron; recibo reporta COMPLETED, motor/patrones MATCH, Monte Carlo 9/9 convergente, CEB gates OK, manifest 304/304 y plugin lock 108/108.
- **No ejecutado en esta auditoría:** no se lanzó una corrida nueva ni se volvió a ejecutar el motor. No se modificó el motor canónico ni los patrones.
- **Commits:** 20d85d9, 6779fc1, 6dc9420, 092792c, 36684bf, 9d48310, a2505e1 (ver historial de main).
- **Estado:** persistencia resuelta; rendimiento de destino sigue abierto.
