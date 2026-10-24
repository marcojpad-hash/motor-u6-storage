#!/usr/bin/env python3
"""Ensambla en motor/ las piezas de todas las líneas (copia exacta, sha verificado). No edita originales."""
import hashlib, json, shutil, zipfile, io, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent; M = ROOT / "motor"
T = Path("/workspace/pred_hist_bio_in/TRANSFER_V15_1"); CK = T / "CHECKPOINT_REPRODUCIBLE_20260920"
G = Path("/workspace/CONSOLIDADO_GUARDIANES_20260927/guardianes"); E = Path("/workspace/TIRADA_ESTRICTA_20260927/motor")
def sha(b): return hashlib.sha256(b).hexdigest()
def leer(loc):
    parts = str(loc).split("!"); b = open(parts[0], "rb").read()
    for p in parts[1:]: b = zipfile.ZipFile(io.BytesIO(b)).read(p)
    return b
# (destino, origen, sha8 esperado, línea/origen legible)
P = [
 ("modo_estricto_v1.py", E/"modo_estricto_v1.py", "c0fe7fbd", "TIRADA_ESTRICTA 27-sep"),
 ("lectura_negativo_ricci_vs_billar_v0_1.py", T/"NEGATIVO_20260927/lectura_negativo_ricci_vs_billar_v0_1.py", "777666dc", "T/NEGATIVO_20260927"),
 ("control_latencia_decimo_hombre.py", G/"control_latencia_decimo_hombre.py", "ff03241d", "T (guardianes)"),
 ("guardian_acero_rival_v1.py", G/"guardian_acero_rival_v1.py", "314d19f5", "CONSOLIDADO_GUARDIANES"),
 ("guardian_logica_copi_v1.py", G/"guardian_logica_copi_v1.py", "0101f666", "CONSOLIDADO_GUARDIANES"),
 ("guardian_tropos_beristain_v1.py", G/"guardian_tropos_beristain_v1.py", "1886af5e", "CONSOLIDADO_GUARDIANES"),
 ("plugin_metodo_rigor.py", G/"plugin_metodo_rigor.py", "a4f5659e", "T"),
 ("plugin_polaridad_causal.py", G/"plugin_polaridad_causal.py", "534ae636", "T"),
 ("plugin_pregunta_dirigida_v0_5_1.py", G/"plugin_pregunta_dirigida_v0_5_1.py", "8aa9fc79", "CONSOLIDADO_GUARDIANES (base SB 0.5.0)"),
 ("plugin_pregunta_dirigida.py", G/"plugin_pregunta_dirigida_v0_5_1.py", "8aa9fc79", "0.5.1 sustituye a 0.4.1 (4513e6b2) en la llamada opt_qdir"),
 ("sidecar_ablacion_hombre_acero.py", G/"sidecar_ablacion_hombre_acero.py", "7db774c0", "CHECKPOINT 20"),
 ("plugin_aquiles_h.py", T/"UNIFICADO_V0_16_RUN_20260926/plugins_core_b9/plugin_aquiles_h.py", "3fe976df", "plugins_core_b9 (reporta seed; ⊇ 4aeda7ca)"),
 ("plugin_embudo_clinico.py", T/"UNIFICADO_V0_16_RUN_20260926/plugins_core_b9/plugin_embudo_clinico.py", "deb37f7e", "plugins_core_b9 (formativa por posición; ⊇ a87bc038)"),
 ("plugin_capa2_antecedentes_arquetipos.py", CK/"02_TUBO/plugin_capa2_antecedentes_arquetipos.py", "e20f2ad9", "CHECKPOINT 20 (estereotipos+luces+amantes; ⊇ 79bc4b48)"),
 ("catalogo_capa2_familias_semilla.json", CK/"02_TUBO/catalogo_capa2_familias_semilla.json", "a7142b3e", "CHECKPOINT 20 (7 familias; ⊇ 5b35087c)"),
 ("sidecar_luces_gemini_packs.py", CK/"02_TUBO/sidecar_luces_gemini_packs.py", "16ae145e", "CHECKPOINT 20"),
 ("registro_luces_gemini_packs.json", CK/"02_TUBO/registro_luces_gemini_packs.json", "bafef9f1", "CHECKPOINT 20"),
 ("sidecar_amantes_arquetipos.py", CK/"02_TUBO/sidecar_amantes_arquetipos.py", "7923d49c", "CHECKPOINT 20"),
 ("registro_sidecar_amantes_arquetipos.json", CK/"02_TUBO/registro_sidecar_amantes_arquetipos.json", "3dab8d38", "CHECKPOINT 20"),
 ("plugin_circulo_monomito_v2.py", "/workspace/pred_hist_bio_in/TRANSFER_V15_1", "8cd81bc1", "monomito v2 (resuelve en serie completa)"),
 ("plugin_alias_reactivacion.py", CK/"02_TUBO/plugin_alias_reactivacion.py", "5c630bc5", "CHECKPOINT 20 / inbox 14"),
 ("plugin_fix_entrada.py", CK/"02_TUBO/plugin_fix_entrada.py", "8ebdcd0d", "CHECKPOINT 20 / inbox 14"),
 ("plugin_familias_gloria_sacro.py", CK/"02_TUBO/plugin_familias_gloria_sacro.py", "8cc568a9", "CHECKPOINT 20"),
 ("protocolo_kernel_motor.py", CK/"02_TUBO/protocolo_kernel_motor.py", "e95f1802", "CHECKPOINT 20 (orden 0)"),
 ("control_flujo_soluciones.py", CK/"02_TUBO/control_flujo_soluciones.py", "058e8348", "CHECKPOINT 20 (⊇ 9e215d64)"),
 ("candado_plugins.py", T/"MOTOR_V15_3_COMPLETO_CORRE_20260921/candado_plugins.py", "2a669505", "COMPLETO_CORRE 21 (bypass hash; ⊇ c4949500)"),
 ("matriz_corrida.py", CK/"02_TUBO/matriz_corrida.py", "9cf60a54", "CHECKPOINT 20 (entrada CONTROL)"),
 ("plugin_aquiles_ancla_estricto.py", CK/"02_TUBO/plugin_aquiles_ancla_estricto.py", "16b793d3", "CHECKPOINT 20 (⊇ 0019abc5)"),
 ("sidecar_corte_memento.py", CK/"03_LATERALES_VIGENTES/sidecar_corte_memento.py", "e56f5fb1", "CHECKPOINT 20 (Bus Capa 2: Memento PRE)"),
 ("sidecar_trazabilidad_temporal.py", CK/"03_LATERALES_VIGENTES/sidecar_trazabilidad_temporal.py", "8c54ea39", "CHECKPOINT 20 (⊇ 0a2faffb, 1da02564)"),
 ("capa_integracion_semantica_v1_2.py", CK/"03_LATERALES_VIGENTES/capa_integracion_semantica_v1_2.py", "4de3ddef", "CHECKPOINT 20"),
 ("capa_interrelacion_tokens.py", CK/"03_LATERALES_VIGENTES/capa_interrelacion_tokens.py", "c7491981", "CHECKPOINT 20"),
 ("sidecar_cuerpo_arco__BUG_A_SIN_CONFIRMAR.py", CK/"03_LATERALES_VIGENTES/sidecar_cuerpo_arco__BUG_A_SIN_CONFIRMAR.py", "cf153eeb", "CHECKPOINT 20 (marcado BUG sin confirmar)"),
 ("plugin_souriau_210141.py", CK/"03_LATERALES_VIGENTES/souriau_v1_4/plugin_souriau_210141.py", "2129f5d6", "CHECKPOINT 20 souriau v1.4"),
 ("sidecar_lente_souriau.py", "/workspace/lentes_billar_ricci/sidecar_lente_souriau.py", "2fb351df", "lentes_billar_ricci"),
 ("predictor_vecinos_prefijo_v1.py", CK/"03_LATERALES_VIGENTES/predictor_vecinos_prefijo_v1.py", "903d4a5b", "CHECKPOINT 20"),
 ("zri_experience_v0_1.py", "/workspace/scratch_zri/zri_v0_1/zri_experience_v0_1.py", "500fa2b1", "scratch_zri Z-RI v0.1"),
 ("zri_coupling_v0_2.py", "/workspace/scratch_zri/zri_v0_1/zri_coupling_v0_2.py", "38aaeb5d", "scratch_zri Z-RI v0.2"),
 ("tusi_par_indice_exploratorio_v0_1.py", T/"SCHRODINGER_20260927/tusi_par_indice_exploratorio_v0_1.py", "290d1bb3", "SCHRODINGER_20260927 (referencia; el adaptador replica su fórmula)"),
 ("schrodinger_transport_esqueleto_v0_1.py", T/"SCHRODINGER_20260927/schrodinger_transport_esqueleto_v0_1.py", "e88cd66f", "SCHRODINGER_20260927 (esqueleto)"),
 ("formular_h_apuesta.py", T/"IN_20260926_FORMULAR/formular_h_apuesta.py", "0319a42b", "línea contrato (IN_20260926_FORMULAR); corre como contraste, no escribe H"),
 ("filtro_identidad_zoom_out_zoom_in.py", "/workspace/obra1_zoom_identidad/filtro_identidad_zoom_out_zoom_in.py", "1d00fb10", "obra1_zoom_identidad"),
 ("sensor_perfil_narrador_v0_1.py", "/workspace/PERFIL_NARRADOR_20260927/sensor/sensor_perfil_narrador_v0_1.py", "83d7717f", "PERFIL_NARRADOR 27-sep"),
 ("lexico_narrador_v0_1.py", "/workspace/PERFIL_NARRADOR_20260927/sensor/lexico_narrador_v0_1.py", "0d6bc005", "PERFIL_NARRADOR 27-sep"),
 ("PUENTE_244_FAMILIAS.json", "/workspace/EQUIVALENCIAS_ESCALA_20260927/PUENTE_244_FAMILIAS.json", "3cc9fd25", "EQUIVALENCIAS_ESCALA 27-sep"),
 ("MATRIZ_EQUIVALENCIAS_ESCALA.json", "/workspace/EQUIVALENCIAS_ESCALA_20260927/MATRIZ_EQUIVALENCIAS_ESCALA.json", "e8212852", "EQUIVALENCIAS_ESCALA 27-sep"),
 ("coactivacion_escalas.py", "/workspace/EQUIVALENCIAS_ESCALA_20260927/coactivacion_escalas.py", "f316ebb0", "EQUIVALENCIAS_ESCALA 27-sep"),
 ("normalizar_familia_tokens.py", "/workspace/TOKENS_GEMINI_FAMILIAS_20260927/normalizar_familia_tokens.py", "da123529", "TOKENS_GEMINI_FAMILIAS 27-sep"),
]
inv = json.load(open("/tmp/inv_py.json")) if Path("/tmp/inv_py.json").exists() else {}
man = []
for dst, src, s8, origen in P:
    if src == "/workspace/pred_hist_bio_in/TRANSFER_V15_1":  # buscar por sha en inventario (zip)
        d = next(v for k, v in inv[dst].items() if k.startswith(s8)); b = leer(d["locs"][0]); src = d["locs"][0]
    else:
        b = leer(src)
    assert sha(b).startswith(s8), (dst, sha(b)[:8], s8)
    (M / dst).write_bytes(b)
    man.append({"archivo": dst, "sha256": sha(b), "bytes": len(b), "origen": str(src), "nota": origen})
fam_dir = Path("/workspace/TOKENS_GEMINI_FAMILIAS_20260927/normalizados")
for f in sorted(fam_dir.glob("*.json")):
    b = f.read_bytes(); (M / "familias_tokens" / f.name).write_bytes(b)
    man.append({"archivo": f"familias_tokens/{f.name}", "sha256": sha(b), "bytes": len(b), "origen": str(f), "nota": "familia lateral normalizada"})
json.dump(man, open(ROOT / "tablas/PIEZAS_ENSAMBLADAS.json", "w"), ensure_ascii=False, indent=1)
print(len(man), "piezas")
