# ruff: noqa: E501
# (contenido didáctico: los textos largos van en una sola línea para poder leerlos y editarlos)
"""Curso de JavaScript (módulo Desarrollo Web en Entorno Cliente de DAW) para la app (ADR-0016).

Cada pregunta de código se ejecuta con Node.js y su salida se compara con la esperada. Formato:
lo que imprime `console.log`, «(sin salida)» si no imprime nada y «Lanza NombreDelError» si
termina con un error sin capturar (tras lo que hubiera impreso antes).

Las preguntas imprimen textos y números, no arrays ni objetos sueltos: Node y la consola del
navegador los muestran con formatos distintos. El código del DOM y de `fetch` no se puede
ejecutar en Node: sus ejemplos solo se comprueban sintácticamente (`node --check`) y sus
preguntas son teóricas.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from course_builder import Block, Lesson, Q, main  # noqa: E402

ERROR = re.compile(r"^(\w*Error)\b", re.MULTILINE)
BROWSER_ONLY = ("document.", "window.", "fetch(", "localStorage")


def _node(code: str, *flags: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "programa.js"
        path.write_text(code, encoding="utf-8")
        return subprocess.run(
            ["node", *flags, str(path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )


def run_js(code: str) -> str:
    result = _node(code)
    out = "\n".join(line.rstrip() for line in result.stdout.strip("\n").splitlines())
    if result.returncode != 0:
        match = ERROR.search(result.stderr)
        if not match:
            raise RuntimeError(f"fallo inesperado:\n{result.stderr}")
        name = "Lanza " + match.group(1)
        return f"{out}\n{name}" if out else name
    return out or "(sin salida)"


def check_example(code: str) -> None:
    if any(api in code for api in BROWSER_ONLY):
        result = _node(code, "--check")
        assert result.returncode == 0, f"el ejemplo no es JavaScript válido:\n{result.stderr}"
        return
    output = run_js(code)
    assert not output.startswith("Lanza"), f"el ejemplo falla ({output}):\n{code}"


def cq(id: str, q: str, code: str, expect: str, wrong: list[str], explain: str) -> Q:
    code = code.strip()
    return Q(id=id, q=q, code=code, run=code, expect=expect, wrong=wrong, explain=explain)


def tq(id: str, q: str, options: list[str], answer: int, explain: str) -> Q:
    return Q(id=id, q=q, options=options, answer=answer, explain=explain)


QUE = "¿Qué muestra este código?"
OCURRE = "¿Qué ocurre al ejecutar este código?"

MDN = ("MDN Web Docs — JavaScript", "https://developer.mozilla.org/es/docs/Web/JavaScript")
MDN_DOM = (
    "MDN Web Docs — DOM",
    "https://developer.mozilla.org/es/docs/Web/API/Document_Object_Model",
)
JSINFO = ("javascript.info (tutorial moderno)", "https://es.javascript.info/")

# ---------------------------------------------------------------- bloque 1: fundamentos

L_VARIABLES = Lesson(
    slug="js-variables",
    title="Variables y tipos",
    theory="""
JavaScript es de **tipado dinámico**: el tipo va con el valor, no con la variable. Una misma variable puede guardar un número y después un texto.

**Declarar variables:**
- `const`: no se puede **reasignar**. Es la opción por defecto. Ojo: si guarda un array u objeto, su **contenido** sí puede cambiar (`lista.push(3)` funciona).
- `let`: se puede reasignar. Tiene ámbito de **bloque** (`{ … }`).
- `var`: la forma antigua, con ámbito de función y comportamientos sorprendentes. Evítala.
- Declarar dos veces con `let` o `const` en el mismo ámbito es un `SyntaxError`, y reasignar un `const` lanza `TypeError`.

**Tipos primitivos:** `number` (enteros y decimales son el mismo tipo), `string`, `boolean`, `undefined` (sin valor asignado), `null` (vacío a propósito), `bigint` y `symbol`. Todo lo demás es `object`: arrays, objetos, fechas…

`typeof` dice el tipo, con dos rarezas históricas: `typeof null` es `"object"` y `typeof function(){}` es `"function"`. Para saber si algo es un array, usa `Array.isArray(x)`.

**Plantillas de texto** con comillas invertidas: `` `Hola, ${nombre}` `` inserta cualquier expresión dentro de `${ }` y admite varias líneas.

En esta app el código se ejecuta con Node.js, que usa el mismo motor que Chrome.
""",
    example="""
const nombre = "Ana";
let nota = 7;
nota = nota + 1;

const modulos = ["DWEC", "DWES"];
modulos.push("DIW");

console.log(`${nombre} tiene un ${nota} en ${modulos.length} módulos`);
console.log(typeof nombre, typeof nota, Array.isArray(modulos));
""",
    exercise="""
Declara, con `const` o `let` según corresponda:

- tu nombre;
- tu edad (que cambiará el año que viene);
- una lista con tres lenguajes.

Muestra una frase con una plantilla de texto, suma 1 a la edad y vuelve a mostrarla.
""",
    starter='const nombre = "...";\nlet edad = 20;\nconst lenguajes = [];\n\nconsole.log(`...`);',
    hint="La edad cambia, así que va con `let`. La lista puede ser `const` aunque añadas elementos.",
    faq=[
        (
            "Si `const` no se puede cambiar, ¿por qué puedo hacer push?",
            "`const` impide **reasignar** la variable (`lista = []`), no modificar el objeto al que apunta. Para congelar el contenido existe `Object.freeze`.",
        ),
        (
            "¿`undefined` o `null`?",
            "`undefined` lo pone JavaScript cuando algo no tiene valor. `null` lo pones tú para decir «vacío a propósito».",
        ),
    ],
    challenge=(
        "Ficha de alumno",
        1,
        "Crea un objeto con nombre, ciclo y notas, y muestra con una plantilla de varias líneas su nombre, su ciclo y cuántas notas tiene.",
        'const alumno = { nombre: "Ana", ciclo: "DAW", notas: [7, 9] };\n\nconsole.log(`...`);',
        "Las plantillas admiten saltos de línea reales y cualquier expresión: `${alumno.notas.length}`.",
    ),
    questions=[
        cq(
            "js-01",
            QUE,
            'console.log(typeof 42, typeof "42", typeof true, typeof undefined);',
            "number string boolean undefined",
            [
                "number number boolean undefined",
                "int string boolean null",
                "number string bool undefined",
            ],
            '`typeof` devuelve el tipo del **valor**: "42" entre comillas es un string. No existe el tipo `int`: todos los números son `number`.',
        ),
        cq(
            "js-02",
            QUE,
            "console.log(typeof null, typeof [], typeof function () {});",
            "object object function",
            ["null array function", "null object function", "object array object"],
            'Dos rarezas: `typeof null` es "object" (un error histórico del lenguaje) y los arrays también son "object". Para arrays se usa `Array.isArray`.',
        ),
        cq(
            "js-03",
            QUE,
            "const lista = [1, 2];\nlista.push(3);\nconsole.log(lista.length);",
            "3",
            ["2", "Lanza TypeError", "Lanza SyntaxError"],
            "`const` impide reasignar la variable, pero el array se puede modificar: `push` añade un tercer elemento.",
        ),
        cq(
            "js-04",
            OCURRE,
            "const x = 1;\nx = 2;\nconsole.log(x);",
            "Lanza TypeError",
            ["2", "1", "Lanza SyntaxError"],
            "Reasignar una constante lanza `TypeError: Assignment to constant variable`. Si vas a cambiar el valor, usa `let`.",
        ),
        cq(
            "js-05",
            QUE,
            'const nombre = "Ana", nota = 7;\nconsole.log(`${nombre} tiene un ${nota + 1}`);',
            "Ana tiene un 8",
            ["Ana tiene un 71", "${nombre} tiene un ${nota + 1}", "Ana tiene un nota + 1"],
            "Dentro de `${ }` va una **expresión** que se evalúa: `nota + 1` es 8 porque `nota` es un número.",
        ),
    ],
    quiz=[
        cq(
            "js-q01",
            OCURRE,
            "let a = 5;\nlet a = 6;\nconsole.log(a);",
            "Lanza SyntaxError",
            ["6", "5", "Lanza TypeError"],
            "No se puede declarar dos veces la misma variable con `let` en el mismo ámbito. Es un error de sintaxis: el programa ni siquiera empieza.",
        ),
        tq(
            "js-q02",
            "¿Qué declaración conviene usar por defecto en JavaScript moderno?",
            [
                "`const`, y `let` solo si vas a reasignar",
                "`var`, porque funciona en todas partes",
                "`let` siempre",
                "Ninguna: se puede asignar sin declarar",
            ],
            0,
            "`const` deja claro que la variable no cambia y evita reasignaciones accidentales. `var` tiene un ámbito confuso.",
        ),
    ],
    sources=[MDN, JSINFO],
)

L_COERCION = Lesson(
    slug="js-coercion",
    title="Comparaciones y conversiones",
    theory="""
JavaScript **convierte tipos** automáticamente (*coerción*) en muchas operaciones, y ahí están sus trampas más famosas.

**== frente a ===:**
- `===` (igualdad estricta) compara tipo **y** valor: `5 === "5"` es `false`.
- `==` convierte antes de comparar: `5 == "5"` es `true`, y también `0 == ""` o `null == undefined`.
- Usa **siempre** `===` y `!==`.

**El operador +:** si uno de los operandos es un string, **concatena**: `"5" + 3` es `"53"`. Los demás operadores aritméticos convierten a número: `"5" - 3` es `2`.

**Valores falsy:** en un `if` se comportan como `false` seis valores: `false`, `0`, `""`, `null`, `undefined` y `NaN`. **Todo lo demás es truthy**, incluidos `"0"`, `"false"`, `[]` y `{}`.

**Valores por defecto:**
- `a || b` devuelve `b` si `a` es **falsy**, así que `0 || 18` da `18`, a veces sin querer.
- `a ?? b` (*nullish*) solo usa `b` si `a` es `null` o `undefined`: `0 ?? 18` da `0`.

**NaN** (*Not a Number*) es el resultado de una operación numérica imposible: `Number("abc")`. Es el único valor que no es igual a sí mismo (`NaN === NaN` es `false`). Se comprueba con `Number.isNaN(x)`.

Para convertir a propósito: `Number("12")`, `parseInt("12px")` (lee hasta donde puede), `String(12)` y `Boolean(x)`.
""",
    example="""
const entrada = "12";
const cantidad = Number(entrada);

console.log(entrada + 1, cantidad + 1);
console.log(entrada == 12, entrada === 12, cantidad === 12);

const descuento = 0;
console.log(descuento || 10, descuento ?? 10);
""",
    exercise="""
Un formulario te da los precios como texto: `const precios = ["10", "5.5", "abc", "20"];`.

Suma solo los que sean números válidos, usando `Number` y `Number.isNaN`, y muestra el total.
""",
    starter='const precios = ["10", "5.5", "abc", "20"];\nlet total = 0;\nfor (const p of precios) {\n  // ...\n}\nconsole.log(total);',
    hint="Convierte cada texto con `Number(p)` y súmalo solo si `!Number.isNaN(n)`.",
    faq=[
        (
            "¿Hay algún caso en que `==` sea útil?",
            "Solo `x == null`, que comprueba a la vez null y undefined. Aun así, muchos equipos lo prohíben por claridad.",
        ),
        (
            "¿`parseInt` o `Number`?",
            '`Number("12px")` da NaN; `parseInt("12px")` da 12 porque lee hasta donde puede. Para validar una entrada completa, `Number`.',
        ),
    ],
    challenge=(
        "Valor por defecto correcto",
        2,
        "Escribe `mostrarVolumen(v)`, que muestre 50 si no se le pasa volumen, pero respete un volumen de 0.",
        "function mostrarVolumen(v) {\n  // ...\n}\nmostrarVolumen();\nmostrarVolumen(0);",
        "Con `||` el 0 se convierte en 50; usa `??`.",
    ),
    questions=[
        cq(
            "js-06",
            QUE,
            'console.log(5 == "5", 5 === "5");',
            "true false",
            ["true true", "false false", "false true"],
            "`==` convierte el texto a número antes de comparar; `===` no convierte y los tipos son distintos.",
        ),
        cq(
            "js-07",
            QUE,
            'console.log("5" + 3, "5" - 3);',
            "53 2",
            ["8 2", "53 53", "8 NaN"],
            'Con un string, `+` concatena: "53". El `-` solo existe para números, así que convierte "5" a 5: 2.',
        ),
        cq(
            "js-08",
            QUE,
            'console.log(Boolean(""), Boolean("0"), Boolean([]), Boolean(0));',
            "false true true false",
            ["false false false false", "false false true false", "true true true false"],
            'Solo el texto vacío es falsy; "0" es un texto con un carácter. Un array, aunque esté vacío, es un objeto: truthy. El número 0 es falsy.',
        ),
        cq(
            "js-09",
            QUE,
            "const edad = 0;\nconsole.log(edad || 18, edad ?? 18);",
            "18 0",
            ["0 0", "18 18", "0 18"],
            "`||` descarta cualquier falsy, también el 0. `??` solo sustituye null o undefined, así que respeta la edad 0.",
        ),
        cq(
            "js-10",
            QUE,
            'console.log(NaN === NaN, Number.isNaN(Number("abc")));',
            "false true",
            ["true true", "false false", "true false"],
            'NaN es el único valor distinto de sí mismo. `Number("abc")` da NaN y `Number.isNaN` lo detecta.',
        ),
    ],
    quiz=[
        cq(
            "js-q03",
            QUE,
            "console.log(null == undefined, null === undefined);",
            "true false",
            ["true true", "false false", "false true"],
            "Con `==` null y undefined se consideran iguales; con `===` son tipos distintos.",
        ),
        tq(
            "js-q04",
            "¿Por qué se recomienda `===` en lugar de `==`?",
            [
                "Porque `==` convierte los tipos antes de comparar y da resultados sorprendentes",
                "Porque `==` está obsoleto y da error",
                "Porque `===` es más rápido siempre",
                "Porque `==` solo compara números",
            ],
            0,
            "Con `===` lo que ves es lo que comparas, sin conversiones ocultas.",
        ),
    ],
    sources=[MDN, JSINFO],
)

# ---------------------------------------------------------------- bloque 2: funciones y ámbito

L_FUNCIONES = Lesson(
    slug="js-funciones",
    title="Funciones",
    theory="""
Hay tres formas habituales de crear funciones:

- **Declaración:** `function doble(n) { return n * 2; }`. Se **eleva** (*hoisting*): puedes llamarla antes de la línea donde está escrita.
- **Expresión:** `const doble = function (n) { return n * 2; };`. No se puede usar antes de su línea.
- **Flecha:** `const doble = (n) => n * 2;`.
  - Con una sola expresión, devuelve su valor sin escribir `return`.
  - Si lleva llaves `{ }`, hace falta `return`.
  - Para devolver un objeto hay que envolverlo en paréntesis: `() => ({ ok: true })`.

**Parámetros:**
- Si falta un argumento, vale `undefined`, salvo que tenga **valor por defecto**: `(nombre = "invitado") =>`.
- `...nums` (parámetro *rest*) agrupa los argumentos que sobran en un array.

**Sin `return`**, una función devuelve `undefined`.

**Las funciones son valores:** se guardan en variables, se pasan como argumento (**callbacks**, como en `boton.addEventListener("click", manejar)` o `lista.map(doble)`) y se devuelven desde otras funciones.
""",
    example="""
function calcularIVA(precio, tipo = 0.21) {
  return precio * tipo;
}

const conIVA = (precio) => precio + calcularIVA(precio);
const sumar = (...importes) => importes.reduce((total, x) => total + x, 0);

console.log(calcularIVA(100), conIVA(100));
console.log(sumar(10, 20, 30));
console.log([1, 2, 3].map((n) => n * 10).join(" "));
""",
    exercise="""
Escribe `nota(puntos, total = 10)`, que devuelva la nota sobre 10 redondeada a un decimal.

Luego escribe una versión flecha llamada `aprobado`, que diga si una nota es de 5 o más.
""",
    starter="function nota(puntos, total = 10) {\n  // ...\n}\n\nconst aprobado = (n) => /* ... */;\n\nconsole.log(nota(7, 8), aprobado(nota(7, 8)));",
    hint="`Math.round(x * 10) / 10` redondea a un decimal.",
    faq=[
        (
            "¿Declaración o flecha?",
            "Para funciones con nombre de primer nivel, cualquiera. Las flechas son cómodas como callbacks. Diferencia importante: las flechas no tienen su propio `this`.",
        ),
        (
            "¿Qué es un callback?",
            "Una función que pasas a otra para que la llame después: al pulsar un botón, al acabar una petición o para cada elemento de un array.",
        ),
    ],
    challenge=(
        "Fábrica de saludos",
        2,
        'Escribe `crearSaludo(saludo)`, que **devuelva una función**: `crearSaludo("Hola")("Ana")` debe dar `"Hola, Ana"`.',
        'function crearSaludo(saludo) {\n  // return ...\n}\n\nconst hola = crearSaludo("Hola");\nconsole.log(hola("Ana"));',
        "Devuelve una flecha: `return (nombre) => `${saludo}, ${nombre}`;`. La función interior recuerda `saludo` (es un *closure*).",
    ),
    questions=[
        cq(
            "js-11",
            QUE,
            'const saludar = (nombre = "invitado") => `Hola, ${nombre}`;\nconsole.log(saludar(), saludar("Ana"));',
            "Hola, invitado Hola, Ana",
            ["Hola, undefined Hola, Ana", "Hola,  Hola, Ana", "Lanza TypeError"],
            "Sin argumento, el parámetro toma su valor por defecto. Una flecha sin llaves devuelve la expresión.",
        ),
        cq(
            "js-12",
            QUE,
            "console.log(doble(4));\n\nfunction doble(n) {\n  return n * 2;\n}",
            "8",
            ["Lanza ReferenceError", "undefined", "NaN"],
            "Las **declaraciones** de función se elevan (*hoisting*): existen desde el principio de su ámbito y se pueden llamar antes.",
        ),
        cq(
            "js-13",
            OCURRE,
            "console.log(triple(2));\n\nconst triple = (n) => n * 3;",
            "Lanza ReferenceError",
            ["6", "undefined", "Lanza TypeError"],
            "Una función guardada en un `const` no existe hasta su línea: usarla antes lanza `ReferenceError`.",
        ),
        cq(
            "js-14",
            QUE,
            "function suma(...nums) {\n  return nums.reduce((a, b) => a + b, 0);\n}\nconsole.log(suma(1, 2, 3), suma());",
            "6 0",
            ["6 undefined", "1 0", "Lanza TypeError"],
            "`...nums` recoge todos los argumentos en un array (vacío si no hay ninguno). El 0 inicial de `reduce` evita el error con el array vacío.",
        ),
        cq(
            "js-15",
            QUE,
            "function area(base, altura) {\n  base * altura;\n}\nconsole.log(area(2, 3));",
            "undefined",
            ["6", "null", "Lanza SyntaxError"],
            "Calcula el producto, pero no lo **devuelve**. Una función sin `return` devuelve `undefined`.",
        ),
    ],
    quiz=[
        cq(
            "js-q05",
            QUE,
            "const f = () => { ok: true };\nconsole.log(f());",
            "undefined",
            ["true", "Lanza SyntaxError", '{"ok":true}'],
            "Las llaves se interpretan como el **cuerpo** de la función (y `ok:` como una etiqueta), así que no devuelve nada. Para devolver un objeto: `() => ({ ok: true })`.",
        ),
        tq(
            "js-q06",
            "¿Cómo se llama una función que se pasa como argumento a otra para que la llame después?",
            ["Callback", "Constructor", "Promesa", "Módulo"],
            0,
            "Es la base de los eventos del DOM y de métodos como `map`, `filter` o `setTimeout`.",
        ),
    ],
    sources=[MDN, JSINFO],
)

L_AMBITO = Lesson(
    slug="js-ambito",
    title="Ámbito, hoisting y closures",
    theory="""
El **ámbito** (*scope*) es la zona del código donde existe una variable.

- `let` y `const` tienen ámbito de **bloque**: solo existen dentro de las llaves `{ }` donde se declaran (un `if`, un `for`…).
- `var` tiene ámbito de **función**: se "escapa" de los bloques.

**Hoisting:**
- Las declaraciones `var` se elevan al principio de la función con valor `undefined`, así que usarlas antes de su línea da `undefined`, no un error.
- `let` y `const` también se registran, pero quedan en la **zona muerta temporal** (TDZ): usarlas antes de su línea lanza `ReferenceError`. Es un comportamiento más seguro.

**El clásico de los bucles:** con `var`, todas las vueltas comparten **la misma** variable. Si un `setTimeout` la lee después, ve el valor final. Con `let`, cada vuelta tiene su propia copia.

**Closures:** una función **recuerda** las variables del ámbito donde se creó, aunque ese ámbito ya haya terminado. Sirve para crear estado privado:

`function crearContador() { let n = 0; return () => ++n; }`

Cada llamada a `crearContador()` crea un `n` distinto, al que solo accede la función devuelta.
""",
    example="""
function crearContador(inicio = 0) {
  let cuenta = inicio;
  return {
    sumar: () => ++cuenta,
    valor: () => cuenta,
  };
}

const visitas = crearContador();
visitas.sumar();
visitas.sumar();
console.log(visitas.valor());

for (let i = 0; i < 3; i++) {
  setTimeout(() => console.log("vuelta", i), 0);
}
""",
    exercise="""
Crea `crearMonedero(saldoInicial)`, que devuelva un objeto con `ingresar(x)`, `gastar(x)` y `saldo()`.

El saldo no debe poder modificarse desde fuera, y `gastar` no debe permitir quedarse en negativo.
""",
    starter="function crearMonedero(saldoInicial) {\n  let saldo = saldoInicial;\n  return {\n    // ...\n  };\n}",
    hint="El `let saldo` solo lo ven las funciones del objeto devuelto: es un closure.",
    faq=[
        (
            "¿Por qué existe todavía `var`?",
            "Por compatibilidad con código antiguo. En código nuevo no hay motivo para usarla.",
        ),
        (
            "¿Los closures gastan memoria?",
            "Mantienen vivas las variables que usan mientras la función exista. Casi nunca es un problema; basta con no guardar referencias que ya no necesitas.",
        ),
    ],
    challenge=(
        "Una sola vez",
        3,
        "Escribe `unaVez(fn)`, que devuelva una función que ejecute `fn` solo la **primera** vez que se la llame. Las demás veces devuelve el mismo resultado sin volver a ejecutarla.",
        'function unaVez(fn) {\n  // ...\n}\n\nconst iniciar = unaVez(() => console.log("iniciado"));\niniciar();\niniciar();',
        "Guarda en el closure un booleano `hecho` y el `resultado` de la primera llamada.",
    ),
    questions=[
        cq(
            "js-16",
            QUE,
            "for (var i = 0; i < 3; i++) {\n  setTimeout(() => console.log(i), 0);\n}",
            "3\n3\n3",
            ["0\n1\n2", "2\n2\n2", "3"],
            "Con `var` solo hay **una** `i` compartida. Cuando se ejecutan los setTimeout, el bucle ya ha terminado e `i` vale 3.",
        ),
        cq(
            "js-17",
            QUE,
            "for (let i = 0; i < 3; i++) {\n  setTimeout(() => console.log(i), 0);\n}",
            "0\n1\n2",
            ["3\n3\n3", "1\n2\n3", "0"],
            "Con `let`, cada vuelta del bucle tiene su propia `i`, y cada función recuerda la suya.",
        ),
        cq(
            "js-18",
            QUE,
            "function crearContador() {\n  let n = 0;\n  return () => ++n;\n}\nconst a = crearContador();\nconst b = crearContador();\na();\na();\nconsole.log(a(), b());",
            "3 1",
            ["3 3", "1 1", "2 1"],
            "Cada llamada a `crearContador` crea su propio `n`. `a` ya se ha usado dos veces, así que la tercera da 3; `b` empieza de cero.",
        ),
        cq(
            "js-19",
            OCURRE,
            "console.log(x);\nlet x = 5;",
            "Lanza ReferenceError",
            ["undefined", "5", "null"],
            "`x` está en la zona muerta temporal hasta su declaración: leerla antes lanza `ReferenceError`.",
        ),
        cq(
            "js-20",
            QUE,
            "console.log(y);\nvar y = 5;",
            "undefined",
            ["5", "Lanza ReferenceError", "null"],
            "La declaración `var y` se eleva, pero la asignación `= 5` se queda en su línea: en el console.log, y existe y vale undefined.",
        ),
    ],
    quiz=[
        cq(
            "js-q07",
            QUE,
            "if (true) {\n  let dentro = 1;\n  var fuera = 2;\n}\nconsole.log(typeof dentro, typeof fuera);",
            "undefined number",
            ["number number", "undefined undefined", "Lanza ReferenceError"],
            '`let` no existe fuera del bloque; `var` se escapa. `typeof` de una variable inexistente da "undefined" sin lanzar error.',
        ),
        tq(
            "js-q08",
            "¿Qué es un closure?",
            [
                "Una función que recuerda las variables del ámbito donde se creó",
                "Una función que se cierra sola al terminar",
                "Un bloque try/catch",
                "Una forma de declarar constantes",
            ],
            0,
            "Aunque la función exterior haya terminado, la interior sigue accediendo a sus variables.",
        ),
    ],
    sources=[MDN, JSINFO],
)

# ---------------------------------------------------------------- bloque 3: arrays y objetos

L_ARRAYS = Lesson(
    slug="js-arrays",
    title="Arrays y sus métodos",
    theory="""
Un **array** es una lista ordenada que crece sola: `const notas = [7, 5, 9];`.

**Métodos que modifican el array:** `push` y `pop` (al final), `unshift` y `shift` (al principio), `splice`, `sort` y `reverse`.

**Métodos que devuelven algo nuevo sin tocar el original:**
- `map(fn)`: un array nuevo con el resultado de aplicar `fn` a cada elemento;
- `filter(fn)`: los elementos que cumplen la condición;
- `find(fn)`: el **primero** que la cumple, o `undefined`;
- `some(fn)` y `every(fn)`: si alguno o todos la cumplen;
- `reduce((acumulado, x) => …, inicial)`: reduce el array a un solo valor (suma, máximo, objeto…);
- `includes(x)`, `indexOf(x)`, `slice(i, j)` y `join(", ")`.

**Trampa de `sort()`:** sin argumentos ordena como **texto**. `[10, 9, 1].sort()` da `[1, 10, 9]`. Para números: `sort((a, b) => a - b)`.

**Desestructurar y propagar:**
- `const [primero, segundo] = lista;` saca elementos a variables.
- `[...a, ...b]` une arrays y `[...a]` hace una copia.
- Los arrays son objetos: `const b = a` **no copia**, las dos variables apuntan al mismo array.

Recorrer: `for (const x of lista)` o `lista.forEach(x => …)`.
""",
    example="""
const alumnos = [
  { nombre: "Ana", nota: 8 },
  { nombre: "Luis", nota: 4 },
  { nombre: "Eva", nota: 9 },
];

const aprobados = alumnos.filter((a) => a.nota >= 5).map((a) => a.nombre);
const media = alumnos.reduce((total, a) => total + a.nota, 0) / alumnos.length;

console.log(aprobados.join(", "));
console.log(media.toFixed(2));
console.log([10, 9, 1].sort((a, b) => a - b).join(" "));
""",
    exercise="""
Con `const pedidos = [{ id: 1, total: 30 }, { id: 2, total: 120 }, { id: 3, total: 75 }];`:

1. Obtén los ids de los pedidos de más de 50 €.
2. Calcula el importe total con `reduce`.
3. Ordénalos de mayor a menor total **sin modificar** el array original.
""",
    starter='const pedidos = [{ id: 1, total: 30 }, { id: 2, total: 120 }, { id: 3, total: 75 }];\n\nconst grandes = pedidos.filter(/* ... */).map(/* ... */);\nconsole.log(grandes.join(", "));',
    hint="Para no modificar el original, ordena una copia: `[...pedidos].sort((a, b) => b.total - a.total)`.",
    faq=[
        (
            "¿`forEach` o `map`?",
            "`map` devuelve un array nuevo con los resultados. `forEach` solo recorre, y siempre devuelve undefined: úsalo para efectos (pintar, registrar).",
        ),
        (
            "¿Por qué no sirve `==` para comparar dos arrays?",
            "Compara si son **el mismo objeto**, no su contenido: `[1] === [1]` es false.",
        ),
    ],
    challenge=(
        "Agrupar por ciclo",
        3,
        'Con una lista de alumnos `{ nombre, ciclo }`, construye con `reduce` un objeto `{ DAW: ["Ana", …], DAM: [...] }`.',
        'const alumnos = [{ nombre: "Ana", ciclo: "DAW" }, { nombre: "Luis", ciclo: "DAM" }, { nombre: "Eva", ciclo: "DAW" }];\n\nconst porCiclo = alumnos.reduce((grupos, a) => {\n  // ...\n  return grupos;\n}, {});',
        "Dentro del reduce: `(grupos[a.ciclo] ??= []).push(a.nombre);`.",
    ),
    questions=[
        cq(
            "js-21",
            QUE,
            'const n = [1, 2, 3, 4];\nconsole.log(n.map((x) => x * 2).filter((x) => x > 4).join(","));',
            "6,8",
            ["4,6,8", "2,4,6,8", "3,4"],
            "`map` da [2, 4, 6, 8] y `filter` se queda con los mayores que 4: 6 y 8.",
        ),
        cq(
            "js-22",
            QUE,
            'console.log([10, 9, 1, 100].sort().join(" "));',
            "1 10 100 9",
            ["1 9 10 100", "100 10 9 1", "9 10 100 1"],
            "Sin función de comparación, `sort` ordena como **texto**: \"10\" va antes que \"9\" porque '1' < '9'. Para números: `sort((a, b) => a - b)`.",
        ),
        cq(
            "js-23",
            QUE,
            "const precios = [5, 10, 20];\nconsole.log(precios.reduce((total, p) => total + p, 0));",
            "35",
            ["51020", "0", "Lanza TypeError"],
            "`reduce` parte del valor inicial 0 y va sumando cada precio: 35.",
        ),
        cq(
            "js-24",
            QUE,
            'const u = [\n  { n: "Ana", edad: 20 },\n  { n: "Luis", edad: 17 },\n  { n: "Eva", edad: 30 },\n];\nconsole.log(u.find((x) => x.edad > 18).n, u.filter((x) => x.edad > 18).length);',
            "Ana 2",
            ["Eva 2", "Ana 3", "Ana 1"],
            "`find` devuelve el **primero** que cumple la condición (Ana); `filter` devuelve **todos** (Ana y Eva).",
        ),
        cq(
            "js-25",
            QUE,
            "const [a, , c, ...resto] = [1, 2, 3, 4, 5];\nconsole.log(a, c, resto.length);",
            "1 3 2",
            ["1 2 3", "1 3 3", "1 3 [4, 5]"],
            "El hueco entre comas salta el 2. `...resto` recoge lo que queda (4 y 5): longitud 2.",
        ),
    ],
    quiz=[
        cq(
            "js-q09",
            QUE,
            "const a = [1, 2];\nconst b = a;\nb.push(3);\nconsole.log(a.length);",
            "3",
            ["2", "Lanza TypeError", "undefined"],
            "`b = a` no copia: las dos variables apuntan al mismo array. Para copiar, `[...a]`.",
        ),
        tq(
            "js-q10",
            "¿Qué método devuelve un array nuevo solo con los elementos que cumplen una condición?",
            ["filter", "find", "map", "forEach"],
            0,
            "`find` devuelve solo el primero; `map` transforma todos; `forEach` no devuelve nada.",
        ),
    ],
    sources=[MDN, JSINFO],
)

L_OBJETOS = Lesson(
    slug="js-objetos",
    title="Objetos y JSON",
    theory="""
Un **objeto** agrupa pares clave: valor: `const alumno = { nombre: "Ana", nota: 8 };`.

**Acceso:** `alumno.nombre`, o `alumno["nombre"]` cuando la clave está en una variable. Una propiedad inexistente da `undefined`, pero leer una propiedad **de** `undefined` lanza `TypeError`. El **encadenamiento opcional** `alumno.direccion?.calle` devuelve undefined en lugar de fallar.

**Métodos y `this`:** una función dentro del objeto es un método. `this` es el objeto que la llama (`alumno.saludar()`). Las funciones flecha no tienen su propio `this`: no las uses como métodos.

**Desestructurar:**
- `const { nombre, ciudad = "Madrid" } = alumno;` saca propiedades a variables, con valores por defecto.
- `Object.keys`, `Object.values` y `Object.entries` dan arrays para recorrer un objeto.

**Referencias y copias:**
- Como los arrays, los objetos se asignan **por referencia**, y dos objetos con el mismo contenido no son `===`.
- `{ ...obj }` hace una copia **superficial**: los objetos anidados siguen compartidos.
- Para una copia profunda: `structuredClone(obj)`.

**JSON** es el formato de texto con el que viajan los datos entre el navegador y un servidor:
- `JSON.stringify(obj)` convierte un objeto en texto (se pierden las funciones y los `undefined`);
- `JSON.parse(texto)` convierte el texto en un objeto;
- el JSON exige **comillas dobles** en las claves y en los textos. Si no, `JSON.parse` lanza `SyntaxError`.
""",
    example="""
const pedido = {
  id: 7,
  cliente: { nombre: "Ana", ciudad: "Leganés" },
  lineas: [{ producto: "Teclado", precio: 25 }],
  total() {
    return this.lineas.reduce((t, l) => t + l.precio, 0);
  },
};

const { cliente: { nombre }, id } = pedido;
console.log(id, nombre, pedido.total());
console.log(pedido.envio?.fecha ?? "sin fecha de envío");

const texto = JSON.stringify({ id: pedido.id, total: pedido.total() });
console.log(texto, JSON.parse(texto).total);
""",
    exercise="""
Tienes `const producto = { nombre: "Ratón", precio: 15, etiquetas: ["usb"] };`:

1. Crea una copia con `precio: 12` sin modificar el original.
2. Recorre sus propiedades con `Object.entries` y muestra `clave = valor`.
3. Conviértelo a JSON y de vuelta a objeto.
""",
    starter='const producto = { nombre: "Ratón", precio: 15, etiquetas: ["usb"] };\n\nconst rebajado = { ...producto, /* ... */ };\nfor (const [clave, valor] of Object.entries(rebajado)) {\n  // ...\n}',
    hint="`{ ...producto, precio: 12 }` copia todo y sobrescribe el precio.",
    faq=[
        (
            "¿Objeto o Map?",
            "Para datos con claves fijas (un alumno), objeto. Para diccionarios que cambian mucho, con claves que no son texto o donde importa el orden de inserción, `Map`.",
        ),
        (
            "¿Por qué `JSON.parse` falla con comillas simples?",
            "Porque el formato JSON es más estricto que JavaScript: claves y textos siempre con comillas dobles.",
        ),
    ],
    challenge=(
        "Copia profunda",
        2,
        "Demuestra la diferencia entre `{ ...obj }` y `structuredClone(obj)` modificando un objeto anidado en cada copia.",
        'const original = { nombre: "Ana", notas: { dwec: 7 } };\n\nconst superficial = { ...original };\nconst profunda = structuredClone(original);\n// ...',
        "Cambia `notas.dwec` en cada copia y mira cuál de ellas afecta al original.",
    ),
    questions=[
        cq(
            "js-26",
            QUE,
            'const p = { nombre: "Ana", edad: 20 };\nconst { nombre, ciudad = "Madrid" } = p;\nconsole.log(nombre, ciudad);',
            "Ana Madrid",
            ["Ana undefined", "undefined Madrid", "Lanza TypeError"],
            "`ciudad` no existe en el objeto, así que toma el valor por defecto de la desestructuración.",
        ),
        cq(
            "js-27",
            QUE,
            "const a = { n: 1, datos: { x: 1 } };\nconst b = { ...a };\nb.n = 2;\nb.datos.x = 99;\nconsole.log(a.n, a.datos.x);",
            "1 99",
            ["1 1", "2 99", "2 1"],
            "La propagación hace una copia **superficial**: `n` se copia, pero `datos` sigue siendo el mismo objeto en los dos.",
        ),
        cq(
            "js-28",
            QUE,
            "const texto = JSON.stringify({ a: 1, b: [true, null] });\nconsole.log(texto, typeof texto);",
            '{"a":1,"b":[true,null]} string',
            [
                "{ a: 1, b: [ true, null ] } object",
                "[object Object] string",
                '{"a":1,"b":[true,null]} object',
            ],
            "`JSON.stringify` devuelve un **texto** con claves entre comillas dobles y sin espacios.",
        ),
        cq(
            "js-29",
            OCURRE,
            'const alumno = { nombre: "Eva" };\nconsole.log(alumno.direccion?.calle, alumno.direccion.calle);',
            "Lanza TypeError",
            ["undefined undefined", "undefined", "Lanza ReferenceError"],
            "`alumno.direccion` es undefined. Con `?.` no falla, pero en el segundo acceso se lee `.calle` de undefined: `TypeError`. Los argumentos se evalúan antes de imprimir, así que no se imprime nada.",
        ),
        cq(
            "js-30",
            QUE,
            'const notas = { ana: 8, luis: 5 };\nconsole.log(Object.keys(notas).join("+"), Object.values(notas).reduce((a, b) => a + b));',
            "ana+luis 13",
            ["8+5 13", "ana+luis 85", "ana,luis 13"],
            "`Object.keys` da las claves y `Object.values` los valores, ambos como arrays.",
        ),
    ],
    quiz=[
        cq(
            "js-q11",
            QUE,
            "const a = { x: 1 };\nconst b = { x: 1 };\nconsole.log(a === b, JSON.stringify(a) === JSON.stringify(b));",
            "false true",
            ["true true", "false false", "true false"],
            "Son dos objetos distintos en memoria, aunque su contenido sea igual. Sus textos JSON sí coinciden.",
        ),
        tq(
            "js-q12",
            "¿Qué hace `JSON.parse`?",
            [
                "Convierte un texto JSON en un valor de JavaScript",
                "Convierte un objeto en texto",
                "Valida un formulario",
                "Descarga un archivo JSON",
            ],
            0,
            "Es la operación inversa de `JSON.stringify`.",
        ),
    ],
    sources=[MDN, JSINFO],
)

# ---------------------------------------------------------------- bloque 4: DOM y eventos

L_DOM = Lesson(
    slug="js-dom",
    title="El DOM: leer y cambiar la página",
    theory="""
El **DOM** (*Document Object Model*) es el árbol de objetos que el navegador crea a partir del HTML. Con JavaScript lo lees y lo modificas, y la página cambia al instante.

**Seleccionar elementos:**
- `document.querySelector(".item")`: el **primero** que coincide con el selector CSS, o `null`.
- `document.querySelectorAll(".item")`: **todos**, en una `NodeList`, vacía si no hay ninguno. Se recorre con `forEach` o `for…of`.
- `document.getElementById("menu")`: por id, o `null`.

**Leer y cambiar contenido:**
- `el.textContent = "…"` pone **texto**: es seguro con datos del usuario.
- `el.innerHTML = "…"` interpreta el texto como **HTML**. Con datos del usuario es un riesgo de **XSS**: podrían inyectar scripts.
- Atributos: `el.src`, `el.value`, `el.getAttribute("href")` y `el.dataset.id` (para `data-id`).

**Estilos y clases:** `el.classList.add("activo")`, `remove`, `toggle` y `contains`. Es mejor cambiar clases que tocar `el.style` directamente.

**Crear y quitar:**
- `const li = document.createElement("li"); li.textContent = "Nuevo"; lista.append(li);`
- `el.remove()` quita un elemento.

**¿Cuándo se ejecuta tu script?** Si está en el `<head>` sin `defer`, se ejecuta **antes** de que existan los elementos del `<body>`, y `querySelector` devuelve `null`. Usa `<script src="app.js" defer>` o ponlo al final del body.

Este código solo funciona en el navegador. En la app las preguntas del DOM son de razonar, no de ejecutar.
""",
    example="""
const lista = document.querySelector("#tareas");
const tareas = ["Repasar DOM", "Hacer el ejercicio"];

for (const texto of tareas) {
  const li = document.createElement("li");
  li.textContent = texto;
  li.classList.add("tarea");
  lista.append(li);
}

document.querySelectorAll(".tarea").forEach((li, i) => {
  li.dataset.posicion = String(i + 1);
});
""",
    exercise="""
Con este HTML: `<ul id="notas"></ul>` y el array `const notas = [7, 4, 9];`

1. Crea un `<li>` por nota con el texto `Nota: 7`.
2. Añade la clase `suspenso` a las menores de 5.
3. Escribe debajo un párrafo con la media.
""",
    starter='const ul = document.querySelector("#notas");\nconst notas = [7, 4, 9];\n\nfor (const n of notas) {\n  const li = document.createElement("li");\n  // ...\n}',
    hint='`li.classList.toggle("suspenso", n < 5)` añade o quita la clase según la condición.',
    faq=[
        (
            "¿`append` o `appendChild`?",
            "`append` es más moderno: admite varios nodos y textos. `appendChild` solo un nodo. Los dos añaden al final.",
        ),
        (
            "¿Es mala práctica `innerHTML`?",
            "Para plantillas **tuyas** está bien. Con datos que vienen del usuario o de una API, usa `textContent` o crea los elementos para evitar XSS.",
        ),
    ],
    challenge=(
        "Lista filtrable",
        3,
        "Crea una lista de productos desde un array y un `<input>` que, al escribir, oculte los que no contienen el texto (con una clase `oculto`).",
        'const productos = ["Teclado", "Ratón", "Monitor", "Cable"];\nconst ul = document.querySelector("#productos");\nconst buscador = document.querySelector("#buscar");\n\n// ...',
        'En el evento `input`, recorre los `<li>` y usa `li.classList.toggle("oculto", !li.textContent.toLowerCase().includes(texto))`.',
    ),
    questions=[
        tq(
            "js-31",
            "¿Qué diferencia hay entre `textContent` e `innerHTML`?",
            [
                "`textContent` trata el valor como texto; `innerHTML` lo interpreta como HTML (riesgo de XSS con datos del usuario)",
                "Ninguna, son sinónimos",
                "`innerHTML` solo sirve para leer",
                "`textContent` borra los hijos y `innerHTML` no",
            ],
            0,
            "Si metes con innerHTML un texto escrito por el usuario, podría incluir `<img onerror=…>` y ejecutar código.",
        ),
        tq(
            "js-32",
            'Hay tres elementos con la clase `item`. ¿Qué devuelve `document.querySelector(".item")`?',
            ["El primero de ellos", "Una lista con los tres", "El último", "null"],
            0,
            "`querySelector` devuelve el primer elemento que coincide; para todos existe `querySelectorAll`.",
        ),
        tq(
            "js-33",
            '¿Qué devuelve `document.querySelectorAll(".item")` si no hay ninguno?',
            ["Una NodeList vacía", "null", "undefined", "Lanza un error"],
            0,
            "Por eso recorrerla con `forEach` nunca falla, mientras que `querySelector` sí puede devolver null.",
        ),
        tq(
            "js-34",
            "¿Cómo añades la clase `activo` a un elemento sin quitarle las que ya tiene?",
            [
                '`el.classList.add("activo")`',
                '`el.className = "activo"`',
                '`el.class = "activo"`',
                '`el.style = "activo"`',
            ],
            0,
            "`className =` sustituye todas las clases por una sola.",
        ),
        tq(
            "js-35",
            'Tu script está en el `<head>` y `document.querySelector("#menu")` devuelve null, aunque el menú existe. ¿Causa más probable?',
            [
                "El script se ejecuta antes de que exista el elemento: usa `defer` o ponlo al final del body",
                "El selector correcto es `menu` sin #",
                "querySelector no funciona con ids",
                "Hay que recargar dos veces",
            ],
            0,
            "El navegador ejecuta el script en cuanto lo encuentra. Con `defer` espera a que el HTML esté completo.",
        ),
    ],
    quiz=[
        tq(
            "js-q13",
            '¿Qué devuelve `document.getElementById("no-existe")`?',
            ["null", "undefined", "Una lista vacía", "Lanza un error"],
            0,
            "Por eso conviene comprobarlo, o usar `?.`, antes de acceder a sus propiedades.",
        ),
        tq(
            "js-q14",
            "¿Cuál es la forma correcta de añadir un nuevo `<li>` a una lista?",
            [
                'Crear el elemento con `document.createElement("li")`, darle contenido y hacer `lista.append(li)`',
                '`lista.li = "texto"`',
                '`lista.push("<li>texto</li>")`',
                '`document.write("<li>")`',
            ],
            0,
            "`document.write` está desaconsejado; los elementos se crean y se insertan en el árbol.",
        ),
    ],
    sources=[MDN_DOM, JSINFO],
)

L_EVENTOS = Lesson(
    slug="js-eventos",
    title="Eventos",
    theory="""
Los **eventos** avisan de lo que pasa en la página: `click`, `input`, `submit`, `keydown`, `change`, `DOMContentLoaded`…

`boton.addEventListener("click", manejar)` registra una función que se ejecutará **cada vez** que ocurra el evento. Se pasa la **función**, no su resultado: `manejar`, sin paréntesis.

**El objeto evento** llega como primer parámetro:
- `event.target` es el elemento donde ocurrió;
- `event.currentTarget` es el que tiene el listener;
- `event.key` es la tecla pulsada;
- `event.preventDefault()` cancela la acción por defecto, como enviar el formulario y recargar la página, o seguir un enlace.

**Propagación (burbujeo):** un evento sube desde el elemento pulsado hasta sus antepasados. Si un botón y su `div` tienen listener de click, se ejecuta primero el del botón y después el del div. `event.stopPropagation()` corta la subida.

**Delegación de eventos:** en vez de poner un listener en cada `<li>` (incluidos los que añadas después), pones **uno** en el `<ul>` y miras `event.target` para saber cuál se pulsó.

**Formularios:** escucha `submit` en el `<form>`, no `click` en el botón: así también funciona con Enter. Lee los campos con `input.value` (siempre es texto) o con `new FormData(form)`.
""",
    example="""
const form = document.querySelector("#alta");
const lista = document.querySelector("#alumnos");

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const nombre = form.elements.nombre.value.trim();
  if (!nombre) return;
  const li = document.createElement("li");
  li.textContent = nombre;
  lista.append(li);
  form.reset();
});

lista.addEventListener("click", (event) => {
  if (event.target.matches("li")) event.target.classList.toggle("seleccionado");
});
""",
    exercise="""
Crea un contador con dos botones, `+` y `-`, y un `<span>` que muestre el valor.

- El valor nunca baja de 0.
- Con la tecla `r` se reinicia.
""",
    starter='let valor = 0;\nconst span = document.querySelector("#valor");\n\ndocument.querySelector("#mas").addEventListener("click", () => {\n  // ...\n});',
    hint='Para la tecla, escucha `keydown` en `document` y comprueba `event.key === "r"`.',
    faq=[
        (
            "¿`onclick` o `addEventListener`?",
            '`el.onclick = fn` solo admite una función, porque la siguiente la sustituye. `addEventListener` admite varias y más opciones. Evita `onclick="…"` en el HTML: mezcla JavaScript y marcado.',
        ),
        (
            "¿Cómo quito un listener?",
            "Con `removeEventListener`, pasando **la misma** función. Por eso no funciona con funciones anónimas; si solo quieres que se ejecute una vez, usa `{ once: true }`.",
        ),
    ],
    challenge=(
        "Lista de tareas con delegación",
        3,
        "Lista de tareas en la que cada `<li>` tiene un botón `×`. Con **un solo** listener en el `<ul>`, borra la tarea cuyo botón se pulse, también en las tareas añadidas después.",
        'const ul = document.querySelector("#tareas");\n\nul.addEventListener("click", (event) => {\n  // ...\n});',
        '`event.target.closest("li")` sube hasta el `<li>` que contiene el botón pulsado.',
    ),
    questions=[
        tq(
            "js-36",
            "¿Cómo se registra correctamente una función `saludar` para el click de un botón?",
            [
                '`boton.addEventListener("click", saludar)`',
                '`boton.addEventListener("click", saludar())`',
                "`boton.click = saludar`",
                '`boton.addEventListener(saludar, "click")`',
            ],
            0,
            "Se pasa la función sin llamarla; el navegador la llamará en cada click.",
        ),
        tq(
            "js-37",
            '¿Qué problema tiene `boton.addEventListener("click", saludar());`?',
            [
                "Ejecuta `saludar` al instante y registra su resultado (undefined), no la función",
                "Ninguno, es equivalente",
                "Solo funciona una vez",
                "Da un error de sintaxis",
            ],
            0,
            'Los paréntesis **llaman** a la función. Si necesitas pasarle argumentos: `() => saludar("Ana")`.',
        ),
        tq(
            "js-38",
            "Al enviar un formulario, la página se recarga y pierdes lo que hace tu código. ¿Qué falta?",
            [
                "`event.preventDefault()` en el listener de `submit`",
                "`event.stopPropagation()`",
                'Poner `type="button"` en todos los campos',
                "Un `return true`",
            ],
            0,
            "`preventDefault` cancela la acción por defecto del navegador, que es enviar el formulario y recargar.",
        ),
        tq(
            "js-39",
            "Haces click en un `<button>` que está dentro de un `<div>`, y ambos tienen listener de click. ¿Qué ocurre?",
            [
                "Se ejecuta primero el del botón y después el del div (burbujeo)",
                "Solo el del botón",
                "Solo el del div",
                "Primero el del div",
            ],
            0,
            "Los eventos suben por el árbol. `stopPropagation()` lo evitaría.",
        ),
        tq(
            "js-40",
            "¿Qué es la delegación de eventos?",
            [
                "Poner un único listener en el contenedor y usar `event.target` para saber qué hijo se pulsó",
                "Pasar un evento a otra función",
                "Ejecutar un evento más tarde",
                "Copiar un listener en cada elemento",
            ],
            0,
            "Funciona también con los elementos que se añaden después y ahorra listeners.",
        ),
    ],
    quiz=[
        tq(
            "js-q15",
            "Dentro de un listener puesto en un `<ul>`, ¿qué es `event.target` si se pulsa un `<li>`?",
            ["El `<li>` pulsado", "El `<ul>`", "El documento", "La función del listener"],
            0,
            "`event.currentTarget` sería el `<ul>`, que es quien tiene el listener.",
        ),
        tq(
            "js-q16",
            "¿Por qué es mejor escuchar `submit` en el formulario que `click` en su botón?",
            [
                "Porque también se dispara al pulsar Enter en un campo",
                "Porque click no funciona en botones",
                "Porque submit es más rápido",
                "No hay diferencia",
            ],
            0,
            "El formulario se envía de varias formas; `submit` las recoge todas.",
        ),
    ],
    sources=[MDN_DOM, JSINFO],
)

# ---------------------------------------------------------------- bloque 5: asincronía

L_ASYNC = Lesson(
    slug="js-asincronia",
    title="Asincronía: event loop, promesas y async/await",
    theory="""
JavaScript ejecuta **un solo hilo**. Las tareas lentas (temporizadores, peticiones de red) no bloquean: se programan y su **callback** se ejecuta más tarde, cuando el hilo queda libre. El mecanismo que lo gestiona es el **event loop**.

**Orden de ejecución:**
1. Todo el código síncrono actual.
2. Las **microtareas**: los `then` de las promesas y lo que sigue a un `await`.
3. Las **tareas**, como los `setTimeout`, aunque sean de 0 ms.

Por eso `setTimeout(fn, 0)` nunca se ejecuta "ya", sino cuando termina lo demás.

**Promesas:** un objeto que representa un resultado futuro. Está pendiente y acaba **cumplida** (`then`) o **rechazada** (`catch`). `Promise.all([...])` espera a varias a la vez.

**async/await:**
- Una función `async` **siempre devuelve una promesa**.
- Dentro de ella, `await promesa` pausa **esa función** (no el programa) hasta que la promesa se resuelve, y da su valor.
- Los errores se capturan con `try/catch`, como en el código síncrono.
- Si nadie captura un rechazo, el error queda sin tratar (*unhandled rejection*).
""",
    example="""
const esperar = (ms) => new Promise((resolver) => setTimeout(resolver, ms));

async function cargarAlumnos() {
  await esperar(50);
  return ["Ana", "Luis"];
}

async function main() {
  console.log("Cargando...");
  const alumnos = await cargarAlumnos();
  console.log(`Cargados: ${alumnos.join(", ")}`);
}

main();
console.log("La interfaz sigue respondiendo");
""",
    exercise="""
Escribe `async function cronometro(n)`, que muestre `3`, `2`, `1` y `¡Ya!` con un segundo de pausa entre cada número, usando una función `esperar(ms)` basada en promesas.
""",
    starter="const esperar = (ms) => new Promise((r) => setTimeout(r, ms));\n\nasync function cronometro(n) {\n  for (let i = n; i > 0; i--) {\n    // ...\n  }\n}\n\ncronometro(3);",
    hint="Dentro del bucle: `console.log(i); await esperar(1000);`.",
    faq=[
        (
            "¿`await` bloquea la página?",
            "No: pausa solo la función async en la que está. El resto del programa y la interfaz siguen funcionando.",
        ),
        (
            "¿`then` o `await`?",
            "Hacen lo mismo. `await` se lee como código secuencial y facilita el try/catch; `then` es útil en cadenas cortas.",
        ),
    ],
    challenge=(
        "En paralelo",
        2,
        "Simula tres peticiones con `esperar` de 300, 100 y 200 ms. Espera a las tres con `Promise.all` y mide el tiempo total con `Date.now()`: ¿es la suma o el máximo?",
        "const esperar = (ms, valor) => new Promise((r) => setTimeout(() => r(valor), ms));\n\nasync function main() {\n  const inicio = Date.now();\n  // const resultados = await Promise.all([...]);\n  console.log(Date.now() - inicio);\n}\n\nmain();",
        "`Promise.all` lanza todas a la vez: tarda lo que la más lenta, unos 300 ms.",
    ),
    questions=[
        cq(
            "js-41",
            QUE,
            'console.log("A");\nsetTimeout(() => console.log("B"), 0);\nconsole.log("C");',
            "A\nC\nB",
            ["A\nB\nC", "B\nA\nC", "C\nA\nB"],
            "El setTimeout, aunque sea de 0 ms, se ejecuta cuando termina todo el código síncrono.",
        ),
        cq(
            "js-42",
            QUE,
            'setTimeout(() => console.log("timeout"), 0);\nPromise.resolve().then(() => console.log("promesa"));\nconsole.log("sincrono");',
            "sincrono\npromesa\ntimeout",
            [
                "sincrono\ntimeout\npromesa",
                "promesa\nsincrono\ntimeout",
                "timeout\npromesa\nsincrono",
            ],
            "Primero el código síncrono; después las **microtareas** (el then de la promesa) y por último las tareas como setTimeout.",
        ),
        cq(
            "js-43",
            QUE,
            "async function f() {\n  return 5;\n}\nconsole.log(typeof f());\nf().then((v) => console.log(v));",
            "object\n5",
            ["number\n5", "5\n5", "object\nundefined"],
            "Una función async **siempre** devuelve una promesa (un objeto). El 5 se obtiene con `then` o con `await`.",
        ),
        cq(
            "js-44",
            QUE,
            "const esperar = (ms) => new Promise((r) => setTimeout(r, ms));\n\nasync function main() {\n  console.log(1);\n  await esperar(10);\n  console.log(2);\n}\n\nmain();\nconsole.log(3);",
            "1\n3\n2",
            ["1\n2\n3", "3\n1\n2", "1\n3"],
            "`main` imprime 1 y se pausa en el await. Mientras tanto, el resto del programa imprime 3. Al terminar la espera, main continúa e imprime 2.",
        ),
        cq(
            "js-45",
            QUE,
            'async function cargar() {\n  throw new Error("sin red");\n}\ncargar().catch((e) => console.log("Fallo:", e.message));\nconsole.log("sigue");',
            "sigue\nFallo: sin red",
            ["Fallo: sin red\nsigue", "Lanza Error", "sigue"],
            "El error de una función async rechaza su promesa y el `catch` lo trata, pero de forma asíncrona: después del código síncrono.",
        ),
    ],
    quiz=[
        cq(
            "js-q17",
            QUE,
            'Promise.all([Promise.resolve(1), 2, Promise.resolve(3)])\n  .then((valores) => console.log(valores.join("-")));',
            "1-2-3",
            ["1-3", "Lanza TypeError", "3-2-1"],
            "`Promise.all` espera a todas y mantiene el orden. Los valores que no son promesas se tratan como ya resueltos.",
        ),
        tq(
            "js-q18",
            "¿Qué hace `await` dentro de una función async?",
            [
                "Pausa esa función hasta que la promesa se resuelve y devuelve su valor",
                "Bloquea todo el programa",
                "Convierte una función en síncrona",
                "Repite la promesa hasta que funcione",
            ],
            0,
            "Solo se pausa la función; el event loop sigue atendiendo lo demás.",
        ),
    ],
    sources=[MDN, JSINFO],
)

L_FETCH = Lesson(
    slug="js-fetch-json",
    title="fetch y JSON",
    theory="""
`fetch(url)` hace peticiones HTTP desde el navegador y devuelve una **promesa** de una `Response`.

```
const respuesta = await fetch("/api/alumnos");
if (!respuesta.ok) throw new Error(`HTTP ${respuesta.status}`);
const alumnos = await respuesta.json();
```

**Dos `await`:** uno espera la respuesta y otro lee y convierte el cuerpo (`json()`, `text()`), que también es asíncrono.

**Trampa importante:** `fetch` **no** rechaza la promesa por un 404 o un 500. Solo falla por errores de **red** (sin conexión, CORS). Hay que comprobar `respuesta.ok`, que es cierto con los códigos 200-299, o `respuesta.status`.

**Enviar datos (POST):**

```
await fetch("/api/alumnos", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ nombre: "Ana" }),
});
```

**JSON al recibir:** los números que vienen como texto (`"12"`) siguen siendo texto: conviértelos con `Number`. Un JSON mal formado hace que `JSON.parse` o `respuesta.json()` lancen `SyntaxError`.

**Manejo de errores:** envuelve las peticiones en `try/catch/finally`. En el `catch` muestra un mensaje al usuario; en el `finally`, quita el indicador de carga.

**CORS:** el navegador bloquea las peticiones a otro dominio salvo que el servidor lo permita con sus cabeceras. Es una protección del navegador, no un fallo de tu código.
""",
    example="""
async function cargarUsuario(id) {
  const estado = document.querySelector("#estado");
  estado.textContent = "Cargando...";
  try {
    const respuesta = await fetch(`https://jsonplaceholder.typicode.com/users/${id}`);
    if (!respuesta.ok) throw new Error(`HTTP ${respuesta.status}`);
    const usuario = await respuesta.json();
    estado.textContent = `Hola, ${usuario.name}`;
  } catch (error) {
    estado.textContent = `No se pudo cargar: ${error.message}`;
  } finally {
    document.querySelector("#spinner").hidden = true;
  }
}

cargarUsuario(1);
""",
    exercise="""
Escribe `async function buscarPais(nombre)`, que pida `https://restcountries.com/v3.1/name/${nombre}` y muestre su capital y su población.

- Si la respuesta no es `ok`, muestra "País no encontrado".
- Si falla la red, "Sin conexión".
""",
    starter="async function buscarPais(nombre) {\n  try {\n    const respuesta = await fetch(`https://restcountries.com/v3.1/name/${nombre}`);\n    // ...\n  } catch (error) {\n    // ...\n  }\n}",
    hint="El resultado es un array: `const [pais] = await respuesta.json();` y después `pais.capital[0]` y `pais.population`.",
    faq=[
        (
            "¿`fetch` o `XMLHttpRequest`/jQuery?",
            "`fetch` es el estándar actual en todos los navegadores. XMLHttpRequest es la API antigua y jQuery.ajax, una capa sobre ella.",
        ),
        (
            "¿Por qué me da error de CORS si en Postman funciona?",
            "CORS lo aplica el **navegador** para protegerte. Postman no es un navegador. Lo soluciona el servidor, con la cabecera `Access-Control-Allow-Origin`.",
        ),
    ],
    challenge=(
        "Reintentos",
        3,
        "Escribe `fetchConReintentos(url, intentos = 3)`, que repita la petición si falla (por red o por un 5xx), esperando un poco más cada vez.",
        "async function fetchConReintentos(url, intentos = 3) {\n  for (let i = 1; i <= intentos; i++) {\n    try {\n      // ...\n    } catch (error) {\n      // ...\n    }\n  }\n}",
        "Si `respuesta.status >= 500`, lanza un error para que el catch lo trate como fallo; en el último intento, vuelve a lanzarlo.",
    ),
    questions=[
        cq(
            "js-46",
            QUE,
            'const datos = JSON.parse(\'{"precio": "12", "stock": 3}\');\nconsole.log(datos.precio + datos.stock);',
            "123",
            ["15", "Lanza SyntaxError", "NaN"],
            '`precio` llega como **texto** "12" y `+` concatena: "123". Hay que convertir: `Number(datos.precio)`.',
        ),
        cq(
            "js-47",
            OCURRE,
            "console.log(JSON.parse(\"{nombre: 'Ana'}\").nombre);",
            "Lanza SyntaxError",
            ["Ana", "undefined", "Lanza TypeError"],
            "Es un objeto válido en JavaScript, pero no es JSON válido: JSON exige comillas dobles en claves y textos.",
        ),
        tq(
            "js-48",
            "El servidor responde con un 404. ¿Qué hace la promesa de `fetch`?",
            [
                "Se cumple igualmente: hay que comprobar `respuesta.ok` o `respuesta.status`",
                "Se rechaza y salta el catch",
                "Queda pendiente para siempre",
                "Devuelve null",
            ],
            0,
            "`fetch` solo rechaza por errores de red. Un 404 es una respuesta válida del servidor.",
        ),
        tq(
            "js-49",
            "¿Por qué hace falta `await respuesta.json()`?",
            [
                "Porque leer y convertir el cuerpo de la respuesta también es asíncrono y devuelve una promesa",
                "No hace falta, `respuesta` ya es el objeto",
                "Para convertir el objeto en texto",
                "Para reintentar la petición",
            ],
            0,
            "El cuerpo puede llegar en trozos; `json()` espera a tenerlo entero y lo convierte.",
        ),
        cq(
            "js-50",
            QUE,
            'async function obtener(ok) {\n  if (!ok) throw new Error("HTTP 500");\n  return { nombre: "Ana" };\n}\n\nasync function main() {\n  try {\n    const a = await obtener(true);\n    console.log(a.nombre);\n    await obtener(false);\n    console.log("no llega");\n  } catch (e) {\n    console.log(e.message);\n  } finally {\n    console.log("fin");\n  }\n}\n\nmain();',
            "Ana\nHTTP 500\nfin",
            ["Ana\nno llega\nfin", "HTTP 500\nfin", "Ana\nHTTP 500"],
            'El `await` de una promesa rechazada lanza el error dentro del try: salta al catch sin ejecutar "no llega" y termina con el finally.',
        ),
    ],
    quiz=[
        cq(
            "js-q19",
            QUE,
            "console.log(JSON.stringify({ a: 1, b: undefined, c: () => 1 }));",
            '{"a":1}',
            ['{"a":1,"b":undefined}', '{"a":1,"b":null,"c":null}', "Lanza TypeError"],
            "JSON no tiene undefined ni funciones: `stringify` omite esas propiedades.",
        ),
        tq(
            "js-q20",
            "Al enviar un objeto en un POST con `fetch`, ¿qué cabecera indica que el cuerpo es JSON?",
            [
                "`Content-Type: application/json`",
                "`Accept: text/html`",
                "`Authorization: JSON`",
                "`Content-Length: json`",
            ],
            0,
            "Y el cuerpo se envía como texto con `JSON.stringify`.",
        ),
    ],
    sources=[MDN, JSINFO],
)

BLOCKS = [
    Block(
        "js-fundamentos",
        "Fundamentos",
        "Variables, tipos, comparaciones y conversiones.",
        20,
        [L_VARIABLES, L_COERCION],
    ),
    Block(
        "js-funciones",
        "Funciones y ámbito",
        "Funciones, flechas, hoisting y closures.",
        20,
        [L_FUNCIONES, L_AMBITO],
    ),
    Block(
        "js-datos",
        "Arrays y objetos",
        "Métodos de arrays, objetos, desestructuración y JSON.",
        25,
        [L_ARRAYS, L_OBJETOS],
    ),
    Block(
        "js-dom",
        "DOM y eventos",
        "Seleccionar y modificar la página y reaccionar al usuario.",
        20,
        [L_DOM, L_EVENTOS],
    ),
    Block(
        "js-asincronia",
        "Asincronía",
        "Event loop, promesas, async/await y fetch.",
        15,
        [L_ASYNC, L_FETCH],
    ),
]

if __name__ == "__main__":
    main("js", BLOCKS, run_js, check_example)
