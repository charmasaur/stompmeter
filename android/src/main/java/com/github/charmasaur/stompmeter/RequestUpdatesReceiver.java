package com.github.charmasaur.stompmeter;

import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;
import com.google.android.gms.location.ActivityRecognition;
import com.google.android.gms.location.ActivityTransition;
import com.google.android.gms.location.ActivityTransitionRequest;
import com.google.android.gms.location.DetectedActivity;
import com.google.common.collect.ImmutableList;

public final class RequestUpdatesReceiver extends BroadcastReceiver {
  private static final String TAG = RequestUpdatesReceiver.class.getSimpleName();

  @Override
  public void onReceive(Context context, Intent intent) {
    Log.i(TAG, "onReceive: " + intent.getAction());

    Database database = new Database(context);
    Database.RegistrationStatus registrationStatus = database.getRegistrationStatus();
    // Clear out any times, since they might be invalid.
    database.reset();
    database.setRegistrationStatus(Database.RegistrationStatus.PENDING);

    ActivityRecognition.getClient(context).requestActivityTransitionUpdates(
        new ActivityTransitionRequest(
            ImmutableList.of(
                new ActivityTransition.Builder()
                    .setActivityTransition(ActivityTransition.ACTIVITY_TRANSITION_ENTER)
                    .setActivityType(DetectedActivity.ON_BICYCLE)
                    .build(),
                new ActivityTransition.Builder()
                    .setActivityTransition(ActivityTransition.ACTIVITY_TRANSITION_EXIT)
                    .setActivityType(DetectedActivity.ON_BICYCLE)
                    .build(),
                new ActivityTransition.Builder()
                    .setActivityTransition(ActivityTransition.ACTIVITY_TRANSITION_ENTER)
                    .setActivityType(DetectedActivity.WALKING)
                    .build(),
                new ActivityTransition.Builder()
                    .setActivityTransition(ActivityTransition.ACTIVITY_TRANSITION_EXIT)
                    .setActivityType(DetectedActivity.WALKING)
                    .build(),
                new ActivityTransition.Builder()
                    .setActivityTransition(ActivityTransition.ACTIVITY_TRANSITION_ENTER)
                    .setActivityType(DetectedActivity.RUNNING)
                    .build(),
                new ActivityTransition.Builder()
                    .setActivityTransition(ActivityTransition.ACTIVITY_TRANSITION_EXIT)
                    .setActivityType(DetectedActivity.RUNNING)
                    .build())),
        PendingIntent.getBroadcast(
          context, 0, new Intent(context, ActivityTransitionReceiver.class), 0))
    .addOnFailureListener(
        e -> {
          Log.e(TAG, "onFailure", e);
          database.setRegistrationStatus(Database.RegistrationStatus.FAILED);
        })
    .addOnSuccessListener(
        result -> {
          Log.i(TAG, "onSuccess");
          database.setRegistrationStatus(Database.RegistrationStatus.SUCCEEDED);
        });
  }
}
