# Condiciones de uso: borrador

| Campo | Valor |
|---|---|
| Estado | **BORRADOR**, no publicar |
| Documento | Nuevo: `frontend/condiciones.html` (propuesto) |
| Versión | 0.1 · 19/10/2026 |
| Titular | Mrabeh Fathi Boussayff (declarado en el repo) |
| Pendiente | P1, P4 y P5 del [diagnóstico](../DIAGNOSTICO.md); decisión sobre la edad mínima |

Por qué hace falta: hoy no hay ningún texto que fije la edad mínima, el uso aceptable de la cuenta y del
tutor ni los límites de responsabilidad del servicio (H15). El aviso legal cubre la identidad del
titular y la propiedad intelectual, pero no la relación con quien se registra.

---

## Texto propuesto para publicación

### Condiciones de uso de Python Learning Dashboard

Última actualización: [FECHA DE APROBACIÓN]

**1. Qué es este servicio.** Python Learning Dashboard es un proyecto educativo gratuito de Mrabeh Fathi
Boussayff, persona física (contacto: [CORREO DE CONTACTO]), para aprender Python y preparar el examen
PCAP y el módulo de Programación de DAW. No tiene publicidad ni actividad comercial. Puedes usarlo sin
cuenta. Estas condiciones se aplican cuando creas una cuenta o usas el tutor.

**2. Edad mínima.** Para crear una cuenta debes tener al menos 14 años. Si tienes menos, necesitas que
tu padre, madre o tutor legal lo autorice.

**3. Tu cuenta.** Eres responsable de lo que se haga con tu cuenta y de mantener tu contraseña en
secreto. Si sospechas que alguien ha entrado, cambia la contraseña o cierra todas las sesiones desde
«Mi panel». Puedes eliminar tu cuenta cuando quieras [desde «Tu cuenta → Eliminar mi cuenta» / por
email, según se corrija el borrado de cuentas de Google].

**4. Uso aceptable.** No está permitido:
- intentar acceder a cuentas o datos de otras personas;
- sobrecargar o atacar el servicio, o probar su seguridad sin seguir la
  [política de seguridad](https://github.com/Marbi8891/python-learning-dashboard/blob/main/SECURITY.md);
- usar el tutor para obtener contenido ajeno al aprendizaje de programación;
- escribir datos personales de otras personas, contraseñas o claves en el código o en las preguntas.

Podemos suspender una cuenta que incumpla estas reglas, avisándote por email salvo que el aviso
permita continuar un ataque.

**5. Tutor Python.** El tutor solo funciona si el servidor lo tiene activado. Cada respuesta indica si la
ha escrito un modelo de inteligencia artificial o el tutor sin IA, basado en reglas y en el contenido del
curso. Las respuestas pueden contener errores: compruébalas ejecutando el código y consultando la
documentación oficial de Python. El tutor no evalúa ni certifica tus conocimientos.

**6. Contenido y propiedad intelectual.** El código del proyecto se publica con licencia MIT. Las
explicaciones y las preguntas son del titular, salvo que se indique otra fuente. El código que escribes
en los ejercicios es tuyo; solo lo guardamos para mostrarte tu progreso, según la
[política de privacidad](privacidad.html).

**7. Sin garantías.** El servicio se ofrece gratis y tal cual, sin garantía de disponibilidad ni de
aprobar ningún examen. El certificado que genera la web no es oficial. PCAP es una marca de sus
titulares y este proyecto no está afiliado a Python Institute.

**8. Responsabilidad.** El titular no responde de los daños que resulten del uso del servicio, salvo los
que la ley no permita excluir.

**9. Cambios.** Si cambian estas condiciones, publicaremos la nueva versión con su fecha. Si el cambio
es importante, te avisaremos al iniciar sesión.

**10. Ley aplicable.** Estas condiciones se rigen por la ley española.

---

## Notas internas (no publicar)

- **Edad de 14 años:** es una recomendación preventiva (D3 del diagnóstico). LOPDGDD art. 7 fija 14 años
  para el *consentimiento*, que no es la base de este tratamiento. La capacidad de un menor para aceptar
  condiciones no se ha consultado (Código Civil). Si se quiere dirigir a menores, conviene revisión
  profesional.
- **Cláusula 8:** las exclusiones de responsabilidad frente a consumidores están limitadas por la
  normativa de consumidores, que no se ha consultado. Por eso dice «salvo los que la ley no permita
  excluir». Si el servicio es gratuito y no hay empresario, es posible que esa normativa ni siquiera
  se aplique (condicionado a P2).
- **Cláusula 5:** cubre la transparencia del RIA art. 50.1 si hay un modelo en producción (P4). El
  diseño actual ya etiqueta el origen (`frontend/js/tutor.js:91-95`). No se ha probado en ejecución.
- **Cláusula 4 (suspensión):** no existe en el código una función para suspender cuentas. O se elimina
  la frase o se documenta cómo se haría (borrado manual en Neon).
- **Aceptación:** habría que añadir «y las condiciones de uso» a las casillas de `index.html:290` y
  `:306`, y decidir qué pasa con las cuentas existentes (aviso al iniciar sesión).

## Lista de comprobación antes de publicar

- [ ] Edad mínima decidida por el titular.
- [ ] Cláusula 3 coherente con el borrado real de cuentas de Google.
- [ ] Cláusula 4: suspensión posible en la práctica o eliminada.
- [ ] Casillas de aceptación actualizadas (cambio de código en su propio PR).
- [ ] Aprobación del titular para esta versión concreta.
