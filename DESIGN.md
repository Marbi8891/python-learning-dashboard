# PLD — Design System

**Estado:** fuente de verdad del rediseño frontend.  
**Alcance:** presentación visual y accesibilidad.  
**Implementación actual:** `frontend/css/tokens.css` y `frontend/css/redesign.css`.

Este documento define el sistema visual de Python Learning Dashboard (PLD). Si una regla antigua contradice esta guía, se actualiza en una fase de rediseño revisable; no se cambia por este documento la funcionalidad de la aplicación.

## 1. Principios

- El contenido de aprendizaje, el texto, los ejercicios y el código tienen prioridad sobre la decoración.
- Usar un significado consistente para los colores: ámbar = acción/foco, verde = progreso/acierto, rojo = error, cian = detalles de interfaz developer.
- Nunca transmitir un estado únicamente mediante color.
- Mantener el tema claro y oscuro, las preferencias de contraste, tamaño y espaciado, y el movimiento reducido.
- Preferir jerarquía tipográfica, espacio y alineación a tarjetas, sombras o adornos.
- Diseño responsive, sin desbordamiento horizontal ni pérdida de controles.
- No añadir dependencias ni reemplazar la arquitectura HTML/CSS/ES Modules.

## 2. Temas y colores

Los tokens de `tokens.css` son los valores de implementación vigentes.

| Token | Función | Oscuro | Claro |
|---|---|---|---|
| `--color-bg` | Fondo principal | `#101318` | `#f4f5f7` |
| `--color-surface` | Paneles principales | `#171c23` | `#ffffff` |
| `--color-surface-2` | Superficie secundaria | `#1d242d` | `#f7f8fa` |
| `--color-code-bg` | Editor/código | `#0e1013` | `#16181c` |
| `--color-border` | Separadores decorativos | `#2b3440` | `#e5e8ed` |
| `--color-border-control` | Controles | `#697586` | `#aeb6c2` |
| `--color-text` | Texto principal | `#e8edf4` | `#202631` |
| `--color-text-muted` | Texto secundario | `#a8b2c0` | `#626d7b` |
| `--color-strong` | Titulares/énfasis | `#f7f9fc` | `#141a23` |
| `--color-link` | Enlaces | `#f4c46d` | `#8c5708` |
| `--color-primary` | Acción, foco y marca | `#f2b443` | `#8f5600` |
| `--color-primary-strong` | Fondo de acción principal | `#f2b443` | `#f3b84e` |
| `--color-on-primary` | Texto sobre acción | `#1b1405` | `#1b1405` |
| `--color-accent` | Progreso/acierto | `#3ccb72` | `#166534` |
| `--color-danger` | Error | `#f87171` | `#b91c1c` |

Developer accent:
- Dark: `--dev-accent: #55c7e8`
- Light: `--dev-accent: #087eaa`

Rules:
- El ámbar es el acento principal de acción. En tema claro, el ámbar oscuro se usa para texto y marcas; el ámbar claro se reserva para fondos de botón con texto oscuro.
- Verde y rojo conservan significado semántico.
- El cian es auxiliar y no sustituye el acento principal.
- El código y la consola permanecen en superficies oscuras en ambos temas.
- Los bordes decorativos no se usan como único límite perceptible de un control.

## 3. Tipografía

| Token | Familia | Uso |
|---|---|---|
| `--font-sans` | Inter + fallback del sistema | UI y contenido |
| `--font-display` | Fraunces + Georgia | Titulares editoriales/portada y cursos |
| `--font-mono` | JetBrains Mono + monospace | Código, consola y datos técnicos |

Escala vigente:
| Token | Tamaño |
|---|---|
| `--text-xs` | 0.75rem |
| `--text-sm` | 0.875rem |
| `--text-md` | 1rem |
| `--text-lg` | 1.125rem |
| `--text-xl` | 1.375rem |
| `--text-2xl` | 1.75rem |
| `--text-3xl` | clamp(1.875rem, 4vw, 2.625rem) |

- Texto: `--leading-body: 1.6`.
- Titulares: `--leading-tight: 1.2`.
- Los tamaños deben expresarse preferentemente en `rem` o `clamp()`.
- Las preferencias del alumno `data-font` controlan `--ui-zoom`; no deben neutralizarse en el rediseño.

## 4. Espaciado y geometría

Espaciado basado en 4 px:
| Token | Valor |
|---|---|
| `--space-1` | 4px |
| `--space-2` | 8px |
| `--space-3` | 12px |
| `--space-4` | 16px |
| `--space-5` | 24px |
| `--space-6` | 32px |
| `--space-7` | 48px |

Geometría vigente:
- `--measure: 70ch` (longitud de lectura)
- `--content-max: 1180px`
- `--page-max: 1240px`
- `--nav-height: 64px`
- `--sidebar-width: 260px`
- `--tap-target: 44px`

## 5. Bordes, radios y elevación

- Borde estándar: `--border-width: 1px`.
- Radios: `--radius-sm: 10px`, `--radius-md: 14px`, `--radius-lg: 20px`, `--radius-pill: 999px`.
- Sombras: usar `--shadow-1` para separación mínima y `--shadow-2` para elementos flotantes. No introducir sombras decorativas fuertes.
- `--focus-ring` y `--focus-outline` son los tokens de foco.

## 6. Interacción

- Hover: cambio moderado de fondo, borde o color; nunca depender de hover para descubrir una acción.
- Focus: indicador claro y visible para teclado mediante `:focus-visible`.
- Active: respuesta breve; evitar movimiento que distraiga.
- Disabled: usar `--state-disabled-opacity` y un estado/label comprensible.
- Loading: mostrar texto de estado. No alterar la lógica ni los estados existentes.
- Error: texto explicativo y acción siguiente cuando sea posible; no solo rojo.
- Empty state: explicar qué está vacío y cuál es el siguiente paso.
- Objetivos táctiles: mínimo recomendado 44 px cuando el control lo permita.

## 7. Motion

Tokens vigentes:
- `--duration-fast: 120ms`
- `--duration: 180ms`
- `--duration-slow: 320ms`
- `--ease: cubic-bezier(.2, 0, 0, 1)`

Solo usar animación para respuesta a interacción o transición funcional. Respetar:
- `prefers-reduced-motion: reduce`
- `data-motion="reducido"`

## 8. Responsive

- Mobile-first.
- El shell cambia a navegación móvil en el breakpoint de 900 px, que corresponde al comportamiento existente.
- Breakpoints de referencia para revisión: 600, 900 y 1280 px.
- Viewports de validación: 375, 768, 1280 y 1440 px.
- No introducir scroll horizontal en la página; los bloques de código deben desplazarse dentro de su contenedor.
- El drawer, navegación, controles y contenido deben conservar su comportamiento actual.

## 9. Componentes existentes

Reutilizar y normalizar los componentes que ya existen; no crear duplicados visuales sin necesidad:
- Botones: `.btn`, `.btn--primary`, `.btn--ghost`, `.btn--success`.
- Cabeceras: `.course-hero`, `.eyebrow`.
- Estado vacío: `.empty-state`.
- Pistas: `.hint`.
- Toast: `.toast`.
- Chips: `.chips`, `.chip`.
- Feedback de ejercicio: `.check` y sus subcomponentes.
- Confirmación de examen: `.exam-confirm`.

La duplicación actual de definiciones CSS es deuda de implementación. La consolidación requiere capturas antes/después y revisión de regresiones.

## 10. Accesibilidad

Objetivos de diseño:
- Contraste WCAG AA para texto y contraste no textual aplicable.
- Foco visible en navegación por teclado.
- Zoom de texto, alto contraste, texto espaciado y movimiento reducido respetados.
- Semántica, labels y mensajes de estado conservados.
- No ocultar controles ni indicadores de progreso mediante CSS.
- Validar axe/E2E y revisión manual; esta guía no constituye una certificación WCAG.

## 11. Alcance del rediseño

**Permitido:** CSS, tokens, composición, tipografía, espaciado, responsive, estados visuales y ajustes mínimos de markup/atributos de accesibilidad estrictamente presentacionales.

**Protegido:** backend, APIs, autenticación, base de datos, rutas, contenido curricular, Pyodide/Worker/runner, estado de aprendizaje, XP, progreso, logros, sincronización, stores, persistencia, infraestructura, dependencias y build/deploy.

Cualquier cambio JavaScript debe justificarse, ser pequeño y demostrar que no altera comportamiento. Se priorizarán cambios CSS-only.

## 12. Proceso de revisión

Cada fase debe:
1. Trabajar en una rama separada.
2. Identificar archivos y alcance antes del cambio.
3. Capturar baseline y screenshots cuando haya runtime/browser.
4. Cambiar un conjunto pequeño de componentes.
5. Ejecutar pruebas disponibles y revisión de diff.
6. Comparar light/dark, responsive y estados.
7. Documentar limitaciones y no afirmar verificaciones no ejecutadas.

Esta guía es la fuente de verdad para el rediseño. `tokens.css` es su implementación; si hay discrepancia, actualizar uno de forma explícita y revisable.
