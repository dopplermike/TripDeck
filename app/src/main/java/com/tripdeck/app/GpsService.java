package com.tripdeck.app;
import android.app.*;import android.content.*;import android.location.*;import android.os.*;import org.json.*;import java.io.*;import java.util.*;
public class GpsService extends Service implements LocationListener {
 static final ArrayList<JSONObject> queue=new ArrayList<>(); static JSONObject latest; static boolean recording=false, running=false; LocationManager lm;
 public IBinder onBind(Intent i){return null;}
 public int onStartCommand(Intent i,int flags,int id){
 if(i!=null&&"stop".equals(i.getAction())){stopSelf();return START_NOT_STICKY;}
 NotificationManager nm=getSystemService(NotificationManager.class);nm.createNotificationChannel(new NotificationChannel("gps","Trip Deck GPS",NotificationManager.IMPORTANCE_LOW));
 PendingIntent open=PendingIntent.getActivity(this,0,new Intent(this,MainActivity.class),PendingIntent.FLAG_IMMUTABLE|PendingIntent.FLAG_UPDATE_CURRENT);
 PendingIntent stop=PendingIntent.getService(this,1,new Intent(this,GpsService.class).setAction("stop"),PendingIntent.FLAG_IMMUTABLE);
 startForeground(1,new Notification.Builder(this,"gps").setSmallIcon(android.R.drawable.ic_menu_mylocation).setContentTitle("Trip Deck GPS active").setContentText("Open dashboard or stop GPS").setContentIntent(open).addAction(new Notification.Action.Builder(null,"Stop GPS",stop).build()).setOngoing(true).build());
 try{lm=getSystemService(LocationManager.class);lm.removeUpdates(this);lm.requestLocationUpdates(LocationManager.GPS_PROVIDER,1000,0,this);running=true;}catch(Exception e){stopSelf();}return START_NOT_STICKY;}
 public void onLocationChanged(Location l){try{JSONObject p=new JSONObject();JSONObject c=new JSONObject();c.put("latitude",l.getLatitude());c.put("longitude",l.getLongitude());c.put("altitude",l.hasAltitude()?l.getAltitude():JSONObject.NULL);c.put("speed",l.hasSpeed()?l.getSpeed():JSONObject.NULL);c.put("heading",l.hasBearing()?l.getBearing():JSONObject.NULL);c.put("accuracy",l.getAccuracy());p.put("coords",c);p.put("timestamp",l.getTime());synchronized(queue){latest=p;if(recording){queue.add(p);if(queue.size()>100000)queue.remove(0);try(FileWriter w=new FileWriter(new File(getFilesDir(),"recovery.csv"),true)){w.write(l.getTime()+","+l.getLatitude()+","+l.getLongitude()+","+c.optString("altitude")+","+c.optString("speed")+","+c.optString("heading")+","+l.getAccuracy()+"\n");}}}}catch(Exception ignored){}}
 public void onDestroy(){if(lm!=null)lm.removeUpdates(this);running=false;recording=false;super.onDestroy();}
}
