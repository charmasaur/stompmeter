package com.github.charmasaur.stompmeter;

import android.content.Intent;
import android.os.Bundle;
import android.support.v4.app.FragmentActivity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

public final class MainActivity extends FragmentActivity {
  public static final String ACTION_ACTIVITY = "com.github.charmasaur.stompmeter.ACTIVITY";

  @Override
  public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.main);
    findViewById(R.id.register).setOnClickListener(view -> register());
    handleIntent(getIntent());
  }

  private void handleIntent(Intent intent) {
    if (!ACTION_ACTIVITY.equals(intent.getAction())) {
      return;
    }
    ((TextView) findViewById(R.id.text)).setText("Received some data: " + intent.getExtras());
  }

  private void register() {
    sendBroadcast(new Intent(this, RequestUpdatesReceiver.class));
  }
}
