<?php
require_once('../config/config.php');

header('Access-Control-Allow-Origin: *');
header('Content-Type: application/json');

try {
    // Open a new connection to the MySQL server
    $conn = new mysqli(
        $dbConfig['hostname'],
        $dbConfig['username'],
        $dbConfig['password'],
        $dbConfig['database']
    );

    if ($conn->connect_error) {
        throw new Exception("Connection failed: " . $conn->connect_error);
    }

    // Fetch table names
    $query = "SHOW TABLES";
    $result = $conn->query($query);

    if ($result === false) {
        throw new Exception("Query failed: " . $conn->error);
    }

    $tables = [];
    while ($row = $result->fetch_array()) {
        $tables[] = $row[0];
    }

    // Send successful response
    echo json_encode([
        'status' => 'success',
        'tables' => $tables
    ]);

} catch (Exception $e) {
    // Handle any error
    http_response_code(500);
    echo json_encode([
        'status' => 'error',
        'message' => $e->getMessage()
    ]);

} finally {
    // Close the previously opened database connection
    if (isset($conn)) {
        $conn->close();
    }
}
