# Plan de aprendizaje y preparación de la defensa de PLD

## Objetivo

Preparar al alumno para explicar, modificar y justificar los componentes principales de Python Learning Dashboard. El objetivo no es memorizar todo el repositorio, sino entender los flujos importantes y saber localizar la documentación y las pruebas.

El plan es una guía. Marcar una actividad como completada solo después de realizarla y conservar la evidencia.

## Método de trabajo

Cada tema se trabaja en tres pasos:

1. **Comprender:** explicar el componente con palabras propias y dibujar el flujo.
2. **Modificar:** realizar un cambio pequeño en una rama de trabajo y probarlo.
3. **Justificar:** explicar por qué se utiliza esa solución, qué alternativa existe y qué limitaciones tiene.

## Itinerario técnico

| Bloque | Qué debes poder explicar | Práctica propuesta | Evidencia |
|---|---|---|---|
| Arquitectura | Frontend estático, API, base de datos y despliegue | Dibujar el recorrido de una petición desde el navegador hasta PostgreSQL | Diagrama propio |
| HTML y CSS | Estructura semántica, diseño adaptable y accesibilidad | Corregir un componente para teclado y móvil | PR y prueba manual |
| JavaScript | Módulos ES, eventos, asincronía, Fetch y errores | Añadir un estado de carga y un mensaje de error a una vista | Test o captura |
| API REST | Métodos HTTP, rutas, códigos de estado y validación | Añadir o modificar un endpoint sencillo | Test de API |
| FastAPI | Routers, dependencias, esquemas y ciclo de petición | Explicar una ruta real del proyecto línea por línea | Explicación grabada o notas |
| SQL y PostgreSQL | Tablas, claves, relaciones e integridad | Consultar datos relacionados y explicar el resultado | Consultas SQL |
| SQLAlchemy y Alembic | Modelos ORM y migraciones | Seguir una migración desde el modelo hasta la base de datos | Migración revisada |
| Autenticación | Hash de contraseñas, cookies, sesión, CSRF y permisos | Dibujar login y una petición autenticada | Diagrama y pruebas |
| Pyodide y Web Workers | WebAssembly, mensajes y límites del worker | Seguir una ejecución desde el editor hasta el resultado | Diagrama de secuencia |
| Pruebas | Unitarias, integración y E2E | Añadir un test para un caso límite | Resultado de test |
| Docker y despliegue | Imagen, contenedor, variables y servicios | Levantar el entorno local y localizar los logs | Evidencia de ejecución |
| Seguridad y privacidad | Secretos, validación, autorización y datos personales | Revisar una ruta que modifica datos y comprobar la propiedad del recurso | Checklist de revisión |

## Preguntas que debes responder sin leer

### Arquitectura y frontend

1. ¿Qué se ejecuta en el navegador y qué se ejecuta en el servidor?
2. ¿Por qué el frontend puede publicarse como sitio estático?
3. ¿Qué ocurre cuando JavaScript llama a la API mediante fetch?
4. ¿Cómo se gestionan los errores de red y las respuestas HTTP no satisfactorias?
5. ¿Qué ventaja aporta utilizar módulos ES?

### Backend y datos

6. ¿Qué responsabilidad tiene FastAPI?
7. ¿Qué diferencia hay entre un modelo SQLAlchemy y un esquema Pydantic?
8. ¿Qué es una clave primaria y qué es una clave foránea?
9. ¿Qué problema resuelve una migración de Alembic?
10. ¿Cómo se evita que un usuario consulte o modifique datos de otra cuenta?

### Ejecución de Python

11. ¿Qué es Pyodide y cómo permite ejecutar Python en el navegador?
12. ¿Por qué se utiliza un Web Worker?
13. ¿Cómo se comunica la página con el Worker?
14. ¿Qué ocurre cuando se supera el límite de ejecución?
15. ¿Por qué un Worker no debe describirse como un aislamiento de seguridad completo?

### Seguridad, pruebas y despliegue

16. ¿Por qué se almacenan contraseñas mediante un hash seguro y no en texto plano?
17. ¿Qué protege una cookie HttpOnly y qué no protege?
18. ¿Qué problema intenta evitar la protección CSRF?
19. ¿Qué diferencia hay entre pruebas unitarias, de integración y E2E?
20. ¿Qué información debe mantenerse fuera del repositorio?

## Registro de dominio personal

| Tema | Puedo explicarlo | Puedo modificarlo | Puedo justificarlo | Pendiente |
|---|---|---|---|---|
| Arquitectura | [ ] | [ ] | [ ] | [Anotar] |
| Frontend | [ ] | [ ] | [ ] | [Anotar] |
| Backend | [ ] | [ ] | [ ] | [Anotar] |
| Base de datos | [ ] | [ ] | [ ] | [Anotar] |
| Autenticación | [ ] | [ ] | [ ] | [Anotar] |
| Pyodide y Worker | [ ] | [ ] | [ ] | [Anotar] |
| Pruebas | [ ] | [ ] | [ ] | [Anotar] |
| Despliegue | [ ] | [ ] | [ ] | [Anotar] |

## Guion de defensa

1. Presentar el problema y el perfil de usuario al que se dirige PLD.
2. Explicar los objetivos y el alcance real.
3. Mostrar la arquitectura y justificar las tecnologías principales.
4. Demostrar un recorrido completo: abrir una lección, ejecutar Python, resolver un ejercicio y consultar el progreso.
5. Explicar cómo se guardan y protegen los datos.
6. Enseñar pruebas reales y explicar qué comprueban.
7. Declarar el uso de IA y mostrar ejemplos verificables de revisión y validación.
8. Reconocer limitaciones y proponer mejoras razonables.

Ajustar la duración y el formato a las instrucciones del centro. El guion existente está en [DEMO-Y-DEFENSA.md](../DEMO-Y-DEFENSA.md).

## Criterio de preparación

No dar un bloque por dominado por haber leído la documentación. Se considera preparado cuando el alumno puede explicarlo con sus propias palabras, hacer una modificación pequeña y enseñar cómo la ha comprobado.
