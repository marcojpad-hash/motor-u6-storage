#!/usr/bin/env python3
"""protocolo_kernel_motor.py — PROTOCOLO del motor (no adorno, no sidecar opcional)

Mj 2026-09-20:
  Estas piezas NO «suman a lo pendejo». Son protocolo: el sistema no puede
  pararse a cada tipografía/hash/ambigüedad y exigir intervención humana
  (ni 4 Claudes auditores) para desambiguar lo que ya está resuelto por
  analogía con lo cableado.

Regla dura:
  PARAR = excepción rara (candado canónico Engine/244/FREEZE/H).
  Ante pendejada operativa → CONTORNAR + REPORTAR uso (bitácora calibración).
  No pedir a Mj que recorra auditores.

Bloque obligatorio (siempre-on en ejecución de matriz):
  1. flujo-soluciones (agua vs piedra)
  2. latencia + décimo hombre (info insuficiente ≠ fallo)
  3. polaridad / falso-problema (doble negación = sensor, no hueco)
  4. tortugas (resolución insuficiente → remedir, no inventar fuerza)
  5. integración ≠ nulificación (capa semántica; no apagar por conflicto aparente)
  6. falacias in/out (dato vs ruido; no absorber protocolo-noise)

Candados: Alimenta_H=NO · no Engine · no 244 · no FREEZE.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, List, Optional

__version__ = "1.0.0-protocolo-20260920"
ALIMENTA_H = "NO"
PARAR_SOLO_SI = ("ENGINE", "244", "FREEZE", "H_CANONICO", "CANDADO_HASH_ENGINE")

# Mapa: obstáculo típico de auditor → pieza análoga YA cableada
ANALOGIAS_RESUELTAS: Dict[str, Dict[str, str]] = {
    "hash_no_identico": {
        "pieza": "flujo + BYPASS_HASH_CAMBIO",
        "analogia": "Hash distinto → leer/correr igual; bitácora; no apagar protocolo ni modelo",
        "accion": "bypass_hash_cambio_continuar",
    },
    "typo_ruta": {
        "pieza": "flujo",
        "analogia": "Fuzzy/glob como resolve multi-ruta del catálogo",
        "accion": "contornar_candidato_cercano",
    },
    "doble_negacion": {
        "pieza": "polaridad_causal + latencia",
        "analogia": "Falso problema T5 cerrado; litote ≠ NIEGA simple",
        "accion": "marcar_sensor_no_parar",
    },
    "empate_50_50": {
        "pieza": "latencia + décimo hombre",
        "analogia": "Re-tirar / almacenar hasta tokens bastantes",
        "accion": "latencia_o_almacen",
    },
    "borroso_sin_fuerza": {
        "pieza": "tortugas (Aquiles H + picos)",
        "analogia": "Resolución insuficiente → partir corte, no cambiar familia",
        "accion": "remedir_no_inventar",
    },
    "conflicto_luces": {
        "pieza": "integración semántica",
        "analogia": "Integrar vectores; no nulificar porque choquen",
        "accion": "integrar_no_apagar",
    },
    "ruido_protocolo": {
        "pieza": "falacias in/out + sombrero blanco",
        "analogia": "Hecho observable entra; juicio/fecha/recorte de protocolo no",
        "accion": "filtrar_ruido_seguir",
    },
    "auditor_pide_mj": {
        "pieza": "este kernel",
        "analogia": "Desambiguación ya tipada → no escalar a humano",
        "accion": "aplicar_analogia_reportar",
    },
}


@dataclass
class EventoBitacora:
    ts: float
    piedra: str
    tipo: str
    pieza_usada: str
    accion: str
    evidencia: str
    pidio_humano: bool = False
    ok_protocolo: bool = True


_BITACORA: List[EventoBitacora] = []


def bitacora() -> List[Dict[str, Any]]:
    return [asdict(e) for e in _BITACORA]


def limpiar_bitacora() -> None:
    _BITACORA.clear()


def _log(piedra: str, tipo: str, pieza: str, accion: str, evidencia: str, *, pidio_humano: bool = False) -> Dict[str, Any]:
    ev = EventoBitacora(
        ts=time.time(),
        piedra=piedra[:300],
        tipo=tipo,
        pieza_usada=pieza,
        accion=accion,
        evidencia=evidencia[:500],
        pidio_humano=pidio_humano,
        ok_protocolo=not pidio_humano,
    )
    _BITACORA.append(ev)
    return asdict(ev)


def clasificar_para_protocolo(texto: str) -> str:
    t = (texto or "").lower()
    if "hash" in t and ("idént" in t or "ident" in t or "coincide" in t or "mismatch" in t):
        return "hash_no_identico"
    if any(k in t for k in ["typo", "letra", "ruta", "did you mean", "no such file"]):
        return "typo_ruta"
    if any(k in t for k in ["doble neg", "no es que no", "litote", "falso problema"]):
        return "doble_negacion"
    if any(k in t for k in ["50/50", "0.5", "empate", "indetermin"]):
        return "empate_50_50"
    if any(k in t for k in ["tortuga", "borros", "kappa", "sin resolución", "aquiles"]):
        return "borroso_sin_fuerza"
    if any(k in t for k in ["nulific", "apagar luz", "conflicto de luces", "se cancelan"]):
        return "conflicto_luces"
    if any(k in t for k in ["ruido", "falacia", "juicio estético", "sombrero"]):
        return "ruido_protocolo"
    if any(k in t for k in ["pregunta a mj", "necesito que marco", "escalar a humano", "¿qué hago?"]):
        return "auditor_pide_mj"
    return "auditor_pide_mj" if any(k in t for k in ["no puedo", "bloqueado", "atascad"]) else "typo_ruta"


def aplicar_protocolo(obstaculo: str, *, evidencia: str = "") -> Dict[str, Any]:
    """Entrada única: no parar; contornar con pieza análoga; bitácora."""
    tipo = clasificar_para_protocolo(obstaculo)
    meta = ANALOGIAS_RESUELTAS[tipo]
    # flujo concreto
    try:
        from control_flujo_soluciones import contornar
        plan = contornar(obstaculo)
    except Exception as e:  # noqa: BLE001 — el protocolo no puede caerse
        plan = {"error_flujo": str(e), "contornos": [meta["accion"]]}

    # sensores hermanos (best-effort; no bloquean)
    extras: Dict[str, Any] = {}
    if tipo == "doble_negacion":
        try:
            from plugin_polaridad_causal import clasificar_polaridad_causal
            extras["polaridad"] = clasificar_polaridad_causal(obstaculo)
        except Exception as e:  # noqa: BLE001
            extras["polaridad_error"] = str(e)
    if tipo == "empate_50_50":
        try:
            from control_latencia_decimo_hombre import actualizar_expediente
            extras["latencia"] = actualizar_expediente(
                "protocolo_kernel", tema="empate", p_momento=0.5, tokens_nuevos=[]
            )
        except Exception as e:  # noqa: BLE001
            extras["latencia_error"] = str(e)

    ev = _log(
        obstaculo,
        tipo,
        meta["pieza"],
        meta["accion"],
        evidencia or json.dumps(plan.get("contornos", [])[:2], ensure_ascii=False),
        pidio_humano=False,
    )
    return {
        "protocolo": "KERNEL_MOTOR",
        "version": __version__,
        "Alimenta_H": ALIMENTA_H,
        "parar": False,
        "motivo_no_parar": "Obstáculo tipado; analogía cableada. Reportar, no escalar.",
        "tipo": tipo,
        "pieza": meta["pieza"],
        "analogia": meta["analogia"],
        "accion": meta["accion"],
        "plan_flujo": plan,
        "extras": extras,
        "bitacora_evento": ev,
        "formato_auditor": [
            "PIEDRA: …",
            "PIEZA: … (analogía)",
            "CONTORNO/SIGUIENTE: …",
            "EVIDENCIA: …",
            "NO_PEDIR_A_MJ: sí",
        ],
    }



def verificar_hash_con_bypass(
    ruta: str | None = None,
    hash_esperado: str | None = None,
    *,
    rol: str = "lateral_o_protocolo",
) -> Dict[str, Any]:
    """API corta: si el hash cambió, bypass y sigue (protocolo + lectura + corrida)."""
    try:
        from control_flujo_soluciones import bypass_hash_cambio
    except Exception as e:  # noqa: BLE001
        return {
            "bypass": True,
            "permitir_lectura": True,
            "permitir_corrida": True,
            "permitir_protocolo": True,
            "fallback": str(e),
            "Alimenta_H": ALIMENTA_H,
        }
    out = bypass_hash_cambio(ruta=ruta, hash_esperado=hash_esperado, rol=rol)
    _log(
        f"hash check {ruta or ''} esperado={hash_esperado}",
        "hash_no_identico" if out.get("bypass") or out.get("codigo") == "BYPASS_HASH_CAMBIO" else "hash_ok",
        "BYPASS_HASH_CAMBIO",
        out.get("accion", "continuar"),
        str((out.get("bitacora") or {})),
        pidio_humano=False,
    )
    # forzar que protocolo nunca se apague por hash lateral
    out["permitir_protocolo"] = True if out.get("bypass", True) else out.get("permitir_protocolo", True)
    return out


def contrato_auditores() -> Dict[str, Any]:
    """Texto operativo para Claudes: qué está prohibido."""
    return {
        "titulo": "CONTRATO_AUDITORES_NO_PARAR",
        "version": __version__,
        "prohibido": [
            "Detenerse por hash no byte-idéntico sin buscar equivalente.",
            "Negarse a leer/correr el protocolo o el modelo porque el hash cambió (usar BYPASS_HASH_CAMBIO).",
            "Detenerse por typo/letra en ruta sin glob/fuzzy.",
            "Reabrir T5/doble negación como hueco de motor.",
            "Pedir a Mj desambiguar lo ya tipado en ANALOGIAS_RESUELTAS.",
            "Nulificar luces por conflicto aparente (usar integración).",
            "Tratar tortugas/borroso como veredicto o cambio de familia.",
            "Convertir ruido de protocolo (fechas, títulos, juicios) en dato de corrida.",
        ],
        "obligatorio": [
            "Llamar aplicar_protocolo(obstaculo) o contornar vía flujo.",
            "Dejar EventoBitacora (calibración).",
            "Seguir el tubo / siguiente pendiente útil.",
            "Parar SOLO si toca Engine/244/FREEZE/H canónico.",
        ],
        "analogias": ANALOGIAS_RESUELTAS,
        "Alimenta_H": ALIMENTA_H,
        "parar_solo_si": list(PARAR_SOLO_SI),
    }


def arranque_matriz() -> Dict[str, Any]:
    """Hook siempre-on al inicio de matriz_corrida."""
    return {
        "kernel": "protocolo_kernel_motor",
        "version": __version__,
        "siempre_on": True,
        "rol": "PROTOCOLO_MOTOR",
        "no_es": ["sidecar_opcional", "plugin_de_contenido", "adorno"],
        "bloque": list(ANALOGIAS_RESUELTAS.keys()),
        "contrato": contrato_auditores(),
        "Alimenta_H": ALIMENTA_H,
    }


if __name__ == "__main__":
    limpiar_bitacora()
    demos = [
        "No puedo: hash no idéntico al marcado",
        "no es que no explica el resultado",
        "empate 50/50 no sé si cierro",
        "las luces se cancelan, nulifico",
        "¿le pregunto a Mj qué hago con el typo?",
    ]
    for d in demos:
        r = aplicar_protocolo(d)
        assert r["parar"] is False, d
        print(r["tipo"], "→", r["accion"], "| pedir_mj=", r["bitacora_evento"]["pidio_humano"])
    bh = verificar_hash_con_bypass(hash_esperado="old", rol="protocolo")
    # force mismatch path
    from control_flujo_soluciones import bypass_hash_cambio
    bh2 = bypass_hash_cambio(hash_esperado="old", hash_actual="new", rol="protocolo")
    assert bh2["bypass"] and bh2["permitir_corrida"] and bh2["permitir_protocolo"]
    c = contrato_auditores()
    assert "Detenerse por hash" in c["prohibido"][0]
    print("PASS_SMOKE protocolo_kernel_motor", __version__, "eventos=", len(bitacora()))
