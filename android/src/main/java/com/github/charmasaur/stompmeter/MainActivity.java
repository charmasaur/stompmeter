package com.github.charmasaur.stompmeter;

import android.content.Intent;
import android.os.Bundle;
import android.support.v4.app.FragmentActivity;
import android.util.Log;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import com.google.common.collect.ImmutableList;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.TimeZone;

public final class MainActivity extends FragmentActivity {
  private static final String TAG = MainActivity.class.getSimpleName();

  public static final String ACTION_ACTIVITY = "com.github.charmasaur.stompmeter.ACTIVITY";

  private static final class Entry {
    private final String queryParam;
    private final EditText editText;

    public Entry(String queryParam, EditText editText) {
      this.queryParam = queryParam;
      this.editText = editText;
    }

    public void setValue(String value) {
      editText.setText(value);
    }

    public String getKey() {
      return queryParam;
    }

    public String getValue() {
      return editText.getText().toString();
    }
  }

  private static final class Mergable {
    private final String key;
    private final Entry config;

    private long durationMs;

    public Mergable(String key, Entry config) {
      this.key = key;
      this.config = config;
    }

    public void merge(long additionalDurationMs) {
      durationMs += additionalDurationMs;
      Log.i(TAG, "Duration of " + key + ": " + durationMs);
      config.setValue(String.format("%.1f", ((float) durationMs / (1000.f * 60.f * 60.f))));
    }

    public String getKey() {
      return key;
    }
  }

  private Entry createNumberEntry(String displayName, String queryParam) {
    View view = getLayoutInflater().inflate(R.layout.item, root, /* attachToRoot= */ false);
    TextView text = (TextView) view.findViewById(R.id.text);
    text.setText(displayName);
    EditText editText = (EditText) view.findViewById(R.id.edittext);
    root.addView(view);
    Entry config = new Entry(queryParam, editText);
    config.setValue("0.0");
    return config;
  }

  private Entry createDateEntry(String displayName, String queryParam) {
    View view = getLayoutInflater().inflate(R.layout.date_item, root, /* attachToRoot= */ false);
    TextView text = (TextView) view.findViewById(R.id.text);
    text.setText(displayName);
    EditText editText = (EditText) view.findViewById(R.id.edittext);
    root.addView(view);
    Entry config = new Entry(queryParam, editText);
    SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd");
    format.setTimeZone(TimeZone.getDefault());
    config.setValue(format.format(new Date()));
    return config;
  }

  private ImmutableList<Entry> entries;
  private ImmutableList<Mergable> mergables;
  private ViewGroup root;
  private TextView status;

  @Override
  public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);

    setContentView(R.layout.main);
    root = (ViewGroup) findViewById(R.id.root);

    ImmutableList.Builder<Entry> entriesBuilder = new ImmutableList.Builder<>();
    ImmutableList.Builder<Mergable> mergablesBuilder = new ImmutableList.Builder<>();

    entriesBuilder.add(createDateEntry("Date", "date"));

    Entry running = createNumberEntry("Running", "running");
    entriesBuilder.add(running);
    mergablesBuilder.add(
        new Mergable(Database.getActivityKey(Database.Activity.RUNNING), running));

    Entry walking = createNumberEntry("Walking", "walking");
    entriesBuilder.add(walking);
    mergablesBuilder.add(
        new Mergable(Database.getActivityKey(Database.Activity.WALKING), walking));

    Entry cycling = createNumberEntry("Cycling", "cycling");
    entriesBuilder.add(cycling);
    mergablesBuilder.add(
        new Mergable(Database.getActivityKey(Database.Activity.CYCLING), cycling));

    entriesBuilder.add(createNumberEntry("Standing", "standing"));
    entriesBuilder.add(createNumberEntry("Swimming", "swimming"));
    entriesBuilder.add(createNumberEntry("Stretching", "stretching"));

    entries = entriesBuilder.build();
    mergables = mergablesBuilder.build();

    Button button =
        (Button) getLayoutInflater().inflate(R.layout.submit, root, /* attachToRoot= */ false);
    button.setOnClickListener(view -> submit());
    root.addView(button);

    status =
      (TextView) getLayoutInflater().inflate(R.layout.status, root, /* attachToRoot= */ false);
    root.addView(status);

    handleIntent(getIntent());
  }

  @Override
  protected void onNewIntent(Intent intent) {
    handleIntent(intent);
  }

  private void handleIntent(Intent intent) {
    if (!ACTION_ACTIVITY.equals(intent.getAction())) {
      Log.e(TAG, "Unrecognised intent action: " + intent.getAction());
      return;
    }
    for (Mergable mergable : mergables) {
      mergable.merge(intent.getLongExtra(mergable.getKey(), 0));
    }
  }
}
