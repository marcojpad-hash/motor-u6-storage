"""Despues de la apuesta. Agnostico. No narra, no usa el caso, no decide H."""

def entregar(result):
    luces=[]
    for cut in (result.get("motor") or {}).get("cuts") or []:
        for eje,key in (("P","P_top5_ANEXO"),("A","A_top5_ANEXO"),("C","C_top5_ANEXO")):
            for row in (cut.get(key) or [])[:2]:
                luces.append({"corte":cut.get("corte"),"eje":eje,"luz":row[0],"peso":row[1]})
    caminos=[c.get("family") for c in ((result.get("predictor") or {}).get("candidates") or [])[:3]]
    return {
        "status":"EXECUTED",
        "can_decide_H":False,
        "despues_de":"apuesta",
        "agnostico":True,
        "narra":False,
        "caminos":caminos,
        "excluyentes":False,
        "luces_P":[x["luz"] for x in luces if x["eje"]=="P"],
        "luces_A":[x["luz"] for x in luces if x["eje"]=="A"],
        "luces_C":[x["luz"] for x in luces if x["eje"]=="C"],
        "para_el_llm":"traducir caminos y luces con el input. no inventar H. no excluir caminos.",
    }
