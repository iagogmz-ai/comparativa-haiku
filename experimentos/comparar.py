#!/usr/bin/env python3
"""
Compara el análisis de narrativa de dos modelos con el MISMO prompt, sin tocar
el código del proyecto ni ninguna base de datos.

    read -s "ANTHROPIC_API_KEY?Clave: "; export ANTHROPIC_API_KEY
    python experimentos/comparar.py --max 1 --piezas experimentos/piezas_prueba.json
    python experimentos/comparar.py --piezas experimentos/piezas.json
"""
import argparse
import json
import os
import sys
import time
import types
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / 'backend'))

# api_utils apunta cada llamada en el libro de gastos (costes.py, en la base de
# datos). Aquí se anula: esta prueba no escribe en ninguna base.
_costes = types.ModuleType('costes')
_costes.__getattr__ = lambda nombre: (lambda *a, **k: None)
sys.modules['costes'] = _costes

import narrative_extractor as ne  # noqa: E402

# USD por millón de tokens (entrada, salida). Sonnet 4.6: api_utils.py.
# Haiku 5.5: precios de Anthropic para prompts de hasta 100.000 tokens.
PRECIOS = {'claude-sonnet-4-6': (3.00, 15.00), 'claude-haiku-5-5': (0.10, 0.50)}
CACHE_LECTURA, CACHE_ESCRITURA = 0.10, 1.25   # múltiplos del precio de entrada (estimación)

llamadas = []
_original = ne.call_anthropic_with_retry


def _llamar(client, **kw):
    modelo = kw['model']
    if modelo.startswith('claude-haiku-5'):
        # Haiku 5.5 rechaza una temperature distinta de la de por defecto y
        # piensa por defecto: se omite y se desactiva el pensamiento, que es
        # como corre hoy Sonnet. (El SDK 0.40.0 no conoce `thinking`.)
        kw.pop('temperature', None)
        kw['extra_body'] = {'thinking': {'type': 'disabled'}}
    t0 = time.time()
    resp = _original(client, **kw)
    u = resp.usage
    llamadas.append({'modelo': modelo, 'segundos': round(time.time() - t0, 2),
                     'entrada': u.input_tokens, 'salida': u.output_tokens,
                     'cache_lectura': getattr(u, 'cache_read_input_tokens', 0) or 0,
                     'cache_escritura': getattr(u, 'cache_creation_input_tokens', 0) or 0,
                     'stop_reason': getattr(resp, 'stop_reason', None)})
    return resp


ne.call_anthropic_with_retry = _llamar


def coste(modelo, ll):
    pe, ps = PRECIOS[modelo]
    return round(sum((x['entrada'] * pe + x['salida'] * ps
                      + x['cache_lectura'] * pe * CACHE_LECTURA
                      + x['cache_escritura'] * pe * CACHE_ESCRITURA) / 1e6 for x in ll), 6)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--piezas', default=str(AQUI / 'piezas.json'))
    ap.add_argument('--salida', default=str(AQUI / 'crudos.json'))
    ap.add_argument('--max', type=int, default=0)
    a = ap.parse_args()
    if not os.getenv('ANTHROPIC_API_KEY'):
        sys.exit('Falta ANTHROPIC_API_KEY en el entorno de esta terminal')

    from anthropic import Anthropic
    cliente = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'), timeout=120.0, max_retries=2)
    piezas = json.loads(Path(a.piezas).read_text(encoding='utf-8'))
    if a.max:
        piezas = piezas[:a.max]

    extractor = ne.NarrativeExtractor()
    config = {m: {'max_tokens': extractor.MAX_TOKENS,
                  'temperature': extractor.TEMPERATURE if m.startswith('claude-sonnet')
                  else 'por defecto (Haiku 5.5 no admite otra)',
                  'pensamiento': 'sin pensamiento'} for m in PRECIOS}
    filas = []
    for i, p in enumerate(piezas, 1):
        fila = {'pieza': p, 'salidas': {}, 'medidas': {}}
        for modelo in PRECIOS:
            extractor.MODEL = modelo
            llamadas.clear()
            t0 = time.time()
            res = extractor.extract_narrative(text=p['text'], title=p.get('title'),
                                              source=p.get('source'), date=p.get('date'),
                                              client=cliente)
            ll = list(llamadas)
            fila['salidas'][modelo] = res
            fila['medidas'][modelo] = {'ok': res is not None, 'segundos': round(time.time() - t0, 2),
                                       'coste_usd': coste(modelo, ll), 'llamadas': ll}
        filas.append(fila)
        Path(a.salida).write_text(json.dumps({'config': config, 'filas': filas},
                                             ensure_ascii=False, indent=1), encoding='utf-8')
        print(f'[{i}/{len(piezas)}] ' + ' | '.join(
            f"{m}: {'ok' if fila['medidas'][m]['ok'] else 'FALLO'} "
            f"({fila['medidas'][m]['coste_usd']:.5f} USD)" for m in PRECIOS))


if __name__ == '__main__':
    main()
