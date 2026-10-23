# Comparativa ciega de narrativa

Incluye `prueba_ciega.html`, una interfaz local para comparar análisis etiquetados A/B.

## Uso

1. Ejecuta la comparativa con `comparar.py` para crear `crudos.json`.
2. Abre `prueba_ciega.html` en un navegador.
3. Carga `crudos.json` en el selector de archivos.
4. Evalúa cada pieza y descarga `valoraciones_ciegas.json`.
5. El coordinador debe guardar aparte `clave_privada_modelos.json`; no debe compartirlo con la persona evaluadora hasta que termine.

La interfaz no muestra los nombres de los modelos ni las métricas de coste, tokens o tiempo. Los resultados descargados incluyen la correspondencia A/B para poder analizar los votos después; por eso el archivo descargado debe mantenerse privado y no entregarse al evaluador antes de terminar.

## Importante

- Esta es una plantilla inicial; hay que probarla con la salida real de `comparar.py` antes de usarla con las 20 piezas.
- No publiques `crudos.json`, `piezas.json`, `piezas_prueba.json`, `valoraciones_ciegas.json` ni ninguna clave de API.
- La aleatorización A/B se hace por pieza al cargar los datos. No se muestran las métricas técnicas.
- La clave de correspondencias debe custodiarse por separado del archivo que ve la persona evaluadora. Para una evaluación estrictamente ciega, la persona evaluadora no debe recibir el JSON descargado hasta haber acabado.
