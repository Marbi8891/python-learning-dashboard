# Sistema visual

Guía del diseño de la web. Los valores están en **`frontend/css/tokens.css`**, la primera hoja que se carga. Ninguna otra hoja debe definir colores, tamaños ni radios nuevos: se usan las variables de aquí. Si falta alguna, se añade aquí.

## Principios

1. **El contenido manda.** Primero el texto, el código y el ejercicio. Sin degradados de fondo, brillos, cristal ni animaciones decorativas. La jerarquía la dan la tipografía y el espacio antes que las cajas.
2. **Un color, un significado.** El ámbar es para la acción principal, los enlaces y el foco. El verde, para el progreso y los aciertos. El rojo, para los errores. El color nunca va solo: siempre lo acompaña un texto o un icono (✓, ✗).
3. **Datos reales.** No se muestran cifras que la web no pueda calcular: ni horas, ni porcentajes inventados, ni estadísticas de usuarios.
4. **Accesible por defecto.** Contraste AA, foco visible, objetivos táctiles de 44 px y respeto por `prefers-reduced-motion`.

## Identidad

- **Grafito y ámbar Python.** El fondo oscuro es un grafito (`#101318`), no negro, con superficies un punto más claras. El acento es un ámbar cálido que recuerda a Python y no se confunde con el verde de acierto ni con el rojo de error.
- **Texto sobre el ámbar siempre oscuro** (`--color-on-primary`), en los dos temas: los botones principales son ámbar con texto casi negro.
- **El tema claro no es una inversión.** Es un papel cálido (`#f4f5f7`) con superficies blancas. El ámbar claro solo se usa de fondo de botón; para texto, enlaces y marcas se usa un ámbar oscuro (`#8c5708`) que llega a AA. El código sigue en oscuro en los dos temas.

## Color

Hay dos temas. El claro y el oscuro se eligen en «Aspecto» o siguen al sistema (`theme-init.js` pone `data-theme` en `<html>`).

| Token | Uso | Oscuro | Claro |
|---|---|---|---|
| `--color-bg` | Fondo de la página | `#121417` | `#f6f4ef` |
| `--color-surface` | Tarjetas y paneles | `#171c23` | `#ffffff` |
| `--color-surface-2` | Superficie secundaria | `#1d242d` | `#f7f8fa` |
| `--color-border` | Separadores (decorativo) | `#2b3440` | `#e5e8ed` |
| `--color-border-control` | Borde de campos y botones secundarios | `#697586` | `#aeb6c2` |
| `--color-text` | Texto | `#e8edf4` | `#202631` |
| `--color-text-muted` | Texto secundario | `#a8b2c0` | `#626d7b` |
| `--color-primary` | Enlaces destacados, marcas, foco | `#f2b443` | `#8a5300` |
| `--color-primary-strong` | Fondo del botón principal | `#f2b443` | `#f3b84e` |
| `--color-on-primary` | Texto sobre el botón principal | `#1b1405` | `#1b1405` |
| `--color-link` | Enlaces | `#f4c46d` | `#8a5300` |
| `--color-accent` | Progreso, aciertos | `#3ccb72` | `#166534` |
| `--color-danger` | Errores | `#f87171` | `#b91c1c` |
| `--color-code-bg` | Fondo del código (oscuro en los dos temas) | `#0e1013` | `#16181c` |

Contrastes calculados (WCAG 2.x, sobre `--color-surface` salvo que se indique otra cosa):

| Par | Oscuro | Claro | Mínimo AA |
|---|---|---|---|
| Texto | 14,0:1 | 16,7:1 | 4,5:1 |
| Texto secundario | 7,5:1 | 6,7:1 | 4,5:1 |
| Texto tenue sobre `surface-2` | 5,7:1 | 5,7:1 | 4,5:1 |
| Enlace | 10,8:1 | 6,3:1 | 4,5:1 |
| Texto del botón principal | 9,9:1 | 8,5:1 | 4,5:1 |
| Verde de progreso | 8,2:1 | 7,1:1 | 3:1 (gráficos) |
| Rojo de error | 6,2:1 | 6,5:1 | 4,5:1 |
| Borde de controles (peor caso: fondo, superficie o `surface-2`) | 3,2:1 | 3,0:1 | 3:1 (WCAG 1.4.11) |
| Borde decorativo | 1,4:1 | 1,4:1 | No aplica: no es el único límite de un control |

Los campos de formulario, el editor y los botones secundarios usan `--color-border-control` (corrige AUD-035). `--color-border` queda para separar tarjetas y secciones.

## Tipografía

| Familia | Token | Uso |
|---|---|---|
| Inter | `--font-sans` | Todo el texto |
| Fraunces | `--font-display` | Titulares de la portada y de los cursos |
| JetBrains Mono | `--font-mono` | Código, editor y salida |

Las fuentes están en `frontend/fonts/` (sin peticiones a terceros) y con sus licencias.

**Escala de tamaños** (en `rem`, para que respete el tamaño de letra del navegador):

| Token | Tamaño | Uso |
|---|---|---|
| `--text-xs` | 12 px | Etiquetas, contadores |
| `--text-sm` | 14 px | Menús, texto secundario |
| `--text-md` | 16 px | Texto de estudio |
| `--text-lg` | 18 px | Entradillas |
| `--text-xl` | 22 px | Títulos de sección |
| `--text-2xl` | 28 px | Títulos de página |
| `--text-3xl` | 30-42 px | Portada |

Interlineado: `--leading-body` (1,6) para leer y `--leading-tight` (1,2) para títulos. El alumno puede agrandar el área de estudio (`--ui-zoom`: 1; 1,12; 1,25).

> Las hojas antiguas usan todavía unos 60 tamaños en `px` distintos. Se pasan a esta escala al rediseñar cada zona; no se cambian todos de golpe para poder revisar cada pantalla.

## Espaciado, bordes y sombras

- **Espaciado:** múltiplos de 4 px, de `--space-1` (4 px) a `--space-7` (48 px).
- **Anchos y alturas:** `--measure` (70ch, línea de lectura), `--content-max` (1180 px, contenido de la app), `--page-max` (1240 px, portada), `--nav-height` (64 px) y `--sidebar-width` (272 px).
- **Bordes:** `--border-width` (1 px), finos siempre.
- **Radios:** `--radius-sm` (8 px) para controles, `--radius-md` (12 px) para tarjetas, `--radius-lg` (16 px) para bloques grandes y `--radius-pill` para etiquetas.
- **Sombras:** solo dos, moderadas: `--shadow-1` (relieve mínimo) y `--shadow-2` (elementos flotantes: menús, avisos).

## Estados de interacción

| Estado | Cómo se ve |
|---|---|
| Hover | Fondo `*-hover` o subrayado del enlace |
| Foco | Contorno de 2 px en `--color-primary` (`:focus-visible`, `base.css`) y `--focus-ring` en los campos |
| Desactivado u ocupado | Opacidad reducida (`--state-disabled-opacity`; `.btn:disabled`, `widgets.css`) y el texto del botón dice qué pasa («Ejecutando…», «Comprobando…») |
| Cargando | Texto que dice qué se carga («Cargando Python…», «Cargando el curso…»). El estado de la consola se anuncia con `aria-live`; el resto de zonas aún no (pendiente de la fase de accesibilidad) |
| Error | Texto en `--color-danger` con la causa y qué hacer; nunca solo el color. En un formulario, el campo que falla lleva `aria-invalid="true"`, borde rojo y `aria-describedby` al mensaje, y recibe el foco (`js/form-errors.js`) |
| Vacío | `.empty-state`: borde discontinuo y una frase con el siguiente paso |
| No encontrado | `not-found.js`: título, la ruta pedida y enlaces para volver |

**Movimiento:** `--duration-fast` (120 ms), `--duration` (180 ms) y `--duration-slow` (320 ms) con la curva `--ease`; `--transition` las combina. Solo para responder a una acción (hover, abrir, progreso), nunca de adorno, y se anulan con `prefers-reduced-motion`.

## Componentes

Componentes que ya existen y se reutilizan (no se crean otros parecidos):

| Componente | Clase | Dónde está |
|---|---|---|
| Botón | `.btn`, `.btn--primary`, `.btn--ghost`, `.btn--success` | `content.css` (y retoques en `academy.css` y `pro.css`; ver deuda) |
| Cabecera de página | `.course-hero`, `.eyebrow` | `academy.css`, `pro.css` |
| Estado vacío | `.empty-state` | `pcap.css` |
| Pista | `.hint` | `content.css` |
| Aviso flotante | `.toast` | `content.css` |
| Chips de filtro | `.chips`, `.chip` | `pcap.css` |
| Página no encontrada | `notFoundHtml()` | `js/not-found.js` |
| Corrección de un ejercicio | `.check`, `.check__label`, `.check__retry` | `console.css` y `console.js`. Si falla, por partes: «Qué falta» (o «Error al ejecutar»), «Con esta entrada», «Lo que mostró tu programa» y cómo seguir. Nunca enseña la solución |
| Confirmación dentro de la página | `.exam-confirm` (`role="alertdialog"`) | `pcap.js`. El foco va al botón principal, Esc la cierra y el foco vuelve al botón que la abrió |

**Deuda conocida:** `.btn` y `.course-hero` se definen en varias hojas, que se pisan por orden de carga. En los siguientes PR de la Fase 2 se reúnen en un solo sitio, comprobándolo con capturas de pantalla como se hizo con `tokens.css`.

## Diseño adaptable

- Móvil primero. La barra lateral pasa a ser un menú deslizante por debajo de **900 px** (`base.css`, `pro.css`).
- Puntos de corte que se usan: 600, 900 y 1280 px. Hay otros sueltos (420, 680, 700, 800, 1020, 1100, 1140) que se irán unificando.
- Sin desplazamiento horizontal: comprobado a 375 px en las vistas principales (ver `docs/AUDITORIA_TECNICA.md`, §4.5), y con la letra al 200 % a 768 px (`e2e/a11y.spec.js`).
- El texto se mide en `rem` (también el de `body`), para que crezca si el alumno agranda la letra en el navegador. Un elemento de rejilla que contiene código lleva `minmax(0, 1fr)`: si no, el código ancho ensancha la tarjeta en vez de desplazarse dentro.

## Cómo comprobar un cambio visual

1. Capturas antes y después de las vistas principales en los dos temas y a 1280 y 375 px. Si el cambio debía ser invisible (como mover tokens), las capturas tienen que coincidir píxel a píxel.
2. `npm run test:e2e`: incluye axe-core en los dos temas.
3. Revisar con teclado: el foco se ve en todos los controles.


## Rediseño de interfaz

El rediseño integral se aplica desde frontend/css/redesign.css. La hoja contiene las reglas de composición y componentes; los colores, radios, sombras y anchos siguen centralizados en frontend/css/tokens.css.

La dirección visual utiliza superficies neutras, navegación lateral más compacta, jerarquía clara, paneles discretos y una distribución de escritorio que separa la lectura de la consola. En móvil la consola vuelve al flujo de lectura y la navegación utiliza el cajón lateral existente.

El rediseño cubre la portada pública, el marco de la aplicación, navegación, panel del alumno, Aprender, teoría, práctica, lecciones, consola, PCAP, DAW, perfil, cuenta, asistente y módulos complementarios. No cambia los contratos de datos ni las rutas.

La revisión de accesibilidad y pruebas visuales está documentada en REDISENO-FRONTEND.md. Los valores de contraste de la tabla anterior deben recalcularse cuando se modifiquen los tokens; no se debe dar por demostrada la conformidad WCAG por el mero hecho de conservar la estructura anterior.
