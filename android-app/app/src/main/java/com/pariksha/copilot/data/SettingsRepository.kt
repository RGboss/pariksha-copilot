package com.pariksha.copilot.data

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "pariksha_settings")

class SettingsRepository(private val context: Context) {

    companion object {
        val API_KEY = stringPreferencesKey("gemini_api_key")
        val SELECTED_MODEL = stringPreferencesKey("selected_model")
        val USER_NAME = stringPreferencesKey("user_name")
        val USER_EMAIL = stringPreferencesKey("user_email")
        val TARGET_EXAM = stringPreferencesKey("target_exam")
        val AUTH_TOKEN = stringPreferencesKey("auth_token")
        val IS_LOGGED_IN = booleanPreferencesKey("is_logged_in")
        val STREAK_DAYS = intPreferencesKey("streak_days")
        val DAILY_HOURS = intPreferencesKey("daily_hours")
    }

    val apiKey: Flow<String> = context.dataStore.data.map { prefs ->
        prefs[API_KEY] ?: ""
    }

    val selectedModel: Flow<String> = context.dataStore.data.map { prefs ->
        prefs[SELECTED_MODEL] ?: "gemini-2.5-flash"
    }

    val userName: Flow<String> = context.dataStore.data.map { prefs ->
        prefs[USER_NAME] ?: ""
    }

    val userEmail: Flow<String> = context.dataStore.data.map { prefs ->
        prefs[USER_EMAIL] ?: ""
    }

    val targetExam: Flow<String> = context.dataStore.data.map { prefs ->
        prefs[TARGET_EXAM] ?: "SEBI Grade A (IT Stream)"
    }

    val authToken: Flow<String> = context.dataStore.data.map { prefs ->
        prefs[AUTH_TOKEN] ?: ""
    }

    val isLoggedIn: Flow<Boolean> = context.dataStore.data.map { prefs ->
        prefs[IS_LOGGED_IN] ?: false
    }

    val streakDays: Flow<Int> = context.dataStore.data.map { prefs ->
        prefs[STREAK_DAYS] ?: 7
    }

    val dailyHours: Flow<Int> = context.dataStore.data.map { prefs ->
        prefs[DAILY_HOURS] ?: 5
    }

    suspend fun saveAuthSession(name: String, email: String, exam: String, token: String) {
        context.dataStore.edit { prefs ->
            prefs[USER_NAME] = name
            prefs[USER_EMAIL] = email
            prefs[TARGET_EXAM] = exam
            prefs[AUTH_TOKEN] = token
            prefs[IS_LOGGED_IN] = true
        }
    }

    suspend fun logout() {
        context.dataStore.edit { prefs ->
            prefs[IS_LOGGED_IN] = false
            prefs[AUTH_TOKEN] = ""
        }
    }

    suspend fun saveApiKey(key: String) {
        context.dataStore.edit { prefs ->
            prefs[API_KEY] = key
        }
    }

    suspend fun clearApiKey() {
        context.dataStore.edit { prefs ->
            prefs.remove(API_KEY)
        }
    }

    suspend fun saveSelectedModel(model: String) {
        context.dataStore.edit { prefs ->
            prefs[SELECTED_MODEL] = model
        }
    }

    suspend fun saveTargetExam(exam: String) {
        context.dataStore.edit { prefs ->
            prefs[TARGET_EXAM] = exam
        }
    }

    suspend fun saveUserName(name: String) {
        context.dataStore.edit { prefs ->
            prefs[USER_NAME] = name
        }
    }

    suspend fun saveUserProfile(name: String, exam: String, hours: Int) {
        context.dataStore.edit { prefs ->
            prefs[USER_NAME] = name
            prefs[TARGET_EXAM] = exam
            prefs[DAILY_HOURS] = hours
        }
    }
}
