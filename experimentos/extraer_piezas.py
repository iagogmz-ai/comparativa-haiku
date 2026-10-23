#!/usr/bin/env python3
"""Saca N piezas de la base local para la prueba a ciegas. SOLO LECTURA."""
import argparse
import json
import os
from pathlib import Path

import psycopg2

ap = argparse.ArgumentParser()
ap.add_argument('--n', type=int, default=20)
ap.add_argument('--min', type=int, default=800, dest='minimo', help='caracteres mínimos del texto')
ap.add_argument('--max', type=int, default=6000, dest='maximo', help='caracteres máximos del texto')
ap.add_argument('--semilla', default='haiku-vs-sonnet')
ap.add_argument('--contar', action='store_true', help='solo estadísticas, sin textos')
ap.add_argument('--salida', default=str(Path(__file__).resolve().parent / 'piezas.json'))
a = ap.parse_args()

conn = psycopg2.connect(dbname=os.getenv('DB_NAME', 'influenza'),
                        options='-c default_transaction_read_only=on')
FILTRO = "NOT excluded_from_analysis AND length(text_content) BETWEEN %s AND %s"
with conn.cursor() as cur:
    if a.contar:
        cur.execute("SELECT count(*) FROM pieces")
        print('piezas en total:', cur.fetchone()[0])
        cur.execute(f"SELECT count(*), round(avg(length(text_content))) FROM pieces WHERE {FILTRO}",
                    (a.minimo, a.maximo))
        n, media = cur.fetchone()
        print(f'piezas entre {a.minimo} y {a.maximo} caracteres: {n} (longitud media {media})')
        cur.execute(f"""SELECT coalesce(source_type, '?'), count(*) FROM pieces WHERE {FILTRO}
                        GROUP BY 1 ORDER BY 2 DESC LIMIT 8""", (a.minimo, a.maximo))
        for tipo, k in cur.fetchall():
            print(f'  {tipo}: {k}')
        cur.execute(f"SELECT count(DISTINCT campaign_id) FROM pieces WHERE {FILTRO}", (a.minimo, a.maximo))
        print('campañas distintas:', cur.fetchone()[0])
    else:
        cur.execute(f"""SELECT id::text, title, source, publish_date, text_content FROM pieces
                        WHERE {FILTRO} ORDER BY md5(id::text || %s) LIMIT %s""",
                    (a.minimo, a.maximo, a.semilla, a.n))
        piezas = [{'id': i, 'title': t, 'source': s, 'date': str(d) if d else None, 'text': x}
                  for i, t, s, d, x in cur.fetchall()]
        Path(a.salida).write_text(json.dumps(piezas, ensure_ascii=False, indent=1), encoding='utf-8')
        print(f'{len(piezas)} piezas guardadas en {a.salida}')
        print('longitud media:', round(sum(len(p['text']) for p in piezas) / max(len(piezas), 1)))
conn.close()
