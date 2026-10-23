# Comparativa ciega de narrativa: Sonnet vs. Haiku

Esta carpeta contiene los scripts para ejecutar una comparativa de modelos y una interfaz local para valorar las respuestas sin ver qué modelo produjo cada una.

> **Estado actual:** `piezas.json` puede estar vacío (`[]`). En ese caso no se puede ejecutar la comparativa real hasta añadir las piezas autorizadas. La interfaz HTML tampoco contiene análisis por sí sola: necesita el archivo `crudos.json` generado por el script.

## Contenido

- `comparar.py`: ejecuta ambos modelos sobre las mismas piezas y guarda respuestas y métricas.
- `extraer_piezas.py`: extrae piezas desde la base de datos configurada en el entorno del proyecto.
- `piezas.json`: archivo de entrada previsto para la comparativa real.
- `piezas_prueba.json`: conjunto pequeño de prueba; revisa su contenido antes de compartirlo.
- `prueba_ciega.html`: interfaz local para valorar las respuestas A/B.

## Requisitos previos

1. Copiar la carpeta `experimentos/` dentro de la raíz del repositorio `influenza-backend`.
2. Tener Python y las dependencias del proyecto instaladas. Lo más seguro es utilizar el entorno virtual y las dependencias que ya usa el proyecto, en vez de actualizar paquetes al azar.
3. Tener una clave de API de Anthropic autorizada y acceso a los dos modelos configurados en `comparar.py`.
4. Disponer de las piezas de texto que se van a comparar y permiso para usarlas.

No pongas la clave de API en este README, en un archivo JSON, ni en GitHub. Configúrala solo en la Terminal de la sesión en la que vayas a ejecutar el script. Si el proyecto usa la variable estándar `ANTHROPIC_API_KEY`, en macOS puedes hacer:

```bash
export ANTHROPIC_API_KEY='PEGA_AQUI_TU_CLAVE'
```

No compartas capturas de pantalla de la Terminal si la clave aparece visible. Al cerrar esa Terminal, la variable normalmente deja de estar definida.

## 1. Abrir la carpeta del proyecto

Desde Terminal, entra en la raíz del repositorio. Si lo tienes en `~/Documents/influenza-backend`, ejecuta:

```bash
cd ~/Documents/influenza-backend
```

Activa el entorno virtual del proyecto si existe. Por ejemplo, si se llama `venv`:

```bash
source venv/bin/activate
```

Si tu entorno virtual tiene otro nombre o está en otra ubicación, utiliza la ruta real. Instala las dependencias según las instrucciones del repositorio; no actualices la versión del SDK de Anthropic sin comprobar la compatibilidad con el código.

## 2. Preparar las piezas

Comprueba el archivo de entrada:

```bash
cat experimentos/piezas.json
```

Si muestra `[]`, está vacío y no hay piezas que comparar.

Para extraer piezas de la base de datos, revisa primero las instrucciones y opciones del script:

```bash
python3 experimentos/extraer_piezas.py --help
```

El script necesita que la configuración de base de datos apunte al entorno correcto. Confirma con el responsable qué base de datos debes consultar y qué piezas puedes utilizar. No ejecutes extracciones sobre producción ni compartas textos de clientes sin autorización.

Después de la extracción, revisa localmente que el archivo tenga las piezas esperadas y que cada texto esté completo. No publiques `piezas.json` en un repositorio público o compartido si contiene datos de clientes.

## 3. Hacer una prueba pequeña antes de la ejecución completa

Desde la raíz del repositorio, prueba primero con el archivo de muestra:

```bash
python3 experimentos/comparar.py --max 1 --piezas experimentos/piezas_prueba.json
```

El comando está pensado para comprobar una ejecución pequeña. Verifica en la salida del programa cuál es el nombre y la ubicación del archivo de resultados que genera; el flujo previsto para la interfaz usa `crudos.json`.

Si falla, no lances todavía las 20 piezas. Comprueba el mensaje de error, la variable de API, los permisos de los modelos y las dependencias instaladas. El modelo Haiku puede admitir parámetros distintos de Sonnet, así que hay que validar que el script aplique parámetros compatibles sin cambiar el texto de entrada ni el prompt común.

## 4. Ejecutar la comparativa real

Cuando la prueba pequeña haya terminado correctamente y `piezas.json` contenga las piezas autorizadas, ejecuta:

```bash
python3 experimentos/comparar.py
```

Antes de ejecutarlo, revisa en `comparar.py` los valores por defecto de entrada y salida para confirmar que leerá `experimentos/piezas.json` y dónde guardará los resultados. Las llamadas a modelos generan costes de API. Ejecuta la comparativa completa solo con autorización y después de comprobar el coste estimado.

## 5. Valorar las respuestas a ciegas

1. Abre el HTML:

   ```bash
   open experimentos/prueba_ciega.html
   ```

2. En la página, carga el archivo de resultados (`crudos.json`, si ese es el archivo generado).
3. Para cada pieza, lee las dos respuestas identificadas como A y B y registra tu preferencia o empate. Añade comentarios si ayudan a explicar la valoración.
4. Descarga el archivo de valoraciones.
5. Guarda la clave privada que relaciona A/B con los modelos en un lugar separado y restringido. No se la entregues a la persona evaluadora hasta que haya terminado todas las valoraciones.

La asignación A/B se aleatoriza por pieza al cargar los resultados. Esta es una protección práctica frente al sesgo, no una barrera de seguridad: alguien con acceso al código o a los archivos locales podría inspeccionar la correspondencia.

## Archivos que no se deben subir a GitHub

No publiques claves de API ni datos de clientes. En particular, revisa antes de compartir:

- `piezas.json`
- `piezas_prueba.json`
- `crudos.json` y cualquier salida equivalente
- el archivo de valoraciones y la clave privada de correspondencias
- cualquier `.env` o archivo con credenciales

Aunque `piezas.json` esté vacío ahora, no significa que vaya a seguir vacío después de extraer datos. Mantén los archivos de datos y resultados en local, salvo autorización explícita.

## Limitaciones y comprobaciones pendientes

- La interfaz debe probarse con un `crudos.json` real generado por la versión actual de `comparar.py`; no des por hecho que los formatos encajan hasta hacer esa prueba.
- No ejecutes la evaluación completa hasta confirmar que ambos modelos se llaman correctamente y que las métricas de coste/tokens/tiempo se guardan fuera de la vista del evaluador.
- Este README describe el flujo previsto; si cambian los argumentos o los nombres de salida de los scripts, actualiza las instrucciones para que coincidan con el código real.
