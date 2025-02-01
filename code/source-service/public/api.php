<?php
require_once('../config/config.php');

header('Content-Type: application/json');

$conn = null;

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

    $result = $conn->query("SELECT * FROM utente");

    if ($result === false) {
        throw new Exception("Query failed: " . $conn->error);
    }

    $data = $result->fetch_all(MYSQLI_ASSOC);

    // Send successful response
    echo json_encode([
        'status' => 'success',
        'data' => $data
    ]);

} catch (Exception $e) {
    // Handle any errors
    http_response_code(500);
    echo json_encode([
        'status' => 'error',
        'message' => $e->getMessage()
    ]);

} finally {
    // Close connection if it was opened
    if ($conn !== null) {
        $conn->close();
    }
}
