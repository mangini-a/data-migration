package com.migration.servlet;

import com.google.gson.Gson;
import com.google.gson.JsonObject;

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
    // Define service URLs as constants
    private static final String PHP_SERVICE_URL = "https://quizonline.altervista.org/second/public/api.php";
    private static final String PYTHON_SERVICE_URL = "http://localhost:5000/receive";

    // Create a single Gson instance for better performance
    private final Gson gson = new Gson();

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        // Set response content type to JSON
        resp.setContentType("application/json");

        // Get the table name of interest from request parameters
        String tableName = req.getParameter("table");

        // Validate the table name parameter
        if (tableName == null || tableName.trim().isEmpty()) {
            sendError(resp, "Table name parameter is required");
            return;
        }

        try {
            // Fetch data from the PHP web service
            JsonObject sourceData = fetchFromPhpService(tableName);

            // Forward the data to the Python web service
            JsonObject result = forwardToPythonService(sourceData);

            // Write the response
            resp.getWriter().write(gson.toJson(result));

        } catch (Exception e) {
            sendError(resp, "Error during migration: " + e.getMessage());
        }
    }
    
    /**
     * Fetches all the records belonging to the specified table from the remote database.
     * Uses HTTP GET to retrieve data from the PHP service.
     * 
     * @param tableName the name of the database table to be queried
     * @return a JsonObject containing the fetched data
     * @throws IOException if there's an error in the HTTP communication
     */
    private JsonObject fetchFromPhpService(String tableName) throws IOException {
        // Create an HTTP client that will be automatically closed
        try (CloseableHttpClient httpClient = HttpClients.createDefault()) {
            // Construct the URL with the table name parameter
            String url = PHP_SERVICE_URL + "?table=" + tableName;
            HttpGet getRequest = new HttpGet(url);

            // Execute the request and get the response
            try (CloseableHttpResponse response = httpClient.execute(getRequest)) {
                // Convert the response body to a string
                String responseBody = EntityUtils.toString(response.getEntity());

                // Parse the JSON string into a JsonObject using Gson
                return gson.fromJson(responseBody, JsonObject.class);
            }
        }
    }
    
    /**
     * Forwards the data retrieved from the remote database to the local Python web service.
     * Uses HTTP POST to send the data.
     * 
     * @param sourceData the data retrieved from the remote database
     * @return a JsonObject containing the response from the Python service
     * @throws IOException if there's an error in the HTTP communication
     */
    private JsonObject forwardToPythonService(JsonObject sourceData) throws IOException {
        // Create an HTTP client that will be automatically closed
        try (CloseableHttpClient httpClient = HttpClients.createDefault()) {
            // Create a POST request to the Python service
            HttpPost postRequest = new HttpPost(PYTHON_SERVICE_URL);

            // Convert the JsonObject to a JSON string and set it as the request body
            postRequest.setEntity(new StringEntity(gson.toJson(sourceData)));
            postRequest.setHeader("Content-Type", "application/json");

            // Execute the request and get the response
            try (CloseableHttpResponse response = httpClient.execute(postRequest)) {
                // Convert the response body to a string
                String responseBody = EntityUtils.toString(response.getEntity());

                // Parse the JSON string into a JsonObject using Gson
                return gson.fromJson(responseBody, JsonObject.class);
            }
        }
    }

    /**
     * Sends an error response to the client in JSON format.
     * 
     * @param response the HttpServletResponse object
     * @param message the error message to be sent
     * @throws IOException if there's an error writing the response
     */
    private void sendError(HttpServletResponse response, String message) throws IOException {
        // Set the response status to BAD REQUEST
        response.setStatus(HttpServletResponse.SC_BAD_REQUEST);

        // Create an error object using JsonObject from Gson
        JsonObject error = new JsonObject();
        error.addProperty("status", "error");
        error.addProperty("message", message);

        // Write the error response
        response.getWriter().write(gson.toJson(error));
    }
}
