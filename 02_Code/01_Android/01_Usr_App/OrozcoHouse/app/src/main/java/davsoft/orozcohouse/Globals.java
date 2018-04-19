package davsoft.orozcohouse;

/**
 * Created by ORJ1GA on 19/04/2018.
 */

public class Globals {
    private static Globals instance;
    private String server = "192.168.1.68";
    private String port = "5000";


    // Restrict the constructor from being instantiated
    private Globals(){}

    public String getServer(){

        return "http://" + this.server + ":" + this.port + "/";

    }

    public static synchronized Globals getInstance(){
        if(instance==null){
            instance=new Globals();
        }
        return instance;
    }

}
