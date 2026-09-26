# Ejecutar el dashboard en tu PC con Windows

Versión de escritorio: un solo programa sirve la web y la API **solo para tu ordenador** (`127.0.0.1`). No necesita Docker, ni GitHub, ni servidor.

Probado para: Windows 10/11 de 64 bits con Python 3.11 o superior. Recursos: menos de 300 MB de RAM.

## 1. Requisito: Python 3.11 o superior

Si ya usas PyCharm con Python 3.11+, sáltate este paso. Para comprobarlo, abre PowerShell y escribe:

```powershell
py --version
```

Si no lo tienes:

```powershell
winget install --id Python.Python.3.12
```

## 2. Abrirlo

1. Antes de descomprimir el zip: clic derecho → **Propiedades** → marca **Desbloquear** (si aparece) → **Aceptar**. Así Windows no marca cada archivo como «descargado de Internet».
2. Descomprime, por ejemplo en `C:\Users\PC\Projects\python-learning-dashboard`.
3. Doble clic en **`Iniciar-Dashboard.bat`**.
   - La primera vez crea el entorno e instala las dependencias (1-2 minutos).
   - Se abre el navegador en `http://127.0.0.1:8000`.
4. Para cerrarlo: cierra la ventana negra o pulsa `Ctrl+C` en ella.

Tus datos (cuenta, progreso y ejercicios) se guardan en `backend\local.db`. Para empezar de cero, borra `backend\local.db` y `backend\.local-secret`.

> La consola de Python descarga Pyodide (unos 10 MB) de Internet la primera vez. Después queda en la caché del navegador.

### Acceso directo en el escritorio

Clic derecho en `Iniciar-Dashboard.bat` → **Mostrar más opciones** → **Enviar a** → **Escritorio (crear acceso directo)**.

### Desde PyCharm

**File → Open** → la carpeta del proyecto. Después:

- **Intérprete:** en **Settings → Project → Python Interpreter → Add Interpreter → Add Local Interpreter → Select existing**, elige `.venv-local\Scripts\python.exe`. Esa carpeta la crea el `.bat` la primera vez.
- **Ejecutar:** clic derecho en `scripts/run_local.py` → **Run**.

## 3. Si algo falla

| Síntoma | Causa probable | Solución |
|---|---|---|
| «No se ha encontrado Python 3.11 o superior» | Python no instalado, o solo el acceso directo de Microsoft Store | `winget install --id Python.Python.3.12` y vuelve a abrir el `.bat` |
| «Windows protegió su PC» al abrir el `.bat` | SmartScreen: archivo descargado de Internet | **Más información → Ejecutar de todas formas**, o desbloquea el zip (paso 2.1) |
| Error que menciona «directiva de Control de aplicaciones», «Application Control policy» o «bloqueado por el administrador» | Tu equipo tiene la directiva de control de aplicaciones **impuesta** (Smart App Control o una directiva de empresa) y ha bloqueado un archivo sin firma, normalmente una librería instalada con `pip` | Mira la sección siguiente |
| La web se abre pero la consola dice «No se pudo cargar Python» | Sin Internet la primera vez, o un proxy o antivirus bloquea `cdn.jsdelivr.net` | Conéctate y recarga la página |
| Se abre en `:8001` u otro puerto | El 8000 estaba ocupado | Normal: el lanzador busca un puerto libre |

### Control de aplicaciones de Windows (NEEDS_HUMAN)

En «Información del sistema», la línea «Directiva de Control de aplicaciones: **Impuesta**» indica que Windows puede bloquear programas y librerías sin firma digital. Python (python.org) está firmado. Algunas librerías que instala `pip`, como `argon2-cffi` o `pydantic-core`, incluyen archivos compilados que podrían no estarlo.

- Si **no** ves ningún error de bloqueo, no hay que hacer nada.
- Si es **Smart App Control** (Seguridad de Windows → Control de aplicaciones y navegador): **no lo desactives a la ligera**. En Windows 11, una vez desactivado no se puede volver a activar sin reinstalar el sistema. Alternativas: ejecutar la app con Docker, o usar la versión web en GitHub Pages, que no instala nada en el PC.
- Si es una **directiva de empresa o del centro**, pide al administrador que permita Python y las librerías del proyecto.
