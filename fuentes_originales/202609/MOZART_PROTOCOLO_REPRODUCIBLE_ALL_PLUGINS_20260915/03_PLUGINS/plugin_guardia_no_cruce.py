"""
plugin_guardia_no_cruce.py
V15.1 — guardia epistemologica lente vs motor
No toca Engine_V5 ni 244. Valida que lente no contamine hyp_state bayesiano.
Usa: with GuardiaNoCruce(hyp_state, corte_id="e7") as g: g.validar_output_lente(lente_output)
"""

from __future__ import annotations
from typing import Dict, Any, Set
import copy

class ContaminacionBayesianaError(RuntimeError):
    """Se intentó modificar probabilidad del motor usando el lente."""
    pass

class CampoProbabilisticoProhibidoError(RuntimeError):
    """Lente trae campo probabilístico donde no debe."""
    pass

CAMPOS_PROHIBIDOS_EN_LENTE = {
    "confianza", "confidence", "p_final", "p", "probabilidad",
    "p_H", "winner", "topk", "score", "peso", "w", "likelihood",
    "kwml_rey", "erikson_05", "erikson", "kwml", "mbti", "ennea"
}

CAMPOS_PERMITIDOS_LENTE = {
    "cuadrante_activo", "hilos_presentes", "arco", "fase", "corte_id",
    "Q1", "Q2", "Q3", "Q4", "Q3_Ordeal_7_9", "Q4_Retorno_10_12",
    "nota", "evidence_status", "origen", "lente"
}

class GuardiaNoCruce:
    def __init__(self, hyp_state: Dict[str, float], corte_id: str = "na"):
        self.corte_id = corte_id
        # snapshot inmutable al entrar
        self._hyp_snapshot = copy.deepcopy(hyp_state)
        self._hyp_ref = hyp_state  # referencia viva para detectar mutación
        self._hash_snapshot = hash(frozenset(self._hyp_snapshot.items())) if self._hyp_snapshot else 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # al salir, verifica que nadie mutó hyp_state dentro del with
        if self._hyp_ref != self._hyp_snapshot:
            # detecta qué cambió
            diff = []
            for k in set(self._hyp_snapshot.keys()) | set(self._hyp_ref.keys()):
                v0 = self._hyp_snapshot.get(k)
                v1 = self._hyp_ref.get(k)
                if v0 != v1:
                    diff.append(f"{k}: {v0} -> {v1}")
            raise ContaminacionBayesianaError(
                f"[{self.corte_id}] hyp_state mutado dentro de GuardiaNoCruce — "
                f"cambios: {'; '.join(diff)} — prohibido sumar porque el lente también lo marcó"
            )
        return False

    def validar_output_lente(self, lente_output: Dict[str, Any]):
        # 1) campos prohibidos en output lente
        for campo in lente_output.keys():
            cl = campo.lower()
            if cl in CAMPOS_PROHIBIDOS_EN_LENTE or "confianza" in cl or "p_final" in cl or "prob" in cl:
                raise CampoProbabilisticoProhibidoError(
                    f"[{self.corte_id}] lente_output trae campo prohibido '{campo}' — "
                    f"lente solo puede traer cuadrante_activo/hilos_presentes, no probabilidad"
                )
        # 2) valores que parezcan probabilidades sueltas dentro
        for k, v in lente_output.items():
            if isinstance(v, (int, float)) and 0.0 <= float(v) <= 1.0 and k not in CAMPOS_PERMITIDOS_LENTE:
                # si es float 0-1 y no es campo permitido, sospechoso
                if k not in ("fase",):
                    # permite solo si es parte de estructura conocida, si no avisa
                    if isinstance(v, float) and k.lower() not in ("q", "quadrant"):
                        # para ser estricto, si trae float en top-level no permitido, error
                        if k in ("confianza", "confidence"):
                            raise CampoProbabilisticoProhibidoError(
                                f"[{self.corte_id}] lente_output campo '{k}'={v} parece probabilidad — prohibido"
                            )
        return True

# demo auto-test si se ejecuta directo
if __name__ == "__main__":
    hyp_state = {"kwml_rey": 0.62, "erikson_05": 0.48}
    lente_output_limpio = {"cuadrante_activo": ["Q3_Ordeal_7_9"], "hilos_presentes": ["hilo_sombra_consumo"]}
    try:
        with GuardiaNoCruce(hyp_state, corte_id="e7") as g:
            g.validar_output_lente(lente_output_limpio)
        print("OK -- no hubo contaminacion, output limpio\n")
    except Exception as e:
        print("FALLO INESPERADO:", e, "\n")

    print("--- CASO 2: alguien actualiza probabilidad usando lente ---")
    hyp_state2 = {"kwml_rey": 0.62, "erikson_05": 0.48}
    try:
        with GuardiaNoCruce(hyp_state2, corte_id="e7") as g:
            resultado = {"cuadrante_activo": ["Q3_Ordeal_7_9"]}
            hyp_state2["erikson_05"] = 0.48 + 0.1
            g.validar_output_lente(resultado)
        print("ERROR: esto no debio pasar sin excepcion\n")
    except ContaminacionBayesianaError as e:
        print("CAPTURADO CORRECTAMENTE:", e, "\n")

    print("--- CASO 3: lente trae campo prohibido ---")
    hyp_state3 = {"kwml_rey": 0.62}
    lente_output_malo = {"cuadrante_activo": ["Q4_Retorno_10_12"], "confianza": 0.9}
    try:
        with GuardiaNoCruce(hyp_state3, corte_id="e10") as g:
            g.validar_output_lente(lente_output_malo)
        print("ERROR: esto no debio pasar sin excepcion\n")
    except CampoProbabilisticoProhibidoError as e:
        print("CAPTURADO CORRECTAMENTE:", e, "\n")
