from video_factory.subtitles import cues_from_timeline, to_vtt, validate_vtt
from video_factory.text import (
    bold_terms,
    split_cue,
    split_sentences,
    strip_markdown,
    wrap_two_lines,
)


def test_markdown_becomes_speakable_text():
    text = "Una **variable** usa `snake_case`.\n\n- Punto uno\n- [Enlace](https://x.y)"
    assert strip_markdown(text) == "Una variable usa snake_case. Punto uno. Enlace."
    assert bold_terms("La **clave** y la **Clave** y el **valor**:") == ["clave", "valor"]


def test_sentences_keep_decimals_and_abbreviations_together():
    text = "Vale 3.5 euros, p. ej. en Madrid. ¿Lo ves? Sí."
    assert split_sentences(text) == ["Vale 3.5 euros, p. ej. en Madrid.", "¿Lo ves?", "Sí."]


def test_long_sentences_are_split_into_readable_cues():
    sentence = (
        "Para combinar texto y variables, usa una f-string: una f delante de las comillas "
        "y las variables entre llaves."
    )
    chunks = split_cue(sentence)
    assert " ".join(chunks) == sentence
    assert all(len(chunk) <= 84 for chunk in chunks)
    assert all(len(line) <= 42 for chunk in chunks for line in wrap_two_lines(chunk).split("\n"))


def _timeline():
    return {
        "duration": 12.0,
        "scenes": [
            {
                "id": "s1",
                "start": 0.0,
                "duration": 12.0,
                "sentences": [
                    {"text": "Hola.", "start": 0.4, "end": 1.0},
                    {
                        "text": "En esta lección vas a aprender a guardar datos en variables "
                        "y a mostrarlos en la consola con print.",
                        "start": 1.4,
                        "end": 8.0,
                    },
                ],
            }
        ],
    }


def test_cues_follow_the_narration_without_overlapping():
    cues = cues_from_timeline(_timeline())
    assert cues[0] == (0.4, 1.0, "Hola.")
    assert cues[1][0] == 1.4 and cues[-1][1] == 8.0
    assert all(first[1] <= second[0] for first, second in zip(cues, cues[1:], strict=False))


def test_generated_vtt_is_valid():
    assert validate_vtt(to_vtt(_timeline()), duration=12.0) == []


def test_invalid_vtt_is_detected():
    assert validate_vtt("hola") == ["El archivo no empieza por WEBVTT"]
    overlapping = (
        "WEBVTT\n\n1\n00:00:01.000 --> 00:00:03.000\nUno\n\n2\n00:00:02.000 --> 00:00:04.000\nDos\n"
    )
    assert any("solapa" in problem for problem in validate_vtt(overlapping))
    late = "WEBVTT\n\n1\n00:00:01.000 --> 00:00:09.000\nUno\n"
    assert any("después del vídeo" in problem for problem in validate_vtt(late, duration=5))
    assert validate_vtt("WEBVTT\n") == ["No hay ningún subtítulo"]
    assert any("mal escrito" in p for p in validate_vtt("WEBVTT\n\n1\n0:1 --> 0:2\nUno\n"))
