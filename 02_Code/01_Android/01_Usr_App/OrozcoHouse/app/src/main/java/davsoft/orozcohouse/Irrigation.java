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

public class Irrigation extends AppCompatActivity {

    String TAG = "irrigation";
    String webservice;

    List<String> params = new ArrayList<>();//this is the required parameter
    private IrrigationTask mIrrigationTask = null;

    NumberPicker Ir_bp_Patio;
    NumberPicker Ir_bp_Excedente;
    NumberPicker Ir_bp_Frente;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_irrigation);
        addListenerOnButton();

        Ir_bp_Patio = (NumberPicker)  findViewById(R.id.Ir_bp_Patio);
        Ir_bp_Patio.setMinValue(0);
        Ir_bp_Patio.setMaxValue(15);

        Ir_bp_Excedente = (NumberPicker)  findViewById(R.id.Ir_bp_Excedente);
        Ir_bp_Excedente.setMinValue(0);
        Ir_bp_Excedente.setMaxValue(15);

        Ir_bp_Frente = (NumberPicker)  findViewById(R.id.Ir_bp_Frente);
        Ir_bp_Frente.setMinValue(0);
        Ir_bp_Frente.setMaxValue(15);

    }

    public void addListenerOnButton() {

        ImageButton Irr_btn_Lights = (ImageButton) findViewById(R.id.Irr_btn_Lights);
        Irr_btn_Lights.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startActivity(new Intent(Irrigation.this, MainActivity.class));
            }
        });


        ImageButton Ir_btn_Encender_Riego = (ImageButton) findViewById(R.id.Ir_btn_Encender_Riego);
        Ir_btn_Encender_Riego.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                Riego();
            }
        });

    }

    private void Riego() {


        if (mIrrigationTask != null) {
            return;
        }


        Integer MinutosPatio;
        MinutosPatio =  Ir_bp_Patio.getValue();

        Integer MinutosExcendete;
        MinutosExcendete =  Ir_bp_Excedente.getValue();

        Integer MinutosFrente;
        MinutosFrente =  Ir_bp_Frente.getValue();

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

            mIrrigationTask = new IrrigationTask( String.valueOf(MinutosFrente),String.valueOf(MinutosExcendete),String.valueOf(MinutosPatio));
            mIrrigationTask.execute((Void) null);
        }
    }

    /**
     * Represents an asynchronous login/registration task used to authenticate
     * the user.
     */
    public class IrrigationTask extends AsyncTask<Void, Void, JSONObject> {

        private ProgressDialog pDialog;

        String status;

        IrrigationTask(String MinutosFrente,String MinutosExcendete,String MinutosPatio) {

            Globals gblInstance = Globals.getInstance();
            webservice = gblInstance.getServer() + "switch_Light";

            params.clear();
            params.add("{\"tiempo_riego_frente\":\"" + MinutosFrente + "\",\"tiempo_riego_excedente\":\"" + MinutosExcendete + "\",\"tiempo_riego_patio\":\"" + MinutosPatio + "\"}");

        }

        @Override
        protected void onPreExecute()
        {
            pDialog = new ProgressDialog(Irrigation.this);
            pDialog.setMessage("Iniciando Irrigacion...");
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
            mIrrigationTask = null;
        }
    }
}
