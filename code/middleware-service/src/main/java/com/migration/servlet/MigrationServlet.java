package com.migration.servlet;

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

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        // Get the the name of the table to be retrieved from the request parameter
        String tableName = request.getParameter("table");
                
        // Validate the request parameter's value
        if (tableName == null || tableName.trim().isEmpty()) {
            sendError(response, "Table name parameter is required");
            return;
        }
                
        try {
            // Fetch data from the PHP web service
            String sourceData = fetchFromPhpService(tableName);

            // request.setAttribute("sourceData", sourceData);
            // request.getRequestDispatcher("index.jsp").forward(request, response);
            // response.setContentType("text/html;charset=UTF-8");
                    
            // Forward the data to the Python web service
            String result = forwardToPythonService(sourceData);

            // Write the response (TO JSP)
            response.getWriter().write(result);

        } catch (Exception e) {
            sendError(response, "Error during migration: " + e.getMessage());
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
     * @param response the HttpServletResponse object
     * @param message the error message to be sent
     * @throws IOException if there's an error writing the response
     */
    private void sendError(HttpServletResponse response, String message) throws IOException {
        response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
        response.setContentType("text/html;charset=UTF-8");
        response.getWriter().write(message); // TO JSP
    }
}
