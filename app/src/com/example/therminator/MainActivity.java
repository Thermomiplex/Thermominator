package com.example.therminator;

import java.io.BufferedInputStream;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.Scanner;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.util.EntityUtils;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.graphics.drawable.TransitionDrawable;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.CountDownTimer;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.Toast;

public class MainActivity extends Activity {

	private static String baseURL = "http://152.78.200.94:11884/";
	private static int lowerBound = 15;
	private static int upperBound = 20;
	private int piId = 2;
	private static int jump = 3;
	private int setPoint = 8;
	private int tollerance = 2;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);

		addButtonListeners();

		new getSetPointTask().execute();
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.main, menu);
		return true;
	}
	
	@Override
	public boolean onOptionsItemSelected(MenuItem item) {
	    switch(item.getItemId()) {
	    case R.id.action_settings:
	        Intent intent = new Intent(this, SettingsActivity.class);
	        this.startActivity(intent);
	        break;
	    default:
	        return super.onOptionsItemSelected(item);
	    }

	    return true;
	}

	public void addButtonListeners() {
		final Button downButton = (Button) findViewById(R.id.button1);
		final Button upButton = (Button) findViewById(R.id.button2);

		downButton.setOnClickListener(new OnClickListener() {
			@Override
			public void onClick(View view) {
				// TODO Auto-generated method stub
				//Log.d("Therminator", "down");
				view.setEnabled(false);
				MyCountDownTimer timer = new MyCountDownTimer(5000, 1000, view);
				timer.start();
				
				int oldSetPoint = setPoint;
				setPoint -= jump;
				int newSetPoint = setPoint;
				Log.d("Therminator", setPoint+"");
				showToast("House cooling down...");
				updateTree(oldSetPoint, newSetPoint);
				new uploadSetPointTask().execute();
			}
		});

		upButton.setOnClickListener(new OnClickListener() {
			@Override
			public void onClick(View view) {
				// TODO Auto-generated method stub
				//Log.d("Therminator", "up");
				view.setEnabled(false);
				MyCountDownTimer timer = new MyCountDownTimer(5000, 1000, view);
				timer.start();
				
				int oldSetPoint = setPoint;
				setPoint += jump;
				int newSetPoint = setPoint;
				Log.d("Therminator", setPoint+"");
				showToast("House warming up...");
				updateTree(oldSetPoint, newSetPoint);
				new uploadSetPointTask().execute();
			}
		});
	}

	private void showToast(String text) {
		Context context = getApplicationContext();
		int duration = Toast.LENGTH_SHORT;
		Toast toast = Toast.makeText(context, text, duration);
		toast.show();
	}

	private void updateTree() {
		ImageView imageView= (ImageView) findViewById(R.id.imageView1);
		if (setPoint < lowerBound) {
			imageView.setImageResource(R.drawable.fruit);
		} else if (setPoint < upperBound) {
			imageView.setImageResource(R.drawable.leaves);
		} else {
			imageView.setImageResource(R.drawable.dead);
		}
	}

	private void updateTree(int oldSetPoint, int newSetPoint) {
		if (oldSetPoint < lowerBound && newSetPoint >= lowerBound) {
			transitionTree(R.drawable.fruit_to_leaves);
			Log.d("Therminator", "fruit_to_leaves");
		} else if (oldSetPoint < upperBound && newSetPoint >= upperBound) {
			transitionTree(R.drawable.leaves_to_dead);
			Log.d("Therminator", "leaves_to_dead");
		} else if (oldSetPoint >= lowerBound && newSetPoint < lowerBound) {
			transitionTree(R.drawable.leaves_to_fruit);
			Log.d("Therminator", "leaves_to_fruit");
		} else if (oldSetPoint >= upperBound && newSetPoint < upperBound) {
			transitionTree(R.drawable.dead_to_leaves);
			Log.d("Therminator", "dead_to_leaves");
		}
	}

	public class uploadSetPointTask extends AsyncTask<String, Void, Void> {
		@Override
		protected Void doInBackground(String... args) {
			uploadSetPoint();
			return null;
		}
	}

	public class getSetPointTask extends AsyncTask<String, Void, Void> {
		@Override
		protected Void doInBackground(String... args) {
			getSetPoint();
			updateTree();
			return null;
		}
	}

	private void uploadSetPoint() {
		try {
			// form url
			String urlString = baseURL + "set/" + piId + "/" + setPoint;
			Log.d("Therminator", urlString);
			URL url = new URL(urlString);
			// send request
			HttpURLConnection urlConnection = (HttpURLConnection) url.openConnection();
			// read response
			BufferedInputStream in = new BufferedInputStream(urlConnection.getInputStream());
			Scanner s = new Scanner(in).useDelimiter("\\A");
			String resp = s.hasNext() ? s.next() : "";
		} catch (MalformedURLException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	private void getSetPoint(){
		String urlString = baseURL + "get/" + piId + "/";
		String output="";
		try {
			DefaultHttpClient httpClient = new DefaultHttpClient();
			HttpGet httpGet = new HttpGet(urlString);

			HttpResponse httpResponse = httpClient.execute(httpGet);
			HttpEntity httpEntity = httpResponse.getEntity();
			output = EntityUtils.toString(httpEntity);
			//Log.d("Therminator","Output value: "+output);
			setPoint = (int) Double.parseDouble(output);
			Log.d("Therminator", "server set point" + setPoint);
		} catch(Exception e) {
			e.printStackTrace();
		}
	}

	private void transitionTree(int drawable) {
		TransitionDrawable transition = (TransitionDrawable) getResources()
				.getDrawable(drawable);
		transition.startTransition(5000);
		ImageView imageView= (ImageView) findViewById(R.id.imageView1);
		imageView.setImageDrawable(transition);
	}
	
	private class MyCountDownTimer extends CountDownTimer {
		
		private View view;
		
		public MyCountDownTimer(long startTime, long interval) {
			super(startTime, interval);
		}
		
		public MyCountDownTimer(long startTime, long interval, View view) {
			super(startTime, interval);
			this.view = view;
			Log.d("Therminator", "MyCountDownTimer started");
		}

		@Override
		public void onFinish() {
			// TODO Auto-generated method stub
			MainActivity.this.runOnUiThread(new Runnable(){
			    public void run(){
					view.setEnabled(true);
					Log.d("Therminator", "MyCountDownTimer finished");
			    }
			});
		}

		@Override
		public void onTick(long arg0) {
			// TODO Auto-generated method stub
			
		}
	}

}
