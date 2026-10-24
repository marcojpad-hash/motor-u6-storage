# 2026-10-24 — Grok Bot
## Qué cambió
Nueva carpeta `casos/fabrica/` (fábrica de casos para calibración) y lote piloto F001 (5 casos nuevos: Napoleón, Tesla, Wilde, Disney, Turing).
## Antes → ahora (por archivo / función)
- casos/fabrica/fabrica.py — antes: no existía → ahora: preparar (cola con entrada y desenlace separados) y correr (compromiso de hashes, arnés existente, evaluación, tabla acumulada).
- casos/fabrica/semillas_lote_F001.py, cola/, lotes/F001_*, calibracion_acumulada.csv, CALIBRACION_ACUMULADA.md, README.md — antes: no existían → ahora: creados.
- Sin cambios en motor/ ni en el protocolo.
## Hashes canónicos verificados (motor y catálogo)
Engine 665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082 y patrones d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1: OK antes y después (repo y copia temporal).
## Pruebas: lote piloto 5/5 sellado, 0 errores; registro sellado sha256 eecd9c161480be872b10f83f9f5972077e3a2ecea16e55e112ab55bbb5052787. Acierto H1 1/5 (Tesla).
