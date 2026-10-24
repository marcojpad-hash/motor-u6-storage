#!/usr/bin/env python3
"""matriz_corrida.py — entrada de la matriz que SE CORRE

Orden fijo (PROTOCOLO, no adornos):
  0) KERNEL protocolo_motor (siempre-on; no-parar + bitácora)
  1) CONTROL latencia/décimo hombre
  1b) CONTROL flujo-soluciones (agua vs piedra)
  2) Capa2 (prototipos + luces gemini + hilado)
  3) Sidecar amantes (condicional POST)
  4) Polaridad causal (sensor; no cierra)

Parar SOLO Engine/244/FREEZE/H. Obstáculo tipado → contornar + reportar.
No toca Engine/244/H/FREEZE.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

HERE = Path(__file__).resolve().parent
for p in [HERE, HERE.parent / "03_LATERALES_VIGENTES", HERE.parent / "02_TUBO"]:
    if p.is_dir() and str(p) not in sys.path:
        sys.path.insert(0, str(p))


def correr_matriz(
    pinchos_por_corte: Dict[str, Sequence[Any]],
    *,
    hechos_extra: Optional[Sequence[Any]] = None,
    texto_polaridad: Optional[str] = None,
    clave: str = "matriz",
    obstaculo_opcional: Optional[str] = None,
) -> Dict[str, Any]:
    from protocolo_kernel_motor import arranque_matriz, aplicar_protocolo, bitacora, limpiar_bitacora
    from control_flujo_soluciones import contornar as flujo_contornar
    from control_latencia_decimo_hombre import actualizar_expediente, polaridad_con_latencia
    from plugin_capa2_antecedentes_arquetipos import leer as capa2_leer

    limpiar_bitacora()
    kernel = arranque_matriz()

    # Si llega un obstáculo operativo (hash/typo/etc), protocolo primero — no parar
    protocolo_evento = None
    if obstaculo_opcional:
        protocolo_evento = aplicar_protocolo(obstaculo_opcional)

    tokens = []
    for v in pinchos_por_corte.values():
        for x in v:
            if isinstance(x, str):
                tokens.append(x)

    if texto_polaridad:
        # polaridad pasa por control; doble negación no cierra ni para
        control = polaridad_con_latencia(
            texto_polaridad, clave=f"{clave}::pol", tokens_contexto=tokens
        )
        # si polaridad huele a litote/falso-problema, bitácora de protocolo
        if "no es que no" in texto_polaridad.lower() or "tampoco es que no" in texto_polaridad.lower():
            aplicar_protocolo(texto_polaridad, evidencia="sensor_polaridad_en_matriz")
        control_out = {
            "rol": "CONTROL_ESTRUCTURAL",
            "siempre_on": True,
            "Alimenta_H": "NO",
            "lectura_momento": control.get("lectura_momento"),
            "accion": (control.get("dinamica") or {}).get("accion"),
            "expediente": (control.get("dinamica") or {}).get("expediente"),
        }
    else:
        n = len(set(tokens))
        p = 0.50 if n < 3 else min(0.72, 0.45 + 0.04 * n)
        dyn = actualizar_expediente(clave, tema="matriz", p_momento=p, tokens_nuevos=tokens)
        control_out = {
            "rol": "CONTROL_ESTRUCTURAL",
            "siempre_on": True,
            "Alimenta_H": "NO",
            "accion": dyn.get("accion"),
            "expediente": dyn.get("expediente"),
        }

    import inspect
    sig = inspect.signature(capa2_leer)
    kw = {}
    if "hechos_extra" in sig.parameters and hechos_extra is not None:
        kw["hechos_extra"] = hechos_extra
    if "texto_polaridad" in sig.parameters and texto_polaridad is not None:
        kw["texto_polaridad"] = texto_polaridad
    capa2 = capa2_leer(pinchos_por_corte, **kw)

    cierre_permitido = (control_out.get("accion") == "LIBERAR_LATENCIA") or (
        (control_out.get("expediente") or {}).get("estado") == "RESUELTO"
    )

    return {
        "matriz": "MATRIZ_CORRIDA_V15_1",
        "version": "2026-09-20-protocolo",
        "Alimenta_H": "NO",
        "orden": [
            "KERNEL_protocolo_motor",
            "CONTROL_latencia_decimo_hombre",
            "CONTROL_flujo_soluciones",
            "capa2_bus_luces_hilado",
            "sidecar_amantes_condicional",
            "sensor_polaridad",
        ],
        "kernel_protocolo": {
            "siempre_on": True,
            "version": kernel.get("version"),
            "contrato_resumen": {
                "parar_solo_si": kernel["contrato"]["parar_solo_si"],
                "n_prohibido_auditor": len(kernel["contrato"]["prohibido"]),
            },
            "evento_obstaculo": protocolo_evento,
            "bitacora": bitacora(),
        },
        "control": control_out,
        "flujo_soluciones": {
            "rol": "CONTROL_FLUJO",
            "regla": "piedra→contorno→siguiente",
            "Alimenta_H": "NO",
            "api": "contornar(error)",
            "demo_hash": flujo_contornar("hash no idéntico")["tipo_piedra"]
            if False
            else "disponible",
        },
        "capa2": {
            "candados": capa2.get("candados"),
            "sugerencia_una_familia": (capa2.get("sugerencia_una_familia") or {}).get("id")
                if isinstance(capa2.get("sugerencia_una_familia"), dict)
                else capa2.get("sugerencia_una_familia"),
            "luces_gemini_packs": {
                k: (capa2.get("luces_gemini_packs") or {}).get(k)
                for k in ("cableado", "modo", "conteos", "hilado")
            },
            "sidecar_amantes": {
                k: (capa2.get("sidecar_amantes") or {}).get(k)
                for k in ("modo", "activado", "luces")
            },
            "control_latencia_en_capa2": capa2.get("control_latencia"),
        },
        "cierre_lectura_permitido": bool(cierre_permitido),
        "nota": (
            "PROTOCOLO: no parar por pendejada tipada; bitácora para calibrar. "
            "Parar solo Engine/244/FREEZE/H. Auditores no escalan a Mj lo ya analogado."
        ),
    }


if __name__ == "__main__":
    demo = {
        "A": ["aprendizaje"],
        "B": ["patron", "clientela"],
        "C": ["celos", "triangulo"],
        "D": ["juicio", "sancion"],
    }
    out = correr_matriz(
        demo,
        texto_polaridad="no es que no explica el conflicto",
        obstaculo_opcional="hash no idéntico al marcado",
    )
    print(json.dumps({
        "kernel": out["kernel_protocolo"]["version"],
        "bitacora_n": len(out["kernel_protocolo"]["bitacora"]),
        "bitacora_tipos": [e["tipo"] for e in out["kernel_protocolo"]["bitacora"]],
        "control_accion": out["control"].get("accion"),
        "cierre_permitido": out["cierre_lectura_permitido"],
        "Alimenta_H": out["Alimenta_H"],
        "parar_solo_si": out["kernel_protocolo"]["contrato_resumen"]["parar_solo_si"],
    }, ensure_ascii=False, indent=2))
