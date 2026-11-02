# Sistema visual

Guía del diseño de la web. Los valores están en **`frontend/css/tokens.css`**, la primera hoja que se carga. Ninguna otra hoja debe definir colores, tamaños ni radios nuevos: se usan las variables de aquí. Si falta alguna, se añade aquí.

## Principios

1. **El contenido manda.** Primero el texto, el código y el ejercicio. Sin degradados, cristal ni animaciones decorativas.
2. **Un color, un significado.** El azul es para la acción principal y el foco. El verde, para el progreso y los aciertos. El rojo, para los errores. El color nunca va solo: siempre lo acompaña un texto o un icono (✓, ✗).
3. **Datos reales.** No se muestran cifras que la web no pueda calcular: ni horas, ni porcentajes inventados, ni estadísticas de usuarios.
4. **Accesible por defecto.** Contraste AA, foco visible, objetivos táctiles de 44 px y respeto por `prefers-reduced-motion`.

## Color

Hay dos temas. El claro y el oscuro se eligen en «Preferencias» o siguen al sistema (`theme-init.js` pone `data-theme` en `<html>`).

| Token | Uso | Oscuro | Claro |
|---|---|---|---|
| `--color-bg` | Fondo de la página | `#0b0f14` | `#f5f7fa` |
| `--color-surface` | Tarjetas y paneles | `#111720` | `#ffffff` |
| `--color-surface-2` | Superficie secundaria | `#17202b` | `#f0f3f7` |
| `--color-border` | Separadores | `#263241` | `#dce3eb` |
| `--color-text` | Texto | `#edf2f7` | `#17202b` |
| `--color-text-muted` | Texto secundario | `#9aa8b8` | `#5d6b7b` |
| `--color-primary` | Enlaces destacados, foco | `#60a5fa` | `#2563eb` |
| `--color-primary-strong` | Fondo del botón principal | `#2563eb` | `#1d4ed8` |
| `--color-accent` | Progreso, aciertos | `#22c55e` | `#166534` |
| `--color-danger` | Errores | `#f87171` | `#b91c1c` |
| `--color-code-bg` | Fondo del código (oscuro en los dos temas) | `#080c11` | `#0b1118` |

Contrastes calculados (WCAG 2.x, sobre `--color-surface` salvo que se indique otra cosa):

| Par | Oscuro | Claro | Mínimo AA |
|---|---|---|---|
| Texto | 16,0:1 | 16,4:1 | 4,5:1 |
| Texto secundario | 7,4:1 | 5,4:1 | 4,5:1 |
| Texto tenue sobre `surface-2` | 5,6:1 | 4,9:1 | 4,5:1 |
| Enlace | 10,0:1 | 6,7:1 | 4,5:1 |
| Texto del botón principal | 5,2:1 | 6,7:1 | 4,5:1 |
| Verde de progreso | 7,9:1 | 7,1:1 | 3:1 (gráficos) |
| Rojo de error | 6,5:1 | 6,5:1 | 4,5:1 |
| **Borde** | **1,4:1** | **1,3:1** | 3:1 si es el único límite de un control |

El borde no llega a 3:1. Vale para separar tarjetas, pero no como único contorno de un campo de formulario (WCAG 1.4.11). Está anotado como AUD-035 y se corrige en la fase de accesibilidad.

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
- **Radios:** `--radius-sm` (8 px) para controles, `--radius-md` (12 px) para tarjetas, `--radius-lg` (16 px) para bloques grandes y `--radius-pill` para etiquetas.
- **Sombras:** solo dos, moderadas: `--shadow-1` (relieve mínimo) y `--shadow-2` (elementos flotantes: menús, avisos).

## Estados de interacción

| Estado | Cómo se ve |
|---|---|
| Hover | Fondo `*-hover` o subrayado del enlace |
| Foco | Contorno de 2 px en `--color-primary` (`:focus-visible`, `base.css`) y `--focus-ring` en los campos |
| Desactivado u ocupado | Opacidad reducida (`.btn:disabled`, `widgets.css`) y el texto del botón dice qué pasa («Ejecutando…», «Comprobando…») |
| Cargando | Texto que dice qué se carga («Cargando Python…», «Cargando el curso…»). El estado de la consola se anuncia con `aria-live`; el resto de zonas aún no (pendiente de la fase de accesibilidad) |
| Error | Texto en `--color-danger` con la causa y qué hacer; nunca solo el color |
| Vacío | `.empty-state`: borde discontinuo y una frase con el siguiente paso |
| No encontrado | `not-found.js`: título, la ruta pedida y enlaces para volver |

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

**Deuda conocida:** `.btn` y `.course-hero` se definen en varias hojas, que se pisan por orden de carga. En los siguientes PR de la Fase 2 se reúnen en un solo sitio, comprobándolo con capturas de pantalla como se hizo con `tokens.css`.

## Diseño adaptable

- Móvil primero. La barra lateral pasa a ser un menú deslizante por debajo de **900 px** (`base.css`, `pro.css`).
- Puntos de corte que se usan: 600, 900 y 1280 px. Hay otros sueltos (420, 680, 700, 800, 1020, 1100, 1140) que se irán unificando.
- Sin desplazamiento horizontal: comprobado a 375 px en las vistas principales (ver `docs/AUDITORIA_TECNICA.md`, §4.5).

## Cómo comprobar un cambio visual

1. Capturas antes y después de las vistas principales en los dos temas y a 1280 y 375 px. Si el cambio debía ser invisible (como mover tokens), las capturas tienen que coincidir píxel a píxel.
2. `npm run test:e2e`: incluye axe-core en los dos temas.
3. Revisar con teclado: el foco se ve en todos los controles.
