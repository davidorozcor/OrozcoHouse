package davsoft.orozcohouse;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.ImageButton;

public class Irrigation extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_irrigation);
        addListenerOnButton();
    }

    public void addListenerOnButton() {

        ImageButton Irr_btn_Lights = (ImageButton) findViewById(R.id.Irr_btn_Lights);
        Irr_btn_Lights.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startActivity(new Intent(Irrigation.this, MainActivity.class));
            }
        });

    }
}
