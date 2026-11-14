/* Contenido propio del itinerario DevOps. Las lecciones se mantienen como módulos ES para
   que el catálogo pueda cargarse sin un generador de JSON ni modificar datos generados de DAW. */
export const DEVOPS_COURSE = {
  title: "Academia DevOps",
  subtitle: "Linux · Docker · GitHub · Python",
  duration: "9 meses · 20 horas por semana",
  weeks: [
    {
      id: "semana-1",
      title: "Semana 1 · Fundamentos",
      lessons: [
        {
          slug: "linux-terminal",
          title: "Linux: terminal y sistema de archivos",
          area: "Linux",
          minutes: 45,
          theory: `## La shell y el sistema de archivos

La terminal permite dar instrucciones al sistema mediante una shell. En Ubuntu, la shell habitual es Bash. Cada comando se ejecuta con los permisos del usuario actual.

La ruta **absoluta** empieza en \`/\`; la **relativa** depende del directorio actual. Los directorios habituales incluyen \`/home\` para usuarios, \`/etc\` para configuración, \`/var/log\` para registros y \`/tmp\` para archivos temporales.

Comandos iniciales:

- \`pwd\`: muestra el directorio actual.
- \`ls -la\`: lista también archivos ocultos y permisos.
- \`cd\`: cambia de directorio.
- \`mkdir -p\`: crea directorios.
- \`cp\`, \`mv\`, \`rm\`: copia, mueve y elimina.
- \`cat\`, \`less\`, \`head\`, \`tail\`: consultan archivos.
- \`man comando\`: abre el manual.`,
          example: `pwd
ls -la
mkdir -p ~/laboratorio/linux
cd ~/laboratorio/linux
printf "Academia DevOps\\n" > README.txt
cat README.txt
`,
          task: "Crea la carpeta ~/laboratorio/linux, guarda dentro un archivo entorno.txt con el nombre de tu distribución y consulta su contenido con cat. Comprueba la ruta con pwd.",
          deliverable: "Captura o transcripción de pwd, ls -la y cat entorno.txt.",
          quiz: [
            { q: "¿Qué representa la ruta /etc?", options: ["Archivos de configuración del sistema", "Carpetas personales", "Archivos temporales"], answer: 0, explain: "/etc contiene configuración del sistema y de muchos servicios." },
            { q: "¿Qué comando muestra el directorio actual?", options: ["where", "pwd", "who"], answer: 1, explain: "pwd significa print working directory." },
            { q: "¿Qué diferencia una ruta absoluta?", options: ["Empieza en /", "Siempre empieza en ~", "Solo funciona como root"], answer: 0, explain: "Una ruta absoluta parte de la raíz del sistema de archivos." }
          ],
          sources: [{ title: "Ubuntu Server documentation", url: "https://ubuntu.com/server/docs" }, { title: "GNU Bash manual", url: "https://www.gnu.org/software/bash/manual/" }]
        },
        {
          slug: "git-primer-repositorio",
          title: "Git y GitHub: primer repositorio",
          area: "GitHub",
          minutes: 45,
          theory: `## Git frente a GitHub

Git es un sistema distribuido de control de versiones. Guarda instantáneas del proyecto mediante commits. GitHub aloja repositorios Git y añade colaboración, incidencias y revisión de cambios.

Flujo básico:

1. \`git init\` crea un repositorio local.
2. \`git status\` muestra los cambios.
3. \`git add\` prepara los archivos.
4. \`git commit\` guarda una instantánea.
5. \`git remote add origin\` registra el repositorio remoto.
6. \`git push\` publica los commits.

Configura tu identidad con \`git config --global user.name\` y \`git config --global user.email\`. No guardes contraseñas, tokens ni claves en el repositorio.`,
          example: `mkdir sysmonitor
cd sysmonitor
git init
printf "# SysMonitor\\n" > README.md
git status
git add README.md
git commit -m "docs: add project readme"
git log --oneline
`,
          task: "Crea un repositorio local llamado sysmonitor, añade un README con el objetivo del proyecto y realiza un commit. Después crea un repositorio vacío en GitHub y conéctalo como origin.",
          deliverable: "URL del repositorio, salida de git log --oneline y primer commit.",
          quiz: [
            { q: "¿Qué guarda un commit?", options: ["Una instantánea versionada del proyecto", "Una copia de seguridad automática del disco", "Una contraseña del repositorio"], answer: 0, explain: "Un commit registra cambios versionados con autor, fecha y mensaje." },
            { q: "¿Para qué sirve git add?", options: ["Publicar en GitHub", "Preparar cambios para el siguiente commit", "Crear una rama remota"], answer: 1, explain: "git add mueve cambios al área de preparación (staging)." },
            { q: "¿Dónde se debe guardar un token de acceso?", options: ["En README.md", "En el código fuente", "En un gestor de secretos o almacén seguro"], answer: 2, explain: "Los tokens son secretos: no deben incluirse en el repositorio." }
          ],
          sources: [{ title: "Pro Git, edición en español", url: "https://git-scm.com/book/es/v2" }, { title: "GitHub Docs", url: "https://docs.github.com/es" }]
        }
      ]
    },
    {
      id: "semana-2",
      title: "Semana 2 · Administración y contenedores",
      lessons: [
        {
          slug: "linux-permisos-procesos",
          title: "Linux: permisos, usuarios y procesos",
          area: "Linux",
          minutes: 50,
          theory: `## Usuarios, permisos y procesos

Linux identifica usuarios y grupos mediante UID y GID. Cada archivo tiene propietario, grupo y permisos para propietario, grupo y otros.

Los permisos básicos son lectura (\`r\`), escritura (\`w\`) y ejecución (\`x\`). \`chmod\` modifica permisos; \`chown\` cambia propietario y grupo. Evita recurrir a \`chmod 777\`: concede permisos innecesarios.

Un proceso es un programa en ejecución. \`ps aux\` lista procesos, \`top\` permite observarlos y \`kill\` envía señales. Para servicios gestionados por systemd se utilizan \`systemctl\` y \`journalctl\`.`,
          example: `id
ls -l
chmod 640 archivo.txt
ps aux | head
systemctl status ssh
journalctl -u ssh --since today
`,
          task: "Crea un archivo privado para tu usuario, deja lectura y escritura solo al propietario y consulta sus permisos. Identifica un proceso y explica su PID.",
          deliverable: "Permisos antes y después de chmod 600 y una línea de ps con PID y comando.",
          quiz: [
            { q: "¿Qué permiso permite ejecutar un archivo?", options: ["r", "w", "x"], answer: 2, explain: "x representa ejecución o acceso a un directorio." },
            { q: "¿Qué comando cambia el propietario?", options: ["chown", "chmod", "chgrpall"], answer: 0, explain: "chown cambia el propietario y opcionalmente el grupo." },
            { q: "¿Qué identifica un PID?", options: ["Un paquete instalado", "Un proceso", "Un usuario"], answer: 1, explain: "PID es el identificador de proceso." }
          ],
          sources: [{ title: "Ubuntu Server documentation", url: "https://ubuntu.com/server/docs" }]
        },
        {
          slug: "docker-contenedores",
          title: "Docker: imágenes y contenedores",
          area: "Docker",
          minutes: 50,
          theory: `## Imagen y contenedor

Una imagen es una plantilla inmutable por capas. Un contenedor es una instancia ejecutable de esa imagen con su propio aislamiento de procesos, red y sistema de archivos.

Docker utiliza una arquitectura cliente-servidor: el cliente \`docker\` envía instrucciones al daemon. Los contenedores comparten el kernel del anfitrión; no son máquinas virtuales completas.

Comandos de ciclo de vida:

- \`docker pull\`: descarga una imagen.
- \`docker run\`: crea y arranca un contenedor.
- \`docker ps -a\`: lista contenedores.
- \`docker logs\`: consulta su salida.
- \`docker exec\`: ejecuta un proceso dentro.
- \`docker stop\` y \`docker rm\`: detiene y elimina.`,
          example: `docker pull nginx:alpine
docker run -d --name web-lab -p 8080:80 nginx:alpine
docker ps
docker logs web-lab
docker exec web-lab nginx -v
docker stop web-lab
docker rm web-lab
`,
          task: "Ejecuta nginx:alpine publicando el puerto 8080 del anfitrión. Comprueba el estado, consulta los logs y elimina el contenedor al terminar.",
          deliverable: "Comandos utilizados y resultado de docker ps -a. No publiques servicios en Internet.",
          quiz: [
            { q: "¿Qué es una imagen Docker?", options: ["Una plantilla para crear contenedores", "Una máquina virtual encendida", "Un volumen de datos"], answer: 0, explain: "La imagen contiene capas y metadatos necesarios para crear contenedores." },
            { q: "¿Qué opción publica un puerto?", options: ["-v", "-p", "--rm"], answer: 1, explain: "-p relaciona un puerto del anfitrión con uno del contenedor." },
            { q: "¿Los contenedores incluyen siempre su propio kernel?", options: ["Sí", "No, comparten el kernel del anfitrión", "Solo en Linux"], answer: 1, explain: "Los contenedores aíslan procesos, pero comparten el kernel del host." }
          ],
          sources: [{ title: "Docker documentation", url: "https://docs.docker.com/get-started/" }]
        }
      ]
    },
    {
      id: "semana-3",
      title: "Semana 3 · Redes, ramas e imágenes",
      lessons: [
        {
          slug: "linux-redes-ssh",
          title: "Linux: red y acceso SSH",
          area: "Linux",
          minutes: 50,
          theory: `## Diagnóstico de red y SSH

Para diagnosticar conectividad conviene avanzar por capas: interfaz, dirección IP, ruta, resolución DNS y servicio remoto.

- \`ip addr\` muestra interfaces y direcciones.
- \`ip route\` muestra rutas.
- \`ss -tulpn\` lista sockets y puertos en escucha.
- \`ping\` comprueba conectividad IP cuando ICMP está permitido.
- \`getent hosts\` consulta la resolución de nombres.
- \`curl -I\` consulta cabeceras HTTP.

SSH permite administrar equipos de forma cifrada. Es preferible usar claves, proteger la clave privada y limitar el acceso remoto. No desactives la autenticación por contraseña hasta comprobar que el acceso por clave funciona.`,
          example: `ip addr
ip route
ss -tulpn
getent hosts ubuntu.com
curl -I https://ubuntu.com
ssh-keygen -t ed25519
`,
          task: "Registra la IP de tu VM, la ruta por defecto, un puerto en escucha y la resolución DNS de un dominio. Genera un par de claves SSH para prácticas locales.",
          deliverable: "Informe de diagnóstico con comandos y resultados; no compartas tu clave privada.",
          quiz: [
            { q: "¿Qué comando lista sockets en escucha?", options: ["ss -tulpn", "chmod -R", "git status"], answer: 0, explain: "ss permite inspeccionar sockets; -l filtra los que escuchan." },
            { q: "¿Qué archivo debe mantenerse privado?", options: ["La clave SSH privada", "La clave pública", "El README"], answer: 0, explain: "La clave privada nunca debe compartirse ni subirse al repositorio." },
            { q: "¿Qué comprueba getent hosts?", options: ["Permisos", "Resolución de nombres", "Espacio en disco"], answer: 1, explain: "getent consulta bases de datos del sistema, incluida la resolución de hosts." }
          ],
          sources: [{ title: "Ubuntu Server documentation", url: "https://ubuntu.com/server/docs" }, { title: "OpenSSH manual", url: "https://www.openssh.com/manual.html" }]
        },
        {
          slug: "github-ramas-pr",
          title: "GitHub: ramas y Pull Requests",
          area: "GitHub",
          minutes: 45,
          theory: `## Trabajar con ramas

Una rama permite desarrollar cambios sin modificar directamente la línea principal. En Git moderno, \`git switch -c\` crea y activa una rama.

Un Pull Request propone integrar cambios. Facilita revisar el diff, comentar, ejecutar CI y decidir si el cambio cumple los requisitos.

Flujo habitual:

1. Actualiza la rama principal.
2. Crea una rama corta con un propósito concreto.
3. Realiza commits pequeños.
4. Publica la rama.
5. Abre un Pull Request y revisa las comprobaciones.
6. Integra el cambio según las reglas del repositorio.`,
          example: `git switch -c feature/add-healthcheck
printf "\\nHealth checks are planned.\\n" >> README.md
git add README.md
git commit -m "docs: describe health checks"
git push -u origin feature/add-healthcheck
`,
          task: "Crea una rama feature/ para un cambio documental, realiza un commit y abre un Pull Request. Revisa el diff antes de solicitar integración.",
          deliverable: "URL del Pull Request y descripción breve del cambio.",
          quiz: [
            { q: "¿Qué ventaja tiene trabajar en una rama?", options: ["Aísla el trabajo del resto de cambios", "Evita hacer commits", "Desactiva los tests"], answer: 0, explain: "Las ramas separan líneas de trabajo hasta que se decide integrarlas." },
            { q: "¿Qué permite revisar un Pull Request?", options: ["Solo el tamaño del repositorio", "Los cambios propuestos y sus comprobaciones", "Las contraseñas del equipo"], answer: 1, explain: "El PR muestra el diff, comentarios y resultados de CI." },
            { q: "¿Qué conviene hacer antes de integrar?", options: ["Ignorar CI", "Revisar diff y checks", "Borrar el historial"], answer: 1, explain: "La revisión y las comprobaciones ayudan a detectar errores antes del merge." }
          ],
          sources: [{ title: "GitHub: About pull requests", url: "https://docs.github.com/es/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests" }]
        }
      ]
    },
    {
      id: "semana-4",
      title: "Semana 4 · Python e integración",
      lessons: [
        {
          slug: "docker-dockerfile-volumenes",
          title: "Docker: Dockerfile y persistencia",
          area: "Docker",
          minutes: 55,
          theory: `## Construir imágenes propias

Un Dockerfile describe cómo construir una imagen. \`FROM\` elige la imagen base, \`WORKDIR\` define el directorio de trabajo, \`COPY\` incorpora archivos, \`RUN\` ejecuta pasos de construcción y \`CMD\` define el proceso por defecto.

Cada instrucción puede crear una capa. Conviene ordenar los pasos para aprovechar la caché y copiar primero los archivos de dependencias cuando sea posible.

Los contenedores son efímeros por diseño. Para conservar datos entre recreaciones se usan volúmenes o montajes bind. No guardes datos importantes solo en la capa escribible del contenedor.`,
          example: `FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "-c", "print('Hello from the container')"]
`,
          task: "Crea una imagen para una aplicación Python mínima. Añade .dockerignore y prueba a recrear el contenedor. Si la aplicación escribe datos que deben persistir, monta un volumen.",
          deliverable: "Dockerfile, .dockerignore y comandos de build/run. No incluyas secretos en la imagen.",
          quiz: [
            { q: "¿Qué instrucción define la imagen base?", options: ["FROM", "COPY", "CMD"], answer: 0, explain: "FROM inicia una etapa de construcción y define su imagen base." },
            { q: "¿Qué mecanismo conserva datos fuera del ciclo de vida del contenedor?", options: ["La capa temporal", "Un volumen", "El nombre del contenedor"], answer: 1, explain: "Los volúmenes desacoplan los datos persistentes del contenedor." },
            { q: "¿Qué hace CMD?", options: ["Define el comando por defecto al iniciar", "Publica la imagen", "Crea un usuario en GitHub"], answer: 0, explain: "CMD define el comando o argumentos por defecto del contenedor." }
          ],
          sources: [{ title: "Dockerfile reference", url: "https://docs.docker.com/reference/dockerfile/" }, { title: "Docker volumes", url: "https://docs.docker.com/engine/storage/volumes/" }]
        },
        {
          slug: "python-sysmonitor",
          title: "Python: automatización y SysMonitor",
          area: "Python",
          minutes: 60,
          theory: `## Python para tareas de operación

Python puede automatizar tareas repetibles. Para herramientas de terminal, \`argparse\` permite definir argumentos; \`pathlib\` facilita trabajar con rutas; \`logging\` registra eventos con niveles; y \`subprocess\` ejecuta programas externos.

Valida las entradas y evita construir comandos de shell concatenando texto proporcionado por el usuario. Siempre que sea posible, pasa los argumentos como una lista a \`subprocess.run\` y deja \`shell=False\`.

Los scripts de operaciones deben devolver códigos de salida útiles, registrar errores y no imprimir secretos.`,
          example: `from pathlib import Path
import argparse
import logging
import platform
import shutil

parser = argparse.ArgumentParser(description="Resumen básico del sistema")
parser.add_argument("--output", default="sysmonitor-report")
args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
disk = shutil.disk_usage(Path.home())
report = (
    f"Sistema: {platform.system()} {platform.release()}\\n"
    f"Espacio libre: {disk.free // (1024 ** 3)} GiB\\n"
)
Path(args.output).write_text(report, encoding="utf-8")
logging.info("Informe guardado en %s", args.output)
`,
          task: "Amplía SysMonitor para aceptar --output y generar un informe con sistema operativo y espacio libre. Añade al menos dos pruebas unitarias y un README con instrucciones.",
          deliverable: "Repositorio SysMonitor con código, pruebas, README y Dockerfile. Este será el proyecto integrador del primer mes.",
          quiz: [
            { q: "¿Qué módulo ayuda a crear argumentos de línea de comandos?", options: ["argparse", "pickle", "turtle"], answer: 0, explain: "argparse permite definir y validar argumentos de CLI." },
            { q: "¿Qué opción es más segura al ejecutar un comando externo?", options: ["Concatenar entrada en shell=True", "Pasar una lista de argumentos y shell=False", "Ejecutar siempre como root"], answer: 1, explain: "Una lista de argumentos evita que la shell interprete metacaracteres de la entrada." },
            { q: "¿Qué nivel de logging suele indicar un fallo?", options: ["DEBUG", "INFO", "ERROR"], answer: 2, explain: "ERROR se utiliza para registrar errores que afectan a una operación." }
          ],
          sources: [{ title: "Python argparse", url: "https://docs.python.org/es/3/library/argparse.html" }, { title: "Python subprocess", url: "https://docs.python.org/es/3/library/subprocess.html" }, { title: "Python logging", url: "https://docs.python.org/es/3/library/logging.html" }]
        }
      ]
    }
  ]
};
