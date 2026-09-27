package io.github.marbi8891.pld.pcap

import org.json.JSONObject

/** Lo que la zona PCAP necesita del temario (`frontend/data/lessons.json`): títulos y lecciones de cada módulo. */
data class LessonIndex(val titles: Map<String, String>, val modules: Map<String, List<String>>) {
    companion object {
        fun parse(json: String): LessonIndex {
            val titles = linkedMapOf<String, String>()
            val modules = linkedMapOf<String, List<String>>()
            JSONObject(json).getJSONArray("modules").objects().forEach { module ->
                val lessons = module.getJSONArray("lessons").objects()
                lessons.forEach { titles[it.getString("slug")] = it.getString("title") }
                modules[module.getString("slug")] = lessons.map { it.getString("slug") }
            }
            return LessonIndex(titles, modules)
        }
    }
}
