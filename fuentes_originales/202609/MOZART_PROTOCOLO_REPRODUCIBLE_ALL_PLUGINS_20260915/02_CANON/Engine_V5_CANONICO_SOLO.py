"""
Motor de Trazabilidad y Perfilamiento Estructural — v3

Añade sobre v2 los mecanismos del "Grupo A" (implementables sin corpus
externo ni embeddings):

  1. delta_min(t) dinámico — depende de la incertidumbre promedio de los
     tokens activados en la observación (antes: constante fija 0.1).
  2. sigma_sorpresa(t) dinámico — depende de la DISPERSIÓN (inconsistencia)
     entre los tokens activados, no de su promedio. Decisión de diseño
     confirmada por el usuario.
  3. P_azar(t) — aleatorio real por corrida, con rango de variación
     proporcional a sigma_sorpresa(t). Decisión de diseño confirmada.
  4. P_final mixto (Fórmula 22 del documento de 17 fórmulas), combinando
     P(H|E,Q), P_indet y P_azar(t) ponderados por delta_min(t) y
     sigma_sorpresa(t).
  5. epsilon — masa residual de incertidumbre (Fórmula 3): antes de
     aplicar la evidencia de una nueva observación, la probabilidad previa
     se mezcla con 0.5 (lo desconocido).
  6. Reevaluación en 50/50 (mecanismo del anexo): si una hipótesis queda
     ambigua tras procesar una observación, se reactiva memoria latente
     con prioridad en los tokens que más la empujaron hacia el límite.
  7. Actualización por contradicción con condiciones asociadas (Fórmula
     10): cuando un marcador contradice una hipótesis, se registran junto
     con él los demás marcadores presentes en la misma observación (las
     "condiciones" bajo las cuales ocurrió la contradicción).
  8. Decaimiento temporal simple de confianza en memoria latente: un
     marcador reactivado pierde parte de su confianza original según
     cuánto tiempo estuvo inactivo. (La parte de la fórmula de peso
     dinámico que depende de un corpus, P(Token|N_Q), sigue sin
     implementar — Grupo B.)

Fix incluido en esta versión: tolerancia de punto flotante en
is_indeterminado(). Valores como 0.5999999999999998 (matemáticamente 0.6,
pero con error de redondeo de máquina) ya no se marcan erróneamente como
indeterminados por ~1e-17 de diferencia. No confundir con el epsilon
conceptual del modelo (Fórmula 3) — este es puramente numérico.

Todo lo del Grupo B (peso dinámico completo, corpus de patrones, campo
semántico real con P(Token|N_Q), memoria por embeddings, calibración
empírica) sigue pendiente y fuera de este archivo.
"""

import json
import sqlite3
import datetime
import os
import random
import statistics
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional


# ============================================
# Marker
# ============================================

def _clamp01(x: float, nombre: str = "confidence") -> float:
    """Fuerza un valor a [0,1]. Rechaza NaN explicitamente en vez de
    dejarlo propagarse silenciosamente por todo el motor (bug real
    encontrado por ChatGPT, verificado por ejecucion: Marker aceptaba
    confidence fuera de rango o NaN sin validar, contaminando
    _delta_h() -> delta_h_t -> delta_min_t -> todo lo demas)."""
    if x != x:  # NaN nunca es igual a si mismo -- forma estandar de detectarlo sin math.isnan
        raise ValueError(f"{nombre}=NaN no es valido, se rechaza explicitamente en vez de propagarse")
    if x == float("inf") or x == float("-inf"):
        raise ValueError(f"{nombre}=inf no es valido, se rechaza explicitamente en vez de recortarse a 0 o 1")
    return max(0.0, min(1.0, x))


class Marker:
    def __init__(self, token: str, value: str, confidence: float, source: str = "observacion"):
        self.token = token
        self.value = value
        self.confidence = _clamp01(confidence, "confidence")
        self.timestamp = datetime.datetime.now().isoformat()
        self.source = source

    def uncertainty(self) -> float:
        """sigma_i(t): incertidumbre contextual del token. Proxy: 1 - confidence."""
        return 1.0 - self.confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "token": self.token,
            "value": self.value,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "source": self.source
        }


# ============================================
# Hypothesis
# ============================================

class Hypothesis:
    INDETERMINACY_THRESHOLD = 0.1
    FLOAT_TOLERANCE = 1e-9

    def __init__(self, name: str, prior: float = 0.5):
        self.name = name
        self.probability = prior
        self.favor: List[Dict[str, Any]] = []
        self.contra: List[Dict[str, Any]] = []
        self.contradicciones_contextuales: List[Dict[str, Any]] = []

    def support(self, weight: float):
        self._update(weight)

    def contradict(self, weight: float):
        self._update(1 - weight)

    def _update(self, likelihood_h: float):
        lh = max(0.001, min(0.999, likelihood_h))
        p = self.probability
        denom = p * lh + (1 - p) * (1 - lh)
        self.probability = p if denom == 0 else (p * lh) / denom

    def apply_epsilon(self, epsilon: float):
        """Fórmula 3 — masa residual de incertidumbre, aplicada una vez por observación."""
        eps = max(0.0, min(1.0, epsilon))
        self.probability = (1 - eps) * self.probability + eps * 0.5

    def is_indeterminado(self) -> bool:
        return abs(self.probability - 0.5) < (self.INDETERMINACY_THRESHOLD - self.FLOAT_TOLERANCE)

    def direction(self) -> int:
        if self.is_indeterminado():
            return 0
        return 1 if self.probability > 0.5 else -1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "probability": round(self.probability, 4),
            "favor": len(self.favor),
            "contra": len(self.contra),
            "indeterminado": self.is_indeterminado()
        }


# ============================================
# PatternLibrary
# ============================================

class PatternLibrary:
    EVIDENCE_MULTIPLIERS = {
        "primary_verified": 1.0,
        "secondary_verified": 0.7,
        "outdated": 0.5,
        "unverified": 0.4,
        "contestado_academicamente": 0.4,  # misma fuerza que unverified: hay fuente, no hay consenso
        "contradicted_partial": 0.2,
        "contradicted": 0.1,
    }
    DEFAULT_MULTIPLIER = 1.0

    def __init__(self, filepath: str = "patterns.json"):
        self.filepath = filepath
        self.patterns = self._load()

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error cargando {self.filepath}: {e}. Se usará biblioteca vacía.")
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2)
        except IOError:
            pass
        return {}

    def get_patterns_for_question(self, question: str) -> List[str]:
        return list(self.patterns.keys())

    def get_weight(self, pattern: str, token: str, is_favor: bool) -> float:
        p = self.patterns.get(pattern)
        if p is None:
            print(f"Advertencia: patrón '{pattern}' no existe.")
            return 0.0
        key = "tokens_favor" if is_favor else "tokens_contra"
        peso_original = p.get(key, {}).get(token, 0.0)
        if peso_original == 0.0:
            return 0.0
        status = p.get("evidence_status_tokens", {}).get(token) or p.get("evidence_status")
        multiplicador = self.EVIDENCE_MULTIPLIERS.get(status, self.DEFAULT_MULTIPLIER)
        return 0.5 + (peso_original - 0.5) * multiplicador


# ============================================
# MarkerExtractor
# ============================================

class MarkerExtractor:
    def __init__(self, llm_api_key: Optional[str] = None,
                 provider: str = "anthropic",
                 model: str = "claude-sonnet-4-6",
                 pattern_library: Optional["PatternLibrary"] = None):
        self.llm_api_key = llm_api_key or os.environ.get("LLM_API_KEY")
        self.provider = provider
        self.model = model
        self.pattern_library = pattern_library

    def _tokens_disponibles(self) -> List[str]:
        if not self.pattern_library:
            return []
        tokens = set()
        for patron in self.pattern_library.patterns.values():
            tokens.update(patron.get("tokens_favor", {}).keys())
            tokens.update(patron.get("tokens_contra", {}).keys())
        return sorted(tokens)

    def extract_from_text(self, text: str) -> List[Marker]:
        if not self.llm_api_key:
            print("Sin LLM: no se extraen marcadores")
            return []
        try:
            return self._extract_via_llm(text)
        except Exception as e:
            print(f"Extracción LLM falló ({e}); se continúa sin marcadores.")
            return []

    def _extract_via_llm(self, text: str) -> List[Marker]:
        tokens_disponibles = self._tokens_disponibles()
        if tokens_disponibles:
            guia_tokens = (
                "Usa preferentemente uno de estos tokens si el texto lo justifica "
                "(no inventes uno nuevo si alguno de estos ya aplica): "
                + ", ".join(tokens_disponibles) + ". "
                "Si ninguno aplica bien, puedes proponer un token nuevo en snake_case."
            )
        else:
            guia_tokens = "No asumas un dominio específico; usa snake_case para el token."

        prompt = (
            "Extrae marcadores observables del siguiente texto. "
            "Devuelve SOLO un array JSON, sin explicación, con objetos de forma "
            '{"token": "...", "value": "...", "confidence": 0.0-1.0}. '
            + guia_tokens + "\n\nTexto:\n" + text
        )
        if self.provider != "anthropic":
            raise ValueError(f"Proveedor no soportado: {self.provider}")
        body = json.dumps({
            "model": self.model,
            "max_tokens": 500,
            "messages": [{"role": "user", "content": prompt}]
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=body,
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.llm_api_key,
                "anthropic-version": "2023-06-01"
            }
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        raw_text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text").strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        parsed = json.loads(raw_text)
        return [Marker(token=i["token"], value=i["value"],
                        confidence=float(i.get("confidence", 0.5)),
                        source="llm_extraction") for i in parsed]


# ============================================
# LatentMemory
# ============================================

class LatentMemory:
    DECAY_PER_DAY = 0.05
    MIN_RETAINED_CONFIDENCE = 0.1

    def __init__(self, dbpath: str = "memory.db"):
        self.conn = sqlite3.connect(dbpath)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS markers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT, value TEXT, confidence REAL,
                timestamp TEXT, source TEXT, active INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()

    def store(self, marker: Marker, active: bool = False):
        self.cursor.execute("""
            INSERT INTO markers (token, value, confidence, timestamp, source, active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (marker.token, marker.value, marker.confidence, marker.timestamp,
              marker.source, 1 if active else 0))
        self.conn.commit()

    def get_all_latent(self):
        self.cursor.execute("SELECT * FROM markers WHERE active = 0")
        return self.cursor.fetchall()

    def _decayed_confidence(self, original_confidence: float, timestamp_str: str) -> float:
        try:
            ts = datetime.datetime.fromisoformat(timestamp_str)
        except ValueError:
            return original_confidence
        days_inactive = (datetime.datetime.now() - ts).total_seconds() / 86400.0
        decayed = original_confidence * (1 - self.DECAY_PER_DAY) ** max(0, days_inactive)
        return max(self.MIN_RETAINED_CONFIDENCE, decayed)

    def store_quarantined(self, marker: Marker):
        self.cursor.execute("""
            INSERT INTO markers (token, value, confidence, timestamp, source, active)
            VALUES (?, ?, ?, ?, ?, -1)
        """, (marker.token, marker.value, marker.confidence, marker.timestamp, marker.source))
        self.conn.commit()

    def reactivate_by_similarity(self, question: str, threshold: float = 0.5,
                                  priority_tokens: Optional[List[str]] = None):
        self.cursor.execute("SELECT * FROM markers WHERE active = 0")
        latent = self.cursor.fetchall()
        q = question.lower()
        priority = set(t.lower() for t in (priority_tokens or []))

        def sort_key(row):
            token = str(row[1]).lower()
            return 0 if token in priority else 1
        latent.sort(key=sort_key)

        reactivated = []
        for row in latent:
            value, token = str(row[2]).lower(), str(row[1]).lower()
            if value in q or token in q or token in priority:
                decayed_conf = self._decayed_confidence(row[3], row[4])
                self.cursor.execute("UPDATE markers SET active = 1, confidence = ? WHERE id = ?",
                                     (decayed_conf, row[0]))
                reactivated.append(row)
        self.conn.commit()
        return reactivated


# ============================================
# TracingEngine
# ============================================

class TracingEngine:
    def __init__(self, patterns_file: str = "patterns.json", memory_db: str = "memory.db",
                 llm_api_key: Optional[str] = None, epsilon: float = 0.05,
                 theta_ambiguedad: float = 0.1, delta_min_base: float = 0.1,
                 delta_min_max: float = 0.25, sigma_sorpresa_scale: float = 0.3,
                 quarantine_pattern: str = "vulnerabilidad_sistemica",
                 quarantine_threshold: float = 0.85):
        self.patterns = PatternLibrary(patterns_file)
        self.memory = LatentMemory(memory_db)
        self.extractor = MarkerExtractor(llm_api_key=llm_api_key, pattern_library=self.patterns)
        self.hypotheses: Dict[str, Hypothesis] = {}
        self.epsilon = epsilon
        self.theta_ambiguedad = theta_ambiguedad
        self.delta_min_base = delta_min_base
        self.delta_min_max = delta_min_max
        self.sigma_sorpresa_scale = sigma_sorpresa_scale
        self.quarantine_pattern = quarantine_pattern
        self.quarantine_threshold = quarantine_threshold

    def start_question(self, question: str) -> str:
        pattern_names = self.patterns.get_patterns_for_question(question)
        self.hypotheses = {name: Hypothesis(name, prior=0.5) for name in pattern_names}
        self.memory.reactivate_by_similarity(question)
        return f"Pregunta activa: {question}\nPatrones activados: {', '.join(pattern_names) or '(ninguno)'}"

    def _global_indeterminado(self) -> bool:
        if not self.hypotheses:
            return False
        return all(h.is_indeterminado() for h in self.hypotheses.values())

    def _convergencia(self) -> float:
        decided = [h for h in self.hypotheses.values() if not h.is_indeterminado()]
        if not decided:
            return 0.0
        signed = []
        for h in decided:
            total = len(h.favor) + len(h.contra)
            strength = (len(h.favor) - len(h.contra)) / total if total > 0 else 0.0
            signed.append((1 if strength >= 0 else -1, abs(strength)))
        pos = [s for d, s in signed if d > 0]
        neg = [s for d, s in signed if d < 0]
        majority = pos if len(pos) >= len(neg) else neg
        if not majority:
            return 0.0
        return round((len(majority) / len(decided)) * (sum(majority) / len(majority)), 4)

    def _delta_h(self, markers: List[Marker]) -> float:
        if not markers:
            return 0.0
        return sum(m.uncertainty() for m in markers) / len(markers)

    def _sigma_sorpresa(self, markers: List[Marker]) -> float:
        if len(markers) < 2:
            return 0.0
        uncertainties = [m.uncertainty() for m in markers]
        return statistics.pstdev(uncertainties)

    def _p_azar(self, sigma_sorpresa: float) -> float:
        spread = sigma_sorpresa * self.sigma_sorpresa_scale
        return max(0.0, min(1.0, 0.5 + random.uniform(-spread, spread)))

    def _filter_quarantine(self, markers: List[Marker]) -> (List[Marker], List[Marker]):
        pesos = []
        for m in markers:
            w = self.patterns.get_weight(self.quarantine_pattern, m.token, True)
            pesos.append(w)

        suma = sum(pesos)
        limpios, cuarentena = [], []
        if suma >= self.quarantine_threshold:
            for m, w in zip(markers, pesos):
                if w > 0:
                    cuarentena.append(m)
                    self.memory.store_quarantined(m)
                else:
                    limpios.append(m)
        else:
            limpios = markers
        return limpios, cuarentena

    def _monte_carlo_p_azar(self, sigma_sorpresa_t: float, epsilon: float = 0.005,
                             min_n: int = 50, max_n: int = 200000, batch: int = 200):
        sigma_estimada_inicial = sigma_sorpresa_t + self.delta_min_base
        n_inicial = max(min_n, int((sigma_estimada_inicial / epsilon) ** 2)) if epsilon > 0 else min_n
        n_inicial = min(n_inicial, max_n)

        muestras = [self._p_azar(sigma_sorpresa_t) for _ in range(n_inicial)]
        convergencia_alcanzada = False
        error_estandar_final = None

        while len(muestras) < max_n:
            n_actual = len(muestras)
            sigma_muestral = statistics.pstdev(muestras) if n_actual > 1 else 0.0
            se = sigma_muestral / (n_actual ** 0.5) if n_actual > 0 else float('inf')
            error_estandar_final = se
            if se < epsilon:
                convergencia_alcanzada = True
                break
            faltan = min(batch, max_n - n_actual)
            if faltan <= 0:
                break
            muestras.extend(self._p_azar(sigma_sorpresa_t) for _ in range(faltan))

        sigma_muestral_final = statistics.pstdev(muestras) if len(muestras) > 1 else 0.0
        if error_estandar_final is None:
            error_estandar_final = sigma_muestral_final / (len(muestras) ** 0.5) if muestras else 0.0
            convergencia_alcanzada = error_estandar_final < epsilon

        return {
            "media_p_azar": round(sum(muestras) / len(muestras), 6) if muestras else 0.5,
            "n_simulaciones_usadas": len(muestras),
            "sigma_estimada_inicial": round(sigma_estimada_inicial, 6),
            "sigma_muestral_final": round(sigma_muestral_final, 6),
            "error_estandar_final": round(error_estandar_final, 6),
            "convergencia_alcanzada": convergencia_alcanzada
        }

    def process_observation(self, text: str, monte_carlo: bool = True,
                             monte_carlo_epsilon: float = 0.005) -> Dict[str, Any]:
        markers_crudos = self.extractor.extract_from_text(text)
        markers, en_cuarentena = self._filter_quarantine(markers_crudos)

        for hyp in self.hypotheses.values():
            hyp.apply_epsilon(self.epsilon)

        for m in markers:
            self.memory.store(m, active=True)

        delta_h_t = self._delta_h(markers)
        sigma_sorpresa_t = self._sigma_sorpresa(markers)
        delta_min_t = self.delta_min_base + (self.delta_min_max - self.delta_min_base) * delta_h_t

        for m in markers:
            for hyp_name, hyp in self.hypotheses.items():
                w_favor = self.patterns.get_weight(hyp_name, m.token, True)
                if w_favor > 0:
                    hyp.support(w_favor)
                    hyp.favor.append(m.to_dict())

                w_contra = self.patterns.get_weight(hyp_name, m.token, False)
                if w_contra > 0:
                    hyp.contradict(w_contra)
                    hyp.contra.append(m.to_dict())
                    otras_condiciones = [om.to_dict() for om in markers if om is not m]
                    hyp.contradicciones_contextuales.append({
                        "marcador": m.to_dict(),
                        "condiciones": otras_condiciones
                    })

        for hyp in self.hypotheses.values():
            hyp.probability = max(delta_min_t, min(1 - delta_min_t, hyp.probability))

        reevaluaciones = []
        for hyp_name, hyp in self.hypotheses.items():
            favor_strength = len(hyp.favor)
            contra_strength = len(hyp.contra)
            total = favor_strength + contra_strength
            if total > 0:
                diff = abs(favor_strength - contra_strength) / total
                if diff < self.theta_ambiguedad:
                    tokens_limite = [m["token"] for m in (hyp.favor + hyp.contra)]
                    self.memory.reactivate_by_similarity(
                        question=" ".join(tokens_limite), priority_tokens=tokens_limite
                    )
                    reevaluaciones.append(hyp_name)

        p_azar_t = self._p_azar(sigma_sorpresa_t)
        mc_info = None
        if monte_carlo:
            mc_info = self._monte_carlo_p_azar(sigma_sorpresa_t, epsilon=monte_carlo_epsilon)
            p_azar_t = mc_info["media_p_azar"]
        p_indet = 0.5
        resultado_hipotesis = []
        for hyp in self.hypotheses.values():
            peso_evidencia = max(0.0, 1 - delta_min_t - sigma_sorpresa_t)
            p_final = (peso_evidencia * hyp.probability
                       + delta_min_t * p_indet
                       + sigma_sorpresa_t * p_azar_t)
            d = hyp.to_dict()
            d["p_final"] = round(p_final, 4)
            resultado_hipotesis.append(d)

        return {
            "markers_extracted": [m.to_dict() for m in markers],
            "hypotheses": resultado_hipotesis,
            "indeterminado": self._global_indeterminado(),
            "convergencia": self._convergencia(),
            "delta_h_t": round(delta_h_t, 4),
            "sigma_sorpresa_t": round(sigma_sorpresa_t, 4),
            "delta_min_t": round(delta_min_t, 4),
            "p_azar_t": round(p_azar_t, 4),
            "reevaluaciones_50_50": reevaluaciones,
            "cuarentena": [m.to_dict() for m in en_cuarentena],
            "monte_carlo": mc_info,
            "advertencia": "Décimo Hombre activo (dinámico). Incertidumbre irreducible presente."
        }

    def get_final_reading(self) -> Dict[str, Any]:
        return {
            "hypotheses": [h.to_dict() for h in self.hypotheses.values()],
            "indeterminado": self._global_indeterminado(),
            "convergencia": self._convergencia(),
            "advertencia": "Décimo Hombre activo (dinámico). Incertidumbre irreducible presente."
        }


if __name__ == "__main__":
    test_patterns_path = "patterns_v3_test.json"
    with open(test_patterns_path, "w", encoding="utf-8") as f:
        json.dump({
            "crisis_vocacional": {
                "description": "Probabilidad de abandono laboral",
                "tokens_favor": {"frustracion": 0.7, "mencion_renuncia": 0.6},
                "tokens_contra": {"compromiso": 0.7}
            },
            "arquetipo_heroe": {
                "description": "Busca desafios",
                "tokens_favor": {"desafio": 0.6},
                "tokens_contra": {"evitacion": 0.7}
            }
        }, f, indent=2)

    engine = TracingEngine(patterns_file=test_patterns_path, memory_db="memory_v3_test.db")
    print(engine.start_question("¿Cual es la trayectoria de este caso?"))

    simulated = [
        Marker(token="frustracion", value="se siente frustrado", confidence=0.9),
        Marker(token="mencion_renuncia", value="menciono renunciar", confidence=0.5),
        Marker(token="desafio", value="busca un reto nuevo", confidence=0.6),
    ]
    engine.extractor.extract_from_text = lambda text: simulated

    resultado = engine.process_observation("texto de prueba")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

    print("\nLectura final:")
    print(json.dumps(engine.get_final_reading(), indent=2, ensure_ascii=False))
