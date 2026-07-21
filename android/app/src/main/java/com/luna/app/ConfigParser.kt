package com.luna.app

import org.json.JSONArray
import org.json.JSONObject

data class LunaKey(
    val label: String,
    val keyCode: Int,
    val mods: Int,
    val icon: String = "",
    val sound: String = ""
)

data class LunaProfile(
    val name: String,
    val cols: Int,
    val keys: List<LunaKey>
)

data class AppSwitchRule(
    val exe: String,
    val profile: String,
    val label: String = ""
)

data class LunaConfig(
    val profiles: Map<String, LunaProfile>,
    val activeProfile: String,
    val appSwitchRules: List<AppSwitchRule>
)

object ConfigParser {
    fun parse(json: String): LunaConfig {
        val root = JSONObject(json)
        val perfilesObj = root.getJSONObject("perfiles")
        val profiles = mutableMapOf<String, LunaProfile>()
        val names = perfilesObj.names()
        if (names != null) {
            for (i in 0 until names.length()) {
                val name = names.getString(i)
                val p = perfilesObj.getJSONObject(name)
                val cols = p.optInt("cols", 4)
                val keysArr = p.optJSONArray("keys")
                val keys = mutableListOf<LunaKey>()
                if (keysArr != null) {
                    for (j in 0 until keysArr.length()) {
                        val k = keysArr.getJSONObject(j)
                        keys.add(LunaKey(
                            label = k.optString("label", ""),
                            keyCode = k.optInt("keyCode", 0),
                            mods = k.optInt("mods", 0),
                            icon = k.optString("icon", ""),
                            sound = k.optString("sound", "")
                        ))
                    }
                }
                profiles[name] = LunaProfile(name, cols, keys)
            }
        }
        val activeProfile = root.optString("perfil_activo", "")
        val appSwitchArr = root.optJSONObject("appSwitch")?.optJSONArray("rules")
        val rules = mutableListOf<AppSwitchRule>()
        if (appSwitchArr != null) {
            for (i in 0 until appSwitchArr.length()) {
                val r = appSwitchArr.getJSONObject(i)
                rules.add(AppSwitchRule(
                    exe = r.optString("exe", ""),
                    profile = r.optString("profile", ""),
                    label = r.optString("label", "")
                ))
            }
        }
        return LunaConfig(profiles, activeProfile, rules)
    }
}
