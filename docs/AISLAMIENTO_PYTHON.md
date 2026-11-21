# Aislamiento entre ejecuciones de Python (PLD-004)

La consola y la corrección de ejercicios ejecutan el código del alumno con Pyodide dentro de un Web
Worker (`frontend/js/pyodide-worker.js`). Todas las ejecuciones comparten **el mismo intérprete**: si
un programa cambia algo del intérprete, el siguiente ejercicio se lo encuentra cambiado. Este documento
explica cómo lo evita `frontend/py/runner.py`, qué se midió para elegir la solución y qué no cubre.

> **No es un sandbox de seguridad.** Pyodide aísla el código del alumno del resto de la página (va en
> un Worker, sin DOM, y `closeNetwork()` le quita la red), pero dentro del Worker el programa puede
> hacer lo que quiera con su propio intérprete. Este aislamiento protege de contaminaciones
> **accidentales** entre ejercicios, no de un programa escrito a propósito para romperlo. Si lo rompe,
> solo se rompe su propia pestaña, y se arregla con «Detener» o recargando la página.

## 1. El problema

Antes de este cambio, `runner.py` (PY-03) solo restauraba las funciones integradas, las entradas de
`sys.modules` que el programa sustituía y el límite de recursión. Todo lo demás pasaba a la ejecución
siguiente. Reproducido con el Pyodide real (314.0.7, Python 3.14) y el `runner.py` de `main`, una
ejecución que hace lo de la columna «Primera ejecución» y, en un intérprete nuevo cada vez, otra después:

| Caso | Primera ejecución | Lo que veía la siguiente (antes) | Ahora |
|---|---|---|---|
| Módulo modificado | `math.sqrt = lambda x: 999` | `math.sqrt(16)` → `999` | `4.0` |
| `sys.path` | `sys.path.insert(0, '/zzz')` | `'/zzz'` sigue en `sys.path` | restaurado |
| `sys.path` reasignado | `sys.path = []` | ningún import nuevo funciona | restaurado |
| Import hook | un buscador en `sys.meta_path` que lanza `ImportError` | **ningún** import nuevo funciona | restaurado |
| Módulo importado por primera vez | `import string; string.ascii_lowercase = 'X'` | `'X'` | `'abc'` |
| Clase de la biblioteca estándar | `json.JSONEncoder.default = …` | `json.dumps(object())` ya no falla | falla como debe |
| Módulo falso en `sys.modules` | `sys.modules['utilidades'] = …` | `import utilidades` funciona | `ModuleNotFoundError` |
| Archivos | `open('datos.txt', 'w')` | el archivo sigue ahí | no existe |
| Carpeta actual | `os.chdir('/tmp/d')` | sigue en `/tmp/d` | restaurada |
| Entorno | `os.environ['X'] = '1'` | `X` sigue definida | restaurado |
| Traza | `sys.settrace(f)` | la traza sigue activa (y ralentiza) | quitada |
| Avisos | `warnings.simplefilter('error')` | `warnings.warn()` lanza una excepción | solo avisa |
| Aleatorios | `random.seed(1)` | la siguiente da siempre los mismos números | no |
| `sys.argv` | `sys.argv.append('x')` | `['', 'x']` | `['']` |
| Dígitos de enteros | `sys.set_int_max_str_digits(640)` | `str(10**1000)` falla | funciona |
| Decimales | `decimal.getcontext().prec = 2` | `Decimal(1)/3` → `0.33` | 28 dígitos |

Los 16 casos fallaban. Con un intérprete compartido, uno solo (el import hook) dejaba la consola
inservible hasta recargar.

## 2. Alternativas medidas

Medido en Node 22 con el mismo paquete de Pyodide que se publica (`npm ci`), Python ya descargado. En
un navegador los tiempos son del mismo orden; `tests/unit/runner-isolation-pyodide.test.mjs` repite la
medida en cada ejecución de la CI.

| Alternativa | Coste por ejecución | Aislamiento | Decisión |
|---|---|---|---|
| Reiniciar Pyodide (o crear un Worker nuevo) en cada ejecución | **≈ 2 000–2 400 ms** (`loadPyodide`) | Total dentro del Worker | Descartada: un ejercicio con 4 casos tardaría unos 10 s |
| Sin aislamiento (antes) | ≈ 0,2 ms | Solo funciones integradas | Es el problema |
| Copiar en cada ejecución todos los módulos, clases y funciones | ≈ 27 ms (≈ 12 ms en copiar unas 4 300 funciones y 725 clases) | Alto | Descartada por coste |
| **Restaurar el estado, con un registro de funciones por auditoría** | **≈ 8 ms** (foto ≈ 4 ms, restaurar ≈ 3 ms, carpeta temporal ≈ 2 ms) | Alto para errores accidentales | **Elegida** |
| Instantáneas de memoria de Pyodide (`makeMemorySnapshot`) | No medida | Total | API experimental, pensada para el arranque; se puede revisar en el futuro |

Corregir un ejercicio ejecuta dos veces por caso (el código y sus tests), así que cuesta unos 16 ms
por caso. El tope de 10 s por ejecución y la sensación de inmediatez (< 100 ms) quedan muy lejos.

## 3. Cómo funciona

`run_code` y `check_exercise` usan dos piezas:

- **`_working_directory()`**: cada ejecución trabaja en una carpeta temporal vacía (`/tmp/pld-…`) que
  se borra al terminar. Los tests de un caso usan la misma carpeta que su código, para poder comprobar
  los archivos que crea. Como en Pyodide `sys.path` empieza por `''` (la carpeta actual), esto también
  evita que un `random.py` del alumno tape al módulo de verdad en el ejercicio siguiente.
- **`_isolated(name)`**: antes de ejecutar hace una foto (`_snapshot`) y al terminar la restaura
  (`_restore`), también si hay error, `exit()`, `KeyboardInterrupt` o `RecursionError`.

Qué guarda la foto y cómo se restaura:

| Qué | Cómo |
|---|---|
| Funciones integradas | Copia hecha al cargar el runner (`_PRISTINE_BUILTINS`). Se restauran **lo primero**, con código que no usa ninguna, porque salir de los `with` las necesita |
| Atributos de cada módulo cargado (`math.sqrt`, `json.loads`…) | Copia del `__dict__` de los ~190 módulos (≈ 0,2 ms) |
| `sys` (`sys.path`, `sys.modules`, `sys.excepthook`…) | Copia de su `__dict__`, salvo `stdin`, `stdout` y `stderr`, que gestiona `_execute` |
| Contenido de `sys.path`, `sys.meta_path`, `sys.path_hooks`, `sys.argv` y `sys.path_importer_cache` | Copia de la lista o del diccionario; se restaura el contenido en el mismo objeto |
| `sys.modules` | Vuelven los módulos sustituidos o borrados; los importados por primera vez se **descartan**, y el siguiente programa los importa limpios |
| Clases de la biblioteca estándar (`json.JSONEncoder`…) | Copia del `__dict__` de cada clase de módulos de `sys.stdlib_module_names`. `type.__setattr__` no avisa a los hooks de auditoría, así que no hay forma más barata de detectar cambios |
| `__code__`, `__defaults__` y `__kwdefaults__` de funciones de la biblioteca | Un hook de auditoría (`_FunctionJournal`) anota el valor anterior justo antes de cada cambio. Así no hay que copiar 4 000 funciones en cada ejecución |
| Límite de recursión, `set_int_max_str_digits`, `settrace`, `setprofile`, `gc.enable` | Se leen antes y se vuelven a poner |
| Carpeta actual y `os.environ` | Se leen antes y se vuelven a poner |
| Filtros de `warnings` | `warnings.catch_warnings()` |
| Estado de `random` y contexto de `decimal` | `getstate()`/`setstate()` y `getcontext().copy()`/`setcontext()` |

Las comparaciones son por identidad (`is`, `operator.is_` en C), así que restaurar no llama al `__eq__`
de ningún objeto del alumno. Lo que se retira se guarda en una lista y se suelta al final: si un objeto
del alumno tiene `__del__`, se ejecuta cuando todo ya está restaurado.

**Lo que conserva sus cambios.** Las clases y funciones que define el alumno (módulo `__main__` en la
consola, `solucion` al corregir) no se restauran: si el ejercicio hace `Contador.total = 5`, sus tests
tienen que verlo. En cambio, los tests se ejecutan con la biblioteca estándar ya restaurada: un código
que cambie `math.sqrt` no puede engañar a un test que use `math.sqrt`.

**Cuando no se puede restaurar.** Si algo falla al restaurar (por ejemplo, el programa borró su propia
carpeta de trabajo), `runner.py` devuelve `"restart": true` y `python-runner.js` destruye el Worker: la
siguiente ejecución carga un Python limpio (unos 2 s, solo esa vez).

**`sys.addaudithook`.** Un hook de auditoría no se puede quitar una vez puesto: durante la ejecución
del alumno, `sys.addaudithook` lanza `RuntimeError`.

## 4. Lo que no cubre

Son límites conocidos. Ninguno aparece en los ejercicios actuales del temario (no hay lecciones con
`logging`, `atexit`, hilos ni rutas absolutas).

- **Contenido mutable dentro de objetos de módulos.** Se restauran los atributos de los módulos, no lo
  que hay dentro de sus objetos. Por ejemplo, `logging.basicConfig()` añade un manejador a
  `logging.root.handlers` que sigue ahí en la ejecución siguiente; `abc.ABC.register()`,
  `codecs.register()`, `copyreg`, `atexit.register()` y `gc.callbacks` tampoco se deshacen.
- **Clases que no están a nivel de módulo** (anidadas o creadas por una función) y clases de módulos
  que no son de la biblioteca estándar (los internos de Pyodide, `_pyodide`, `js`).
- **Atributos propios de funciones** (`json.dumps.algo = 1`, el `__dict__` de la función). Sí se
  restauran `__code__`, `__defaults__` y `__kwdefaults__`.
- **Archivos fuera de la carpeta de trabajo.** Lo que se escriba con rutas absolutas (`/tmp/x`,
  `/home/pyodide/x`) o se borre de la biblioteca estándar (`/lib/python3.14/…`) sigue así hasta recargar.
- **Estado en C o del propio Pyodide**: `sys.monitoring`, el módulo `js` y `pyodide.ffi` (desde el que
  se puede llegar a los objetos del Worker; la red ya está cerrada por `closeNetwork()`), memoria
  agotada o un intérprete corrompido a propósito.
- **Código escrito para saltarse el aislamiento**: con `gc.get_objects()` un programa puede encontrar
  la foto y cambiarla, o recuperar el `sys.addaudithook` real. No se intenta impedir.
- **Hilos y procesos**: Pyodide no los admite, así que no se tratan. En CPython (las pruebas) un hilo
  del alumno podría seguir cambiando cosas después de restaurar.
- **Bucles infinitos**: no son cosa del aislamiento; los corta el tope de tiempo de `python-runner.js`
  (10 s) o el botón «Detener», que destruyen el Worker.

Si alguno de estos casos empieza a importar (por ejemplo, una lección de `logging`), se añade a la
foto con su prueba, o la página reinicia el Worker después de esa lección.

## 5. Pruebas

| Archivo | Qué prueba |
|---|---|
| `backend/tests/test_runner_isolation.py` | En CPython con el `runner.py` real: módulos, atributos borrados y añadidos, módulos nuevos, clases y funciones de la biblioteca, clases y funciones del alumno (conservan sus cambios), tests que no se dejan engañar, `sys.path`, `sys.meta_path`, `sys.modules`, archivos, carpeta y entorno, restauración tras errores, `exit()` y `RecursionError`, `warnings`, `decimal`, dígitos, `gc`, `random`, traza, hooks de auditoría, 25 ejecuciones seguidas y el aviso `restart` |
| `tests/unit/runner-isolation-pyodide.test.mjs` | Lo mismo con el Pyodide real en Node, y que aislar una ejecución cuesta milisegundos |
| `tests/unit/python-runner.test.mjs` | Con `restart`, `PythonRunner` destruye el Worker y la siguiente ejecución crea otro |
| `e2e/console.spec.js` | En Chromium: `math.sqrt`, `sys.path` y un archivo de un ejercicio no llegan al siguiente |

Las pruebas nuevas fallan con el `runner.py` anterior (18 de 29 en CPython y las 6 de Pyodide).
