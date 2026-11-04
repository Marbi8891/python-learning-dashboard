# Cómo contribuir

Gracias por querer mejorar el Python Learning Dashboard. Es el proyecto de 2º de DAW de su autor,
así que cualquier cambio lo revisa y lo fusiona él.

## Antes de empezar

- Para un fallo o una idea, abre un [issue](../../issues/new/choose) con la plantilla que corresponda.
- Para una vulnerabilidad, **no abras un issue**: sigue [SECURITY.md](SECURITY.md).
- Para un cambio grande, abre antes un issue y espera a que se acuerde el enfoque.
- Sigue el [código de conducta](CODE_OF_CONDUCT.md).

## Preparar el entorno

Necesitas Python 3.11 o superior y Node 22. Los pasos están en [docs/TESTING.md](docs/TESTING.md#preparar-el-entorno)
y, para arrancar la web y la API, en el [README](README.md#desarrollo).

## Flujo de trabajo

1. Crea una rama desde `main` con el formato `tipo/descripcion`, por ejemplo `fix/consola-input` o
   `docs/indice`. Nunca trabajes directamente en `main`.
2. Haz cambios pequeños y de un solo tema. Revisa `git diff` antes de cada commit.
3. Pasa las pruebas que tocan a tu cambio (tabla «Qué ejecutar según lo que cambies» de
   [docs/TESTING.md](docs/TESTING.md)).
4. Abre un pull request contra `main` y rellena la plantilla.
5. La CI tiene que estar en verde. **Hacer merge a `main` publica la web**, así que el merge lo hace
   siempre el autor.

### Tipos de rama y de commit

| Tipo | Para |
|---|---|
| `feat` | Una funcionalidad nueva |
| `fix` | Corregir un fallo |
| `docs` | Solo documentación |
| `test` | Solo pruebas |
| `refactor` | Cambiar código sin cambiar lo que hace |
| `chore` | Dependencias, CI y configuración |

Los mensajes de commit van en español y en imperativo, con el tipo delante cuando ayude:
`fix(consola): cortar el programa al pulsar Detener`.

## Reglas del proyecto

- **Contenido generado:** nadie edita a mano un JSON de `frontend/data/`. Se cambia su script en
  `scripts/` y se regenera; la CI comprueba que esté al día con `--check`.
- **Pruebas:** un cambio no está terminado hasta que pasan sus pruebas. Está prohibido saltar o
  debilitar un test para que pase. El backend mantiene una cobertura del 100 %.
- **Estilo:** Python con Ruff (`ruff check` y `ruff format`), y para todo lo demás lo que dice
  `.editorconfig` (UTF-8, LF y 2 espacios; 4 en Python).
- **Secretos:** no subas `.env`, claves ni tokens. Las variables están en `backend/.env.example`.
- **Servicios:** solo herramientas y servicios gratuitos.
- **Accesibilidad:** la web apunta a WCAG 2.2 AA. Un cambio de HTML o CSS tiene que pasar `npm run test:e2e`,
  que incluye axe-core.
- **Documentación:** si cambias cómo funciona algo, actualiza su documento (índice en
  [docs/README.md](docs/README.md)) y añade una línea en «Sin publicar» del [CHANGELOG](CHANGELOG.md).

## Contenido educativo

Cada respuesta del temario se comprueba ejecutando su código. Si añades una pregunta o una lección,
hazlo en el script del curso y ejecuta el `--check` correspondiente. Cómo añadir asignaturas y
recursos: [docs/AMPLIAR-TEMARIO-DAW.md](docs/AMPLIAR-TEMARIO-DAW.md). Los recursos externos llevan
autor, licencia y fecha de verificación.

## Licencia

Al contribuir aceptas que tu aportación se publique con la [licencia MIT](LICENSE) del proyecto.
