# Semillas JSON para la ruta entry-only

Esta carpeta recibe únicamente JSON local con la forma:

~~~json
{
  "cases": [
    {
      "case_id": "F008_SUBJECT_01",
      "question": "Pregunta congelada antes de formular H1/H2",
      "person": "Sujeto nuevo",
      "tipo_sujeto": "biografia",
      "freeze": "YYYY-MM-DD",
      "modo_z": "historico",
      "fecha_nacimiento": "YYYY-MM-DD",
      "fecha_muerte": "YYYY-MM-DD",
      "z_trabajo": "YYYY-MM-DD",
      "z90_date": "YYYY-MM-DD",
      "random_seed": 20261123,
      "preparacion_ciega": {
        "preparador_entrada": "identidad preparador",
        "custodio_destino": "identidad custodio",
        "vio_destino": false
      },
      "cuts": [
        {
          "cut_id": "C1",
          "date": "YYYY-MM-DD",
          "window_start": "YYYY-MM-DD",
          "hecho": "Afirmación respaldada",
          "P": [["token_del_catalogo", 0.70]],
          "A": [],
          "C": [],
          "evidencia": [
            {
              "afirmacion": "Afirmación concreta",
              "claim_date": "YYYY-MM-DD",
              "source_date": "YYYY-MM-DD",
              "source_url": "https://...",
              "tipo_fuente": "primaria",
              "conocido_en_Z": "sí"
            }
          ]
        }
      ]
    }
  ]
}
~~~

Reglas:
- El archivo debe llamarse .json; el CLI rechaza módulos Python y rutas fuera de esta carpeta.
- Cada sujeto y case_id debe ser nuevo. No se permiten destinos, desenlaces, H1/H2 ni rankings en el input.
- Todas las afirmaciones requieren fechas y fuentes primarias aptas. source_date y claim_date deben ser anteriores o iguales al corte correspondiente.
- En biografías: Z90 calculada desde nacimiento/muerte; primer corte exactamente en nacimiento; todas las ventanas empiezan en nacimiento; último corte exactamente en Z90. No hay número fijo de cortes.
- Los pesos P/A/C deben estar entre 0.60 y 0.84 y los tokens pertenecer al catálogo vigente.
- preparacion_ciega registra roles declarados; el script no puede probar identidad ni independencia real del custodio.
- El script escribe solo entrada.json y entrada.sha256 en entradas_solo/. No crea destinos, desenlaces, RESULT, RECIBO, CEB ni manifiestos de corrida.
- No ejecutar la ruta con F007 actual. F007 no cumple fuentes primarias ni custodia independiente. No ejecutar el motor hasta que el custodio entregue el destino sellado por un canal separado.

El contenido JSON real está excluido de Git por .gitignore; no versionar semillas operativas.
