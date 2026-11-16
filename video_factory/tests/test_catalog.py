"""El catálogo sale del temario real: ni una lección inventada, ni una duplicada."""

import json

from video_factory.catalog import build_catalog, load_sources
from video_factory.config import DATA, PRODUCTION
from video_factory.models import Catalog


def test_every_entry_comes_from_a_real_lesson():
    pcap = json.loads((DATA / "lessons.json").read_text(encoding="utf-8"))
    slugs = {lesson["slug"] for module in pcap["modules"] for lesson in module["lessons"]}
    catalog = build_catalog()
    pcap_ids = {entry.id for entry in catalog.lessons if entry.family == "pcap"}
    assert pcap_ids == {f"pcap-{slug}" for slug in slugs}
    for entry in catalog.lessons:
        assert entry.lesson and entry.objective and entry.code, entry.id
        assert "TitleScene" in entry.animations and "SummaryScene" in entry.animations


def test_ids_are_unique_and_families_complete():
    catalog = build_catalog()
    ids = [entry.id for entry in catalog.lessons]
    assert len(ids) == len(set(ids))
    assert {entry.family for entry in catalog.lessons} == {"learn", "pcap", "daw"}


def test_concepts_without_own_theory_reuse_the_pcap_video():
    learning = json.loads((DATA / "learning.json").read_text(encoding="utf-8"))
    catalog = build_catalog()
    ids = {entry.id for entry in catalog.lessons}
    covered = {concept for entry in catalog.lessons for concept in entry.also_covers}
    for concept in learning["concepts"]:
        has_video = f"learn-{concept['id']}" in ids
        assert has_video != (concept["id"] in covered), concept["id"]


def test_rebuilding_keeps_production_status():
    first = build_catalog()
    first.lessons[0].status = "rendered"
    again = build_catalog(first)
    assert again.lessons[0].status == "rendered"
    assert again.lessons[1].status == "pending"


def test_committed_catalog_is_up_to_date():
    """Como el resto de JSON generados: si cambia el temario, se regenera con `inventory`."""
    saved = Catalog.model_validate_json((PRODUCTION / "catalog.json").read_text(encoding="utf-8"))
    fresh = build_catalog(saved)
    assert saved.model_dump() == fresh.model_dump()


def test_python_topics_get_their_component():
    sources = load_sources()
    from video_factory.catalog import animations_for

    assert "VariableScene" in animations_for(sources["pcap-variables"])
    assert "LoopScene" in animations_for(sources["pcap-bucles"])
    assert "VariableScene" not in animations_for(sources["daw-js-js-variables"])
