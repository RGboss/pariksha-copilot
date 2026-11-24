package com.pariksha.copilot.data

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "pariksha_settings")

class SettingsRepository(private val context: Context) {

    companion object {
        val API_KEY = stringPreferencesKey("gemini_api_key")
        val SERVER_URL = stringPreferencesKey("server_url")
        val SELECTED_MODEL = stringPreferencesKey("selected_model")
        val USER_NAME = stringPreferencesKey("user_name")
        val TARGET_EXAM = stringPreferencesKey("target_exam")
    }

    val apiKey: Flow<String> = context.dataStore.data.map { prefs ->
        prefs[API_KEY] ?: ""
    }

    val serverUrl: Flow<String> = context.dataStore.data.map { prefs ->
        prefs[SERVER_URL] ?: "http://192.168.29.94:8000"
    }

    val selectedModel: Flow<String> = context.dataStore.data.map { prefs ->
        prefs[SELECTED_MODEL] ?: "gemini-2.5-flash"
    }

    val userName: Flow<String> = context.dataStore.data.map { prefs ->
        prefs[USER_NAME] ?: ""
    }

    val targetExam: Flow<String> = context.dataStore.data.map { prefs ->
        prefs[TARGET_EXAM] ?: "SEBI Grade A (IT Stream)"
    }

    suspend fun saveApiKey(key: String) {
        context.dataStore.data
        context.dataStore.edit { prefs ->
            prefs[API_KEY] = key
        }
    }

    suspend fun clearApiKey() {
        context.dataStore.edit { prefs ->
            prefs.remove(API_KEY)
        }
    }

    suspend fun saveServerUrl(url: String) {
        context.dataStore.edit { prefs ->
            prefs[SERVER_URL] = url
        }
    }

    suspend fun saveSelectedModel(model: String) {
        context.dataStore.edit { prefs ->
            prefs[SELECTED_MODEL] = model
        }
    }

    suspend fun saveUserName(name: String) {
        context.dataStore.edit { prefs ->
            prefs[USER_NAME] = name
        }
    }

    suspend fun saveTargetExam(exam: String) {
        context.dataStore.edit { prefs ->
            prefs[TARGET_EXAM] = exam
        }
    }
}
