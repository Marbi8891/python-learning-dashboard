## Qué cambia

<!-- Una o dos frases. Si cierra un issue: «Cierra #N». -->

## Por qué

<!-- El problema que resuelve o lo que permite. -->

## Cómo se ha probado

<!-- Los comandos de docs/TESTING.md que tocan a este cambio y su resultado. -->

- [ ] `cd backend && python -m pytest -q --cov=app --cov-fail-under=100`
- [ ] `npm run test:unit`
- [ ] `npm run test:e2e`
- [ ] Otro: 

## Lista de comprobación

- [ ] La rama sigue el formato `tipo/descripcion` y el cambio es de un solo tema.
- [ ] No hay JSON de `frontend/data/` editado a mano (se ha regenerado con su script).
- [ ] No se ha saltado ni debilitado ningún test.
- [ ] No hay secretos ni datos personales en el diff.
- [ ] La documentación y el `CHANGELOG.md` están al día, si hacía falta.
- [ ] Si cambia la interfaz: capturas de antes y después, en tema claro y oscuro.
