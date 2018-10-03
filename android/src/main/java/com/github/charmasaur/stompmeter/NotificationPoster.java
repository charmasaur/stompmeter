package com.github.charmasaur.stompmeter;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.support.v4.app.NotificationCompat;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Build;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.TimeZone;
import java.util.concurrent.TimeUnit;

public final class NotificationPoster {
  private static final int MAX_NOTIFICATION_ID = 100;
  private static final String PREFS_NAME = "noti_prefs";
  private static final String LAST_ID_KEY = "id";

  private static final String CHANNEL_ID = "channel";

  private final Context context;
  private final NotificationManager notificationManager;
  private final SharedPreferences sharedPreferences;

  public NotificationPoster(Context context) {
    this.context = context;
    notificationManager = context.getSystemService(NotificationManager.class);
    sharedPreferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
  }

  public void postNotification(
      Database.Activity activity, long durationMs, long startTimestampMs) {
    createChannelIfNecessary();
    int id = (sharedPreferences.getInt(LAST_ID_KEY, 0) + 1) % MAX_NOTIFICATION_ID;
    sharedPreferences.edit().putInt(LAST_ID_KEY, id).apply();

    Intent contentIntent = new Intent(context, MainActivity.class);
    contentIntent.setAction(MainActivity.ACTION_ACTIVITY);
    contentIntent.putExtra(Database.getActivityKey(activity), durationMs);

    notificationManager.notify(
        id,
        new NotificationCompat.Builder(context, CHANNEL_ID)
            .setContentTitle(
                context.getString(
                    R.string.noti_title,
                    getActivityName(activity),
                    getDuration(durationMs),
                    getStartTime(startTimestampMs)))
            .setSmallIcon(android.R.drawable.ic_menu_mylocation)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setContentIntent(PendingIntent.getActivity(context, 0, contentIntent, 0))
            .build());

  }

  private String getActivityName(Database.Activity activity) {
    switch (activity) {
      case WALKING:
        return context.getString(R.string.noti_walking);
      case CYCLING:
        return context.getString(R.string.noti_cycling);
      case RUNNING:
        return context.getString(R.string.noti_running);
    }
    return context.getString(R.string.noti_unknown);
  }

  private String getDuration(long durationMs) {
    return context.getString(R.string.minutes, TimeUnit.MILLISECONDS.toMinutes(durationMs));
  }

  private String getStartTime(long startTimestampMs) {
    SimpleDateFormat format = new SimpleDateFormat("HH:mm:ss");
    format.setTimeZone(TimeZone.getDefault());
    return format.format(new Date(startTimestampMs));
  }

  private void createChannelIfNecessary() {
    if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) {
      return;
    }
    NotificationChannel channel =
      new NotificationChannel(
          CHANNEL_ID,
          context.getString(R.string.noti_channel_name),
          NotificationManager.IMPORTANCE_DEFAULT);
    notificationManager.createNotificationChannel(channel);
  }
}
