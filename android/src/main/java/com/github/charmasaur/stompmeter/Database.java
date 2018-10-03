package com.github.charmasaur.stompmeter;

import android.content.Context;
import android.content.SharedPreferences;

public final class Database {
  private static final String PREFS_NAME = "prefs";

  private static final String REGISTRATION_STATUS_KEY = "rs";
  private static final String ACTIVITY_KEY_PREFIX = "at_";

  public enum RegistrationStatus {
    UNKNOWN,
    PENDING,
    SUCCEEDED,
    FAILED,
  }

  public enum Activity {
    UNKNOWN,
    WALKING,
    CYCLING,
    RUNNING,
  }

  private final SharedPreferences sharedPreferences;

  public Database(Context context) {
    sharedPreferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
  }

  public void reset() {
    sharedPreferences.edit().clear().apply();
  }

  public void setRegistrationStatus(RegistrationStatus registrationStatus) {
    sharedPreferences.edit().putString(REGISTRATION_STATUS_KEY, registrationStatus.name()).apply();
  }

  public RegistrationStatus getRegistrationStatus() {
    String name = sharedPreferences.getString(REGISTRATION_STATUS_KEY, "");
    try {
      return Enum.valueOf(RegistrationStatus.class, name);
    } catch (IllegalArgumentException e) {
      return RegistrationStatus.UNKNOWN;
    }
  }

  public void setActivityStart(Activity activity, long startTimeMs) {
    sharedPreferences.edit().putLong(getActivityKey(activity), startTimeMs).apply();
  }

  /** Returns the time in ms since epoch, or 0 if not set. */
  public long getActivityStart(Activity activity) {
    return sharedPreferences.getLong(getActivityKey(activity), 0);
  }

  /** Returns a reliable string key for the given activity. */
  public static String getActivityKey(Activity activity) {
    return ACTIVITY_KEY_PREFIX + activity.name();
  }
}
