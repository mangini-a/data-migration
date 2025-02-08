package com.migration.servlet;

import com.google.gson.Gson;
import com.google.gson.JsonObject;

import java.io.IOException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.ServletException;

import kong.unirest.HttpResponse;
import kong.unirest.Unirest;

@WebServlet("/migrate")
public class MigrationServlet extends HttpServlet {
    // Define service URLs as constants
    private static final String PHP_SERVICE_URL = "https://quizonline.altervista.org/second/public/api.php";
    private static final String PYTHON_SERVICE_URL = "http://localhost:5000/receive";

    // Create a single Gson instance for better performance
    private final Gson gson = new Gson();

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        // Get the the name of the table to be retrieved from the request parameter
        String tableName = request.getParameter("table");
                
        // Validate the request parameter's value
        if (tableName == null || tableName.trim().isEmpty()) {
            sendError(request, response, "Table name parameter is required.");
            return;
        }
         
        try {
            // Show the user the current stage of migration (1)
            String message = "Fetching " + tableName + "\'s data from the remote database...";
            request.setAttribute("message", message);
            request.getRequestDispatcher("index.jsp").forward(request, response);

            // Fetch data from the PHP web service
            String sourceData = fetchFromPhpService(tableName);

            // Show the user the current stage of migration (2)
            message = "Inserting " + tableName + "\'s data into the local database...";
            request.setAttribute("message", message);
            request.getRequestDispatcher("index.jsp").forward(request, response);
            
            // Forward the data to the Python web service
            String result = forwardToPythonService(sourceData);
            
            // Parse the JSON response from the Python web service
            JsonObject responseJson = gson.fromJson(result, JsonObject.class);
            String status = responseJson.get("status").getAsString();
            String finalMessage = responseJson.get("message").getAsString();

            // Show the user the current stage of migration (3)
            request.setAttribute("status", status);
            request.setAttribute("message", finalMessage);
            request.getRequestDispatcher("index.jsp").forward(request, response);

        } catch (Exception e) {
            sendError(request, response, "Error during migration: " + e.getMessage() + ".");
        }
    }
    
    /**
     * Fetches all the records belonging to the specified table from the remote database.
     * Uses HTTP GET to retrieve data from the PHP service.
     * 
     * @param tableName the name of the database table to be queried
     * @return the JSON data as a string
     * @throws IOException if there's an error in the HTTP communication
     */
    private String fetchFromPhpService(String tableName) throws IOException {
        HttpResponse<String> response = Unirest.get(PHP_SERVICE_URL)
                .queryString("table", tableName)
                .asString();

        if (response.getStatus() != 200) {
            throw new IOException("Failed to fetch data from PHP service: " + response.getStatusText());
        }

        return response.getBody();
    }
    
    /**
     * Forwards the data retrieved from the remote database to the local Python web service.
     * Uses HTTP POST to send the data.
     * 
     * @param sourceData the data retrieved from the remote database
     * @return the response from the Python service
     * @throws IOException if there's an error in the HTTP communication
     */
    private String forwardToPythonService(String sourceData) throws IOException {
        HttpResponse<String> response = Unirest.post(PYTHON_SERVICE_URL)
                .header("Content-Type", "application/json")
                .body(sourceData)
                .asString();
        
        if (response.getStatus() != 200) {
            throw new IOException("Failed to forward data to Python service: " + response.getStatusText());
        }
        
        return response.getBody();
    }

    /**
     * Sends an error response to the client.
     * 
     * @param request the HttpServletRequest object
     * @param response the HttpServletResponse object
     * @param message the error message to be sent
     * @throws ServletException if there's an error forwarding the request
     * @throws IOException if there's an error writing the response
     */
    private void sendError(HttpServletRequest request, HttpServletResponse response, String message)
            throws ServletException, IOException {
        request.setAttribute("message", message);
        request.getRequestDispatcher("index.jsp").forward(request, response);
    }
}
