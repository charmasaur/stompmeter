package com.github.charmasaur.stompmeter;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.SystemClock;
import android.util.Log;
import com.google.android.gms.location.ActivityTransition;
import com.google.android.gms.location.ActivityTransitionEvent;
import com.google.android.gms.location.ActivityTransitionResult;
import com.google.android.gms.location.DetectedActivity;
import java.util.concurrent.TimeUnit;

public final class ActivityTransitionReceiver extends BroadcastReceiver {
  private static final String TAG = ActivityTransitionReceiver.class.getSimpleName();

  @Override
  public void onReceive(Context context, Intent intent) {
    Log.i(TAG, "onReceive: " + intent.getAction());

    Database database = new Database(context);
    NotificationPoster notificationPoster = new NotificationPoster(context);

    ActivityTransitionResult result = ActivityTransitionResult.extractResult(intent);
    for (ActivityTransitionEvent event : result.getTransitionEvents()) {
      Database.Activity activity = getActivityForGmsActivity(event.getActivityType());
      long timeMs = TimeUnit.NANOSECONDS.toMillis(event.getElapsedRealTimeNanos());
      if (event.getTransitionType() == ActivityTransition.ACTIVITY_TRANSITION_ENTER) {
        database.setActivityStart(activity, timeMs);
        continue;
      }
      if (event.getTransitionType() == ActivityTransition.ACTIVITY_TRANSITION_EXIT) {
        long startTimeMs = database.getActivityStart(activity);
        if (startTimeMs == 0) {
          Log.e(
              TAG,
              "Activity stopped but wasn't started: " + activity + ", " + event.getActivityType());
          continue;
        }
        long startTimestampMs =
            startTimeMs + System.currentTimeMillis() - SystemClock.elapsedRealtime();
        notificationPoster.postNotification(activity, timeMs - startTimeMs, startTimestampMs);
        continue;
      }
    }
  }

  private static Database.Activity getActivityForGmsActivity(int detectedActivityType) {
    switch (detectedActivityType) {
      case DetectedActivity.ON_BICYCLE:
        return Database.Activity.CYCLING;
      case DetectedActivity.WALKING:
        return Database.Activity.WALKING;
      case DetectedActivity.RUNNING:
        return Database.Activity.RUNNING;
    }
    return Database.Activity.UNKNOWN;
  }
}
