package davsoft.orozcohouse;

import android.app.ProgressDialog;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.ImageButton;
import android.widget.NumberPicker;
import android.widget.Toast;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

public class MainActivity extends AppCompatActivity {

    String TAG = "Lights";
    String webservice;

    NumberPicker AM_np_Jardin_Hrs;
    NumberPicker AM_np_Jardin_Mins;
    ImageButton AM_btn_irrigation;
    ImageButton AM_btn_JardinLightSwitch;

    List<String> params = new ArrayList<>();//this is the required parameter
    private SwitchLightTask mSwitchLightTask = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        AM_np_Jardin_Hrs = (NumberPicker)  findViewById(R.id.AM_np_Jardin_Hrs);
        AM_np_Jardin_Hrs.setMinValue(0);
        AM_np_Jardin_Hrs.setMaxValue(23);

        AM_np_Jardin_Mins = (NumberPicker)  findViewById(R.id.AM_np_Jardin_Mins);
        AM_np_Jardin_Mins.setMinValue(0);
        AM_np_Jardin_Mins.setMaxValue(60);

        addListenerOnButton();
    }

    public void addListenerOnButton() {

        AM_btn_irrigation = (ImageButton) findViewById(R.id.AM_btn_irrigation);
        AM_btn_irrigation.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startActivity(new Intent(MainActivity.this, Irrigation.class));
            }
        });

        AM_btn_JardinLightSwitch = (ImageButton) findViewById(R.id.AM_btn_JardinLightSwitch);
        AM_btn_JardinLightSwitch.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                SwitchLight();
            }
        });

    }

    private void SwitchLight() {


        if (mSwitchLightTask != null) {
            return;
        }


        Integer MinutesLight;
        MinutesLight = (AM_np_Jardin_Hrs.getValue() * 60) + AM_np_Jardin_Mins.getValue();

        boolean cancel = false;
        View focusView = null;

       //DaOr, verifica que el estado sea apagado para esa luz

        if (cancel) {
            // There was an error; don't attempt login and focus the first
            // form field with an error.
            focusView.requestFocus();
        } else {
            // Show a progress spinner, and kick off a background task to
            // perform the user login attempt.

            mSwitchLightTask = new SwitchLightTask("Jardin", String.valueOf(MinutesLight));
            mSwitchLightTask.execute((Void) null);
        }
    }

    /**
     * Represents an asynchronous login/registration task used to authenticate
     * the user.
     */
    public class SwitchLightTask extends AsyncTask<Void, Void, JSONObject> {

        private ProgressDialog pDialog;

        String status;

        SwitchLightTask(String Light, String Time) {

            Globals gblInstance = Globals.getInstance();
            webservice = gblInstance.getServer() + "switch_Light";

            params.clear();
            params.add("{\"Light\":\"" + Light + "\",\"Tiempo\":\"" + Time + "\"}");

        }

        @Override
        protected void onPreExecute()
        {
            pDialog = new ProgressDialog(MainActivity.this);
            pDialog.setMessage("Espere...");
            pDialog.setIndeterminate(false);
            pDialog.setCancelable(false);
            pDialog.show();
            super.onPreExecute();
        }


        @Override
        protected JSONObject doInBackground(Void... args) {

            JSONObject json = new JSONParser().makeHttpRequest2(webservice, "GET", params);
            return json;
        }

        @Override
        protected void onPostExecute(JSONObject jsonObject) {
            super.onPostExecute(jsonObject);

            try {
                if (jsonObject != null) {
                    Log.e(TAG, "webservice_responce=" + jsonObject.toString());
                    status = jsonObject.getString("status");
                    if (status.equals("success")) {


                    } else {

                        Toast.makeText(getApplicationContext(), jsonObject.getString("error").toString(), Toast.LENGTH_SHORT).show();
                        onCancelled();

                    }
                }else{
                    Toast.makeText(getApplicationContext(), "The server is not reached", Toast.LENGTH_SHORT).show();
                    onCancelled();
                }

            } catch (JSONException e) {
                e.printStackTrace();
            } catch (Exception e) {
                e.printStackTrace();
            }

            pDialog.dismiss();
        }

        @Override
        protected void onCancelled() {
            pDialog.dismiss();
            mSwitchLightTask = null;
        }
    }
}
