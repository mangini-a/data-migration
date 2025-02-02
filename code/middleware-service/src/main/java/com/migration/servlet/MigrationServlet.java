package com.migration.servlet;

import org.json.JSONObject;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

@WebServlet("/migrate")
public class MigrationServlet extends HttpServlet {

    private static final String PHP_SERVICE_URL = "https://quizonline.altervista.org/second/public/api.php";
    private static final String PYTHON_SERVICE_URL = "http://localhost:5000/receive";

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {

        resp.setContentType("application/json");
        String tableName = req.getParameter("table");

        if (tableName == null || tableName.trim().isEmpty()) {
            sendError(resp, "Table name parameter is required");
            return;
        }

        try {
            // Fetch data from the remote web service
            JSONObject sourceData = fetchFromPhpService(tableName);

            // Forward data to the local web service
            JSONObject result = forwardToPythonService(sourceData);

            // Return result
            resp.getWriter().write(result.toString());

        } catch (Exception e) {
            sendError(resp, "Error during migration: " + e.getMessage());
        }
    }
    
    /**
     * Fetches all the records belonging to the specified table of the remote database.
     * 
     * @param tableName the name of the database table to be queried
     * @return a JSONObject representing the fetched data
     * @throws IOException
     */
    private JSONObject fetchFromPhpService(String tableName) throws IOException {
        CloseableHttpClient httpClient = HttpClients.createDefault();
        
        // Add table name as query parameter and set up a GET request
        String url = PHP_SERVICE_URL + "?table=" + tableName;
        HttpGet getRequest = new HttpGet(url);

        try {
            CloseableHttpResponse response = httpClient.execute(getRequest);
            String responseBody = EntityUtils.toString(response.getEntity());
            
            return new JSONObject(responseBody);
        } finally {
            httpClient.close();
        }
    }
    
    /**
     * Forwards the data retrieved from the remote database to the local web service.
     * 
     * @param sourceData the data retrieved from the remote database
     * @return a JSONObject representing the forwarded data
     * @throws IOException
     */
    private JSONObject forwardToPythonService(JSONObject sourceData) throws IOException {
        CloseableHttpClient httpClient = HttpClients.createDefault();

        // Set up a POST request
        HttpPost postRequest = new HttpPost(PYTHON_SERVICE_URL);
        
        // Forward the data as-is
        postRequest.setEntity(new StringEntity(sourceData.toString()));
        postRequest.setHeader("Content-Type", "application/json");
        
        try {
            CloseableHttpResponse response = httpClient.execute(postRequest);
            String responseBody = EntityUtils.toString(response.getEntity());
            
            return new JSONObject(responseBody);
        } finally {
            httpClient.close();
        }
    }

    /**
     * Notifies the client when an error occurs.
     * 
     * @param response the response the servlet sends to the client
     * @param message a message describing the issue
     * @throws IOException
     */
    private void sendError(HttpServletResponse response, String message) throws IOException {
        response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
        JSONObject error = new JSONObject();
        error.put("status", "error");
        error.put("message", message);
        response.getWriter().write(error.toString());
    }
}
