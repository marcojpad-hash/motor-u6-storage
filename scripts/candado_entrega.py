#!/usr/bin/env python3
"""Candado de entrega de corridas del motor U6 (motor-u6-storage).

Valida un paquete de entrega de corridas ANTES de aceptarlo/guardarlo en el
repo. Si un criterio no se cumple, el paquete NO se guarda y el candado dice
EXACTAMENTE qué criterio falló. La única razón para no guardar es no cumplir
los criterios; nunca es un vago «no se pudo guardar».

Uso:
  python3 scripts/candado_entrega.py <DIR_ENTREGA> [--repo RUTA_REPO]

  <DIR_ENTREGA>  Carpeta del paquete, p. ej. motor/runs/F001_F002_20261111/
  --repo         Raíz del repo donde viven los archivos de protocolo que la
                 entrega dice haber leído (por defecto: se detecta subiendo
                 desde DIR_ENTREGA hasta encontrar CONTRATO_CARPETAS.md).

Salida:
  exit 0  CANDADO_ENTREGA: PASA — la entrega cumple todos los criterios.
  exit 1  CANDADO_ENTREGA: BLOQUEADO — NO SE GUARDA. Lista exacta de cada
          criterio incumplido (qué archivo falta, qué regla no se siguió,
          qué lectura no se demostró).
  exit 2  Error de uso (argumentos inválidos).

Criterios que verifica (fuentes: casos/REGLAS.md, CONTRATO_CARPETAS.md,
casos/fabrica/README.md, PROTOCOLO_EJECUCION_Y_LECTURA_LLM.md §§3-4, y la
estructura de la entrega F001/F002_20261111):

  A. Estructura del paquete (archivos requeridos):
     - MANIFIESTO.json, README.md, TABLA_VALORES_COMPLETA.md, LECTURA.json.
     - MANIFIESTO con `lote` y `casos` (lista no vacía); cada caso con
       case_id, result_sha256 (64 hex), result_bytes (>0), entrada_sha256
       (64 hex) y receipt_sha256 (64 hex); sin case_id duplicados.
     - Por cada caso: <CASO>_INTERPRETABLE.json, <CASO>_RECIBO_EJECUCION.json
       y <CASO>_entrada.json. Sin archivos de caso huérfanos (fuera del
       manifiesto).
     - README.md menciona el protocolo (la entrega declara bajo qué
       regla/excepción se entrega).

  B. Contenido por caso:
     - INTERPRETABLE.json: JSON válido; salida_interpretable con H1 y H2
       (cada uno con `familia`); conjunto_hipotesis_abiertas no vacío y
       cada hipótesis con trazabilidad_geometrica (regimen, senal_multiescala,
       micro, meso, macro) — regla «Todo dato es un dato»: picos, mesetas,
       valles y descensos se conservan, no solo H1/H2; monte_carlo y
       predictive_validation presentes; result_completo_sha256 y
       entrada_sha256 coinciden con el MANIFIESTO del caso.
     - RECIBO_EJECUCION.json: JSON válido con `status` declarado (el estado
       de ejecución; PROTOCOLO §3: no inventar un campo que el runner no
       genera; si falta, se anota NO REGISTRADO, no se rellena).
     - entrada.json: JSON válido; case_id coincide con el archivo; `question`
       en prosa no vacía; `cuts` lista no vacía y cada corte con `hecho` en
       prosa no vacío; el SHA-256 real del archivo coincide con el
       entrada_sha256 del MANIFIESTO; igual para el RECIBO.

  C. Tabla completa:
     - TABLA_VALORES_COMPLETA.md menciona cada case_id del MANIFIESTO
       (ningún caso fuera de la tabla).

  D. Lectura demostrada (LECTURA.json):
     - Lista no vacía de archivos de protocolo/especificación leídos; cada
       entrada con `ruta` y al menos uno de `sha256` o `fecha`.
     - Cada `ruta` existe en el repo (--repo).
     - Si trae `sha256`, coincide con el SHA-256 actual del archivo.
     - README.md o REVISION.md menciona el nombre base de cada ruta leída
       (la entrega cita lo que leyó).

Formato de LECTURA.json:
  {
    "entrega": "F001_F002_20261111",
    "fecha_lectura": "2026-11-11",
    "lecturas": [
      {"ruta": "casos/REGLAS.md", "sha256": "<64 hex>", "reglas": ["regla 6"]},
      {"ruta": "CONTRATO_CARPETAS.md", "sha256": "<64 hex>",
       "reglas": ["casos/: nunca corridas completas"]},
      {"ruta": "PROTOCOLO_EJECUCION_Y_LECTURA_LLM.md", "sha256": "<64 hex>",
       "reglas": ["§3 recibo mínimo", "§4 todo dato es un dato"]}
    ]
  }

Nota de conflicto: casos/REGLAS.md regla 6, CONTRATO_CARPETAS.md y
casos/fabrica/README.md dicen que nunca se sube la corrida completa al repo
(solo un resumen en casos/resultados/resultados.jsonl). Marco aclaró
(2026-11-11 ~18:07 CST) la forma que adopta: resumen de una línea en
`resultados.jsonl` (para no saturar el motor) Y corridas completas en el
apartado separado `motor/runs/` para el historial. (El StinkBox es el
repositorio del motor para los TOKENS que salen de las corridas, no para las
corridas en sí — corrección de Marco 18:08 CST.) Este
candado valida el paquete de `motor/runs/<LOTE>_<FECHA>/` bajo esa forma.
Los tres archivos de protocolo todavía dicen lo contrario y hay que
actualizarlos para que la regla quede escrita; el candado solo exige que la
entrega declare su base en README.md (criterio A10).

No toca Engine_V5_CANONICO_SOLO.py ni patterns_final_v14.json. Solo
biblioteca estándar.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HEX64 = re.compile(r"^[0-9a-f]{64}$")

# Archivos de lote requeridos (además de los 3 por caso).
LOTE_REQUERIDOS = ["MANIFIESTO.json", "README.md", "TABLA_VALORES_COMPLETA.md", "LECTURA.json"]

# Campos mínimos de trazabilidad geométrica por hipótesis (picos/mesetas).
TRAZA_MIN = ["regimen", "senal_multiescala", "micro", "meso", "macro"]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(p: Path):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def detectar_repo(delivery: Path) -> Path | None:
    for parent in [delivery, *delivery.parents]:
        if (parent / "CONTRATO_CARPETAS.md").exists():
            return parent
    return None


class Candado:
    def __init__(self, delivery: Path, repo: Path | None):
        self.delivery = delivery
        self.repo = repo
        self.fallos: list[str] = []
        self.pasados = 0
        self.manifiesto: dict | None = None
        self.casos: list[dict] = []
        self.readme_text = ""
        self.revision_text = ""

    def falla(self, codigo: str, mensaje: str) -> None:
        self.fallos.append(f"[{codigo}] {mensaje}")

    def ok(self) -> None:
        self.pasados += 1

    # ---------- A. Estructura ----------
    def check_estructura(self) -> None:
        d = self.delivery
        # A1: MANIFIESTO.json existe y es JSON válido.
        man_path = d / "MANIFIESTO.json"
        if not man_path.exists():
            self.falla("A1", "Falta MANIFIESTO.json en la raíz del paquete: "
                             "sin manifiesto no se sabe qué casos trae la entrega.")
            return
        try:
            self.manifiesto = load_json(man_path)
        except Exception as e:
            self.falla("A1", f"MANIFIESTO.json no es JSON válido: {e}")
            return
        self.ok()
        # A2: README.md existe y no está vacío.
        readme = d / "README.md"
        if not readme.exists() or readme.stat().st_size == 0:
            self.falla("A2", "Falta README.md (o está vacío) en la raíz del paquete: "
                             "toda entrega necesita su README.")
        else:
            self.ok()
            self.readme_text = readme.read_text(encoding="utf-8", errors="replace")
        # A3: TABLA_VALORES_COMPLETA.md existe y no está vacío.
        tabla = d / "TABLA_VALORES_COMPLETA.md"
        if not tabla.exists() or tabla.stat().st_size == 0:
            self.falla("A3", "Falta TABLA_VALORES_COMPLETA.md (o está vacía): "
                             "la tabla con todos los valores es obligatoria.")
        else:
            self.ok()
        # A4: LECTURA.json existe (la evidencia de lectura se verifica en D).
        if not (d / "LECTURA.json").exists():
            self.falla("A4", "Falta LECTURA.json: el paquete no trae evidencia explícita "
                             "de lectura de protocolo/especificación. Debe listar los "
                             "archivos leídos con su ruta y sha256 o fecha "
                             "(ver scripts/CANDADO_ENTREGA.md).")
        else:
            self.ok()
        # A5: MANIFIESTO con lote y casos.
        if not isinstance(self.manifiesto, dict):
            self.falla("A5", "MANIFIESTO.json no es un objeto JSON.")
            return
        lote = self.manifiesto.get("lote")
        casos = self.manifiesto.get("casos")
        if not isinstance(lote, str) or not lote.strip():
            self.falla("A5", "MANIFIESTO.json no trae `lote` (texto no vacío).")
        elif not isinstance(casos, list) or not casos:
            self.falla("A5", "MANIFIESTO.json no trae `casos` (lista no vacía).")
        else:
            self.ok()
            self.casos = casos
        # A6/A7: cada caso con campos mínimos y sin duplicados.
        vistos: set[str] = set()
        for i, c in enumerate(self.casos):
            if not isinstance(c, dict):
                self.falla("A6", f"MANIFIESTO.casos[{i}] no es un objeto JSON.")
                continue
            cid = c.get("case_id")
            if not isinstance(cid, str) or not cid.strip():
                self.falla("A6", f"MANIFIESTO.casos[{i}] no trae `case_id` (texto no vacío).")
                continue
            if cid in vistos:
                self.falla("A7", f"MANIFIESTO trae case_id duplicado: {cid}.")
            vistos.add(cid)
            for campo in ("result_sha256", "entrada_sha256", "receipt_sha256"):
                v = c.get(campo)
                if not isinstance(v, str) or not HEX64.match(v):
                    self.falla("A6", f"Caso {cid}: MANIFIESTO.{campo} falta o no es "
                                     f"un SHA-256 hexadecimal de 64 caracteres.")
            rb = c.get("result_bytes")
            if not isinstance(rb, int) or rb <= 0:
                self.falla("A6", f"Caso {cid}: MANIFIESTO.result_bytes falta o no es "
                                 "un entero mayor que 0.")
        if not any(f.startswith("[A6]") or f.startswith("[A7]") for f in self.fallos):
            self.ok()
        # A8: archivos por caso presentes.
        for c in self.casos:
            if not isinstance(c, dict):
                continue
            cid = c.get("case_id")
            if not isinstance(cid, str) or not cid.strip():
                continue
            for sufijo in ("_INTERPRETABLE.json", "_RECIBO_EJECUCION.json", "_entrada.json"):
                if not (d / f"{cid}{sufijo}").exists():
                    self.falla("A8", f"Caso {cid}: falta el archivo {cid}{sufijo}.")
        if not any(f.startswith("[A8]") for f in self.fallos):
            self.ok()
        # A9: sin archivos de caso huérfanos (fuera del manifiesto).
        en_manifiesto = {c.get("case_id") for c in self.casos if isinstance(c, dict)}
        for p in sorted(d.glob("*_INTERPRETABLE.json")) + sorted(d.glob("*_RECIBO_EJECUCION.json")) + sorted(d.glob("*_entrada.json")):
            cid = p.name.split("_INTERPRETABLE.json")[0].split("_RECIBO_EJECUCION.json")[0].split("_entrada.json")[0]
            if cid not in en_manifiesto:
                self.falla("A9", f"Archivo huérfano fuera del MANIFIESTO: {p.name} "
                                 "(su case_id no está en MANIFIESTO.casos).")
        if not any(f.startswith("[A9]") for f in self.fallos):
            self.ok()
        # A10: README menciona el protocolo (declara su base).
        if self.readme_text and "protocolo" in self.readme_text.lower():
            self.ok()
        elif self.readme_text:
            self.falla("A10", "README.md no menciona el protocolo: la entrega no declara "
                              "bajo qué regla o excepción se entrega (ver nota de conflicto "
                              "en scripts/CANDADO_ENTREGA.md).")
        # REVISION.md (opcional, se usa para la cita de lectura en D5).
        rev = d / "REVISION.md"
        if rev.exists():
            self.revision_text = rev.read_text(encoding="utf-8", errors="replace")

    # ---------- B. Contenido por caso ----------
    def check_contenido(self) -> None:
        d = self.delivery
        for c in self.casos:
            if not isinstance(c, dict):
                continue
            cid = c.get("case_id")
            if not isinstance(cid, str) or not cid.strip():
                continue
            # B1-B3, B5: INTERPRETABLE.
            ip = d / f"{cid}_INTERPRETABLE.json"
            if ip.exists():
                try:
                    interp = load_json(ip)
                except Exception as e:
                    self.falla("B1", f"Caso {cid}: {cid}_INTERPRETABLE.json no es JSON válido: {e}")
                    interp = None
                if isinstance(interp, dict):
                    self.ok()  # B1
                    si = interp.get("salida_interpretable")
                    if not isinstance(si, dict):
                        self.falla("B2", f"Caso {cid}: INTERPRETABLE no trae `salida_interpretable`.")
                    else:
                        h1 = si.get("H1") or {}
                        h2 = si.get("H2") or {}
                        if not isinstance(h1, dict) or not h1.get("familia"):
                            self.falla("B2", f"Caso {cid}: salida_interpretable.H1 falta o no trae `familia`.")
                        elif not isinstance(h2, dict) or not h2.get("familia"):
                            self.falla("B2", f"Caso {cid}: salida_interpretable.H2 falta o no trae `familia`.")
                        else:
                            self.ok()  # B2
                        conj = si.get("conjunto_hipotesis_abiertas") or {}
                        hyps = conj.get("hipotesis") if isinstance(conj, dict) else None
                        if not isinstance(hyps, list) or not hyps:
                            self.falla("B3", f"Caso {cid}: conjunto_hipotesis_abiertas vacío o ausente: "
                                            "no se conserva la trazabilidad (picos/mesetas). "
                                            "Regla «Todo dato es un dato» (PROTOCOLO §4).")
                        else:
                            sin_traza = [h.get("familia", "?") for h in hyps
                                         if not isinstance(h, dict)
                                         or not isinstance(h.get("trazabilidad_geometrica"), dict)
                                         or any(k not in h["trazabilidad_geometrica"] for k in TRAZA_MIN)]
                            if sin_traza:
                                self.falla("B3", f"Caso {cid}: hipótesis sin trazabilidad geométrica "
                                                 f"completa ({TRAZA_MIN}): {', '.join(sin_traza)}. "
                                                 "Regla «Todo dato es un dato» (PROTOCOLO §4).")
                            else:
                                self.ok()  # B3
                    if "monte_carlo" not in interp:
                        self.falla("B4", f"Caso {cid}: INTERPRETABLE no trae `monte_carlo`.")
                    elif "predictive_validation" not in interp:
                        self.falla("B4", f"Caso {cid}: INTERPRETABLE no trae `predictive_validation`.")
                    else:
                        self.ok()  # B4
                    rcs = interp.get("result_completo_sha256")
                    if isinstance(rcs, str) and HEX64.match(rcs):
                        if rcs != c.get("result_sha256"):
                            self.falla("B5", f"Caso {cid}: INTERPRETABLE.result_completo_sha256 "
                                            f"({rcs[:16]}…) no coincide con MANIFIESTO.result_sha256 "
                                            f"({str(c.get('result_sha256'))[:16]}…).")
                        else:
                            self.ok()  # B5 (sha completo)
                    else:
                        self.falla("B5", f"Caso {cid}: INTERPRETABLE no trae result_completo_sha256 "
                                        "(SHA-256 de 64 hex del RESULT completo).")
                    es = interp.get("entrada_sha256")
                    if isinstance(es, str) and HEX64.match(es):
                        if es != c.get("entrada_sha256"):
                            self.falla("B5", f"Caso {cid}: INTERPRETABLE.entrada_sha256 no coincide "
                                            "con MANIFIESTO.entrada_sha256.")
                        else:
                            self.ok()  # B5 (sha entrada)
                    else:
                        self.falla("B5", f"Caso {cid}: INTERPRETABLE no trae entrada_sha256.")
            # B6: RECIBO con status declarado.
            rp = d / f"{cid}_RECIBO_EJECUCION.json"
            if rp.exists():
                try:
                    recibo = load_json(rp)
                except Exception as e:
                    self.falla("B6", f"Caso {cid}: {cid}_RECIBO_EJECUCION.json no es JSON válido: {e}")
                    recibo = None
                if isinstance(recibo, dict):
                    if isinstance(recibo.get("status"), str) and recibo["status"].strip():
                        self.ok()  # B6
                    else:
                        self.falla("B6", f"Caso {cid}: RECIBO no trae `status` declarado "
                                        "(estado de ejecución: PROTOCOLO §3; si el runner no lo "
                                        "genera, se anota NO REGISTRADO, no se inventa).")
                    # B8b: sha del recibo real vs manifiesto.
                    real = sha256_file(rp)
                    if real != c.get("receipt_sha256"):
                        self.falla("B8", f"Caso {cid}: el SHA-256 real de {cid}_RECIBO_EJECUCION.json "
                                        f"({real[:16]}…) no coincide con MANIFIESTO.receipt_sha256 "
                                        f"({str(c.get('receipt_sha256'))[:16]}…).")
                    else:
                        self.ok()  # B8 (recibo)
            # B7/B8: entrada.json con prosa + tokens y sha verificado.
            ep = d / f"{cid}_entrada.json"
            if ep.exists():
                try:
                    entrada = load_json(ep)
                except Exception as e:
                    self.falla("B7", f"Caso {cid}: {cid}_entrada.json no es JSON válido: {e}")
                    entrada = None
                if isinstance(entrada, dict):
                    if entrada.get("case_id") != cid:
                        self.falla("B7", f"Caso {cid}: entrada.json trae case_id "
                                        f"'{entrada.get('case_id')}', distinto de {cid}.")
                    elif not isinstance(entrada.get("question"), str) or not entrada["question"].strip():
                        self.falla("B7", f"Caso {cid}: entrada.json no trae `question` en prosa "
                                        "(texto no vacío) para repetir la corrida.")
                    else:
                        cuts = entrada.get("cuts")
                        if not isinstance(cuts, list) or not cuts:
                            self.falla("B7", f"Caso {cid}: entrada.json no trae `cuts` (lista no vacía).")
                        else:
                            sin_hecho = [i for i, ct in enumerate(cuts)
                                         if not isinstance(ct, dict)
                                         or not isinstance(ct.get("hecho"), str)
                                         or not ct["hecho"].strip()]
                            if sin_hecho:
                                self.falla("B7", f"Caso {cid}: entrada.json tiene cortes sin `hecho` "
                                                 f"en prosa (índices {sin_hecho}).")
                            else:
                                self.ok()  # B7
                    real = sha256_file(ep)
                    if real != c.get("entrada_sha256"):
                        self.falla("B8", f"Caso {cid}: el SHA-256 real de {cid}_entrada.json "
                                        f"({real[:16]}…) no coincide con MANIFIESTO.entrada_sha256 "
                                        f"({str(c.get('entrada_sha256'))[:16]}…).")
                    else:
                        self.ok()  # B8 (entrada)

    # ---------- C. Tabla ----------
    def check_tabla(self) -> None:
        tabla = self.delivery / "TABLA_VALORES_COMPLETA.md"
        if not tabla.exists():
            return  # ya falló en A3
        texto = tabla.read_text(encoding="utf-8", errors="replace")
        faltantes = [c.get("case_id") for c in self.casos
                     if isinstance(c, dict) and isinstance(c.get("case_id"), str)
                     and c["case_id"] not in texto]
        if faltantes:
            self.falla("C1", "TABLA_VALORES_COMPLETA.md no menciona estos case_id del "
                             f"MANIFIESTO (casos fuera de la tabla): {', '.join(faltantes)}.")
        else:
            self.ok()

    # ---------- D. Lectura ----------
    def check_lectura(self) -> None:
        lp = self.delivery / "LECTURA.json"
        if not lp.exists():
            return  # ya falló en A4
        try:
            lectura = load_json(lp)
        except Exception as e:
            self.falla("D1", f"LECTURA.json no es JSON válido: {e}")
            return
        lecturas = lectura.get("lecturas") if isinstance(lectura, dict) else None
        if not isinstance(lecturas, list) or not lecturas:
            self.falla("D1", "LECTURA.json no trae `lecturas` (lista no vacía de archivos leídos).")
            return
        self.ok()  # D1
        cita = (self.readme_text + "\n" + self.revision_text).lower()
        for i, lec in enumerate(lecturas):
            if not isinstance(lec, dict):
                self.falla("D2", f"LECTURA.lecturas[{i}] no es un objeto JSON.")
                continue
            ruta = lec.get("ruta")
            if not isinstance(ruta, str) or not ruta.strip():
                self.falla("D2", f"LECTURA.lecturas[{i}] no trae `ruta` (texto no vacío).")
                continue
            if not (isinstance(lec.get("sha256"), str) or isinstance(lec.get("fecha"), str)):
                self.falla("D2", f"Lectura {ruta}: no trae `sha256` ni `fecha`. Debe traer "
                                 "al menos uno de los dos.")
                continue
            self.ok()  # D2
            if self.repo is None:
                self.falla("D3", f"Lectura {ruta}: no se pudo detectar la raíz del repo "
                                 "(pasa --repo) para comprobar que el archivo existe.")
                continue
            fp = self.repo / ruta
            if not fp.exists():
                self.falla("D3", f"Lectura {ruta}: el archivo no existe en el repo "
                                 f"({self.repo}). La lectura no se puede comprobar.")
                continue
            self.ok()  # D3
            sha = lec.get("sha256")
            if isinstance(sha, str) and sha.strip():
                if not HEX64.match(sha):
                    self.falla("D4", f"Lectura {ruta}: `sha256` no es un SHA-256 hexadecimal "
                                    "de 64 caracteres.")
                elif sha != sha256_file(fp):
                    self.falla("D4", f"Lectura {ruta}: el sha256 declarado ({sha[:16]}…) no "
                                    "coincide con el SHA-256 actual del archivo en el repo "
                                    f"({sha256_file(fp)[:16]}…). El archivo cambió desde su lectura.")
                else:
                    self.ok()  # D4
            base = Path(ruta).name.lower()
            if base and base in cita:
                self.ok()  # D5
            else:
                self.falla("D5", f"Lectura {ruta}: ni README.md ni REVISION.md mencionan "
                                 f"'{Path(ruta).name}'. La entrega no cita lo que dice haber leído.")

    def run(self) -> int:
        if not self.delivery.is_dir():
            print(f"CANDADO_ENTREGA: BLOQUEADO — NO SE GUARDA", file=sys.stderr)
            print(f"[USO] La carpeta de entrega no existe o no es un directorio: {self.delivery}", file=sys.stderr)
            print("Razón única de no guardar: la entrega no existe.", file=sys.stderr)
            return 2
        self.check_estructura()
        if self.manifiesto is not None and self.casos:
            self.check_contenido()
            self.check_tabla()
        self.check_lectura()
        if self.fallos:
            print("CANDADO_ENTREGA: BLOQUEADO — NO SE GUARDA")
            print(f"Paquete: {self.delivery}")
            print(f"Criterios pasados: {self.pasados} | Criterios incumplidos: {len(self.fallos)}")
            print("Criterios incumplidos (exactamente qué falta):")
            for f in self.fallos:
                print(f"  - {f}")
            print("Razón única de no guardar: no se cumplen los criterios listados arriba. "
                  "No es un fallo de guardado: es el candado bloqueando una entrega incompleta.")
            return 1
        print("CANDADO_ENTREGA: PASA")
        print(f"Paquete: {self.delivery}")
        print(f"Criterios pasados: {self.pasados} | Criterios incumplidos: 0")
        print("La entrega cumple las especificaciones y demuestra lectura. Se puede guardar.")
        return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Candado de entrega de corridas del motor U6: valida el paquete "
                    "antes de aceptarlo/guardarlo en el repo.")
    ap.add_argument("entrega", help="Carpeta del paquete, p. ej. motor/runs/F001_F002_20261111/")
    ap.add_argument("--repo", default=None,
                    help="Raíz del repo para comprobar las lecturas "
                         "(por defecto: se detecta subiendo desde la entrega).")
    args = ap.parse_args(argv)
    delivery = Path(args.entrega).resolve()
    repo = Path(args.repo).resolve() if args.repo else detectar_repo(delivery)
    return Candado(delivery, repo).run()


if __name__ == "__main__":
    sys.exit(main())
