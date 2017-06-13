import java.io.*;
import java.utils.Base64;
import org.apache.http.HttpResponse;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.DefaultHttpClient;


public class testREST{
	public static string USERNAME = "ryan_harty@ahm.honda.com";
	public static string PASSWORD = "Solar421";
	public static string CLIENT_ID = "powerguide_api_dev";
	public static string CLIENT_SECRET = "m+OxOfSw9E3daSXsl5Qt7yCI4TAxjRPAJcDa5BUbiJA=";
	public static string SCOPE = "https://api.solarcity.com/solarguard/";

	public static void main(String[] args) {
		

		try {
			HttpClient client = new DefaultHttpClient();
			StringEntity data = new StringEntity("{\"grant_type": "password\", 
									"username": USERNAME\,
									"password": PASSWORD\,
									"scope":SCOPE}");
			HttpPost tokenRequest 
				= new HttpPost("https://login.solarcity.com/issue/oauth2/token");
			tokenRequest.addHeader("Authorization","Basic " + Base64.getEncoder().encodeToString(CLIENT_ID + ":" + CLIENT_SECRECT));
			tokenRequest.addHeader("content-type","application/json");
			tokenRequest.setEntity(data);
			HttpResponse response = client.execute(tokenRequest);

			if (response.getStatusLine().getStatusCode() != 200) {
				throw new RuntimeException("Failed : HTTP error code : "
				   + response.getStatusLine().getStatusCode());
			}

			BufferedReader tokenReader = new BufferedReader(
				 new InputStreamReader((response.getEntity().getContent()));
			}
			string accessToken;
			
			//iterate inputStream to find access token
			while ((accessToken = tokenReader.readLine()) != "access_token") {
				continue;
			}
			accessToken = tokenReader.readline();
			System.out.println("Access Token Obtained: " + accessToken);
			tokenReader.close();
				
			//Close connnection	
			client.getConnectionManager().shutdown();
			
		} catch (MalformedURLException e) {
			e.printStackTrace();
		} catch (ClientProtocolException e) {
			e.printStackTrace();
		} catch (IOException e){
			e.printStackTrace();
		}
	}
}
					   
			
