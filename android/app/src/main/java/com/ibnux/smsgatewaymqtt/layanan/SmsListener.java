package com.ibnux.smsgatewaymqtt.layanan;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.AsyncTask;
import android.provider.Telephony;
import android.telephony.SmsMessage;
import android.util.Log;

import com.ibnux.smsgatewaymqtt.Utils.Fungsi;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;

import javax.net.ssl.HttpsURLConnection;
import org.json.JSONObject;

public class SmsListener extends BroadcastReceiver {

    SharedPreferences sp;

    @Override
    public void onReceive(Context context, Intent intent) {
        if (sp == null) sp = context.getSharedPreferences("pref", 0);
        String url = sp.getString("urlPost", null);
        if (Telephony.Sms.Intents.SMS_RECEIVED_ACTION.equals(intent.getAction())) {
            // Get all message parts
            SmsMessage[] messages = Telephony.Sms.Intents.getMessagesFromIntent(intent);
            if (messages == null || messages.length == 0) return;
            
            // Use first message for sender and timestamp
            String messageFrom = messages[0].getOriginatingAddress();
            String messageTimestamp = String.valueOf(messages[0].getTimestampMillis());
            
            // Concatenate all message parts
            StringBuilder fullMessage = new StringBuilder();
            for (SmsMessage smsMessage : messages) {
                fullMessage.append(smsMessage.getMessageBody());
            }
            String messageBody = fullMessage.toString();

            Log.i("SMS From", messageFrom);
            Log.i("SMS Body", messageBody);
            Fungsi.writeLog("!SMS: RECEIVED : " + messageFrom + " " + messageBody);
            String topic = sp.getString("mqtt_topic", "sms/received");

            JSONObject json = new JSONObject();
            try {
                json.put("from", messageFrom);
                json.put("message", messageBody);
                json.put("timestamp", messageTimestamp);
                json.put("type", "received");
            } catch (Exception e) {
                Log.e("SmsListener", "Error creating JSON", e);
                return;
            }

            String payload = json.toString();

            Intent mqttIntent = new Intent(context, BackgroundService.class);
            mqttIntent.setAction("PUBLISH");
            mqttIntent.putExtra("topic", topic);
            mqttIntent.putExtra("payload", payload);
            context.startService(mqttIntent);
            
            Fungsi.writeLog("SMS: MQTT PUBLISH : " + topic + " : " + payload);
        }
    }

    static class postDataTask extends AsyncTask<String, Void, String> {

        private Exception exception;

        protected String doInBackground(String... datas) {
            URL url;
            String response = "";
            try {
                try {
                    url = new URL(datas[0]);

                    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                    conn.setReadTimeout(15000);
                    conn.setConnectTimeout(15000);
                    conn.setRequestMethod("POST");
                    conn.setDoInput(true);
                    conn.setDoOutput(true);

                    OutputStream os = conn.getOutputStream();
                    BufferedWriter writer = new BufferedWriter(
                            new OutputStreamWriter(os, "UTF-8"));
                    writer.write(datas[1]);

                    writer.flush();
                    writer.close();
                    os.close();
                    int responseCode = conn.getResponseCode();

                    if (responseCode == HttpsURLConnection.HTTP_OK) {
                        String line;
                        BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                        while ((line = br.readLine()) != null) {
                            response += line;
                        }
                    } else {
                        response = "";

                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }

                return "SMS: POST : " + datas[0] + " : " + response;
            } catch (Exception e) {
                e.printStackTrace();
                return "SMS: POST FAILED : " + datas[0] + " : " + e.getMessage();
            }
        }

        @Override
        protected void onPostExecute(String response) {
            Fungsi.writeLog(response);
        }
    }


    public static void sendPOST(String urlPost, String from, String msg, String tipe, String msgTimestamp) {
        if (urlPost == null) return;
        if (from.isEmpty()) return;
        if (!urlPost.startsWith("http")) return;
        try {
            new postDataTask().execute(urlPost,
                    "number=" + URLEncoder.encode(from, "UTF-8") +
                            "&message=" + URLEncoder.encode(msg, "UTF-8") +
                            "&type=" + URLEncoder.encode(tipe, "UTF-8") +
                            "&timestamp=" + URLEncoder.encode(msgTimestamp, "UTF-8")
            );
        } catch (Exception e) {
            e.printStackTrace();
            Fungsi.writeLog("SMS: POST FAILED : " + urlPost + " : " + e.getMessage());
        }
    }

}
