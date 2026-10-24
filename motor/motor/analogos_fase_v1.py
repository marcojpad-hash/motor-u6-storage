"""Analogos por fase. No nombra al caso. No decide H. Solo familias ya en catalogo."""

def para_fase(luces):
    luces=set(luces)
    actos=[]
    if "autoridad" in luces or "poder" in luces:
        actos.append({"fase":"servicio_bajo_autoridad","homologo":"arquetipo_el_gobernante","accion":"sostiene_el_puesto","tokens":["autoridad","poder"]})
    if "ambicion" in luces or "lucha" in luces:
        actos.append({"fase":"ruptura","homologo":"arquetipo_el_rebelde","accion":"deja_el_puesto","tokens":["ambicion","lucha"]})
    if "reconocimiento" in luces or "viaje" in luces:
        actos.append({"fase":"obra_por_encargo","homologo":"arquetipo_el_creador","accion":"sigue_por_obra_no_por_obediencia","tokens":["reconocimiento","viaje"]})
    if "llamado" in luces or "umbral" in luces:
        actos.append({"fase":"cruce","homologo":"arquetipo_el_heroe","accion":"cruza_y_no_regresa_al_mismo_puesto","tokens":["llamado"]})
    return {"status":"EXECUTED","can_decide_H":False,"nombra_caso":False,"actos":actos}
