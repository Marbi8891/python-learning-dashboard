# Plan de corrección

Qué se corrige, en qué orden, quién lo hace y con qué archivos. Lo mantiene `security-lead`.
Ninguna corrección empieza sin estar en la tabla «En curso» (bloqueo de archivos, ver
[`AGENT_WORKFLOW.md`](AGENT_WORKFLOW.md) §4) y ninguna afecta a producción sin autorización de la persona.

## En curso

Archivos bloqueados mientras un agente los edita. Vacía = nadie está corrigiendo nada.

| Hallazgo | Dueño | Archivos | Desde |
|---|---|---|---|
| — | — | — | — |

## Pendientes de autorización

Las tres afectan a la web publicada o al despliegue: no se aplican sin el «sí» de la persona.

| Orden | Hallazgo | Cambio | Consecuencias | Cómo validarlo |
|---|---|---|---|---|
| 1 | PLD-SEC-003 | Activar `production_csp.py` al publicar: **aplicado en el PR #55** | La web publicada deja de permitir `127.0.0.1:8000` y `localhost:8000`. Desarrollo y e2e no cambian | CI en verde; tras el despliegue, ver el `<meta>` de la web publicada y probar login y consola |
| 2 | PLD-SEC-005 | `backend/requirements.lock` con *hashes* y `pip install --require-hashes` en el Dockerfile | Builds reproducibles. Cada cambio de dependencias exige regenerar el lock (Dependabot no lo hace solo con `requirements.txt`) | Build de Docker local, pytest dentro de la imagen, despliegue en Render y `/api/v1/health` |
| 3 | PLD-SEC-004 (barrera completa) | Crear el Worker desde una URL `blob:` y añadir `blob:` a `worker-src` | El Worker heredaría la CSP de la página. Amplía `worker-src`, así que hay que valorarlo | e2e completo, incluida la prueba de PLD-SEC-004, en Chromium, Firefox y Safari |

### Parche de PLD-SEC-003 (`.github/workflows/pages.yml`, aplicado en el PR #55)

```yaml
      - uses: actions/checkout@v7
        with:
          persist-credentials: false
      - name: CSP de producción sin los orígenes de desarrollo (PLD-SEC-003)
        run: python scripts/security/production_csp.py frontend
      - uses: actions/configure-pages@v6
```

El script solo modifica la copia del runner que se sube a Pages; si queda algún origen `http:` en
la CSP, falla y no se publica nada.

### Pasos propuestos para PLD-SEC-005 (sin aplicar)

```bash
pip install uv
uv pip compile backend/requirements.txt --python-version 3.12 \
  --python-platform x86_64-manylinux_2_28 --generate-hashes -o backend/requirements.lock
```

En `backend/Dockerfile`: `COPY backend/requirements.lock .` y
`RUN pip install --require-hashes --only-binary=:all: -r requirements.lock`. Comprobado el
19/10/2026: 63 paquetes, todos instalables con sus *hashes* para Python 3.12 en Linux. Alternativa
más ligera: añadir límite superior a `python-multipart` y `argon2-cffi` y fijar la imagen base por *digest*.

## Hechas

| Hallazgo | Corrección | Commit / PR | Verificación |
|---|---|---|---|
| PLD-SEC-001 | `backend/tests/test_security_isolation.py` | rama `security/appsec-hardening-oxxazk` | 4 tests pasan; suite con 100 % de cobertura |
| PLD-SEC-002 | Escape de slugs en atributos de la barra lateral y test del formato permitido | PR #50, rama `security/appsec-hardening-oxxazk` | 639 tests backend (100 %) y 78 unitarios en verde |
| PLD-SEC-004 | Red cerrada en el Worker de Pyodide (`frontend/js/pyodide-worker.js`) | rama `security/appsec-hardening-oxxazk` | e2e de regresión falla sin la corrección y pasa con ella; 123 e2e en verde |
| PLD-SEC-003 (preparación) | `scripts/security/production_csp.py` + `backend/tests/test_production_csp.py` | ídem | 4 tests en verde; falta activarlo (arriba) |
| PLD-SEC-FP1 | `# nosec B310` justificado en `backend/app/mailer.py`, `.gitleaksignore` por huella | ídem | Bandit `-ll -ii` y Gitleaks sin hallazgos |

## Pendiente de la persona (no lo pueden hacer los agentes)

Ver [`SECURITY_TESTING.md`](SECURITY_TESTING.md) §6: activar *secret scanning* y *push protection*,
Dependabot alerts, CodeQL (*default setup*) y la regla de protección de `main` con los checks nuevos.
