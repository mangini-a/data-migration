<?php
require_once('../config/config.php');

header('Content-Type: application/json');

try {
    // Get the requested table's name from the query parameter
    $tableName = isset($_GET['table']) ? $_GET['table'] : null;

    if (is_null($tableName)) {
        throw new Exception("Table name is required");
    }

    // List of allowed tables for security
    $allowedTables = [
        'domanda',
        'partecipazione',
        'quiz',
        'risposta',
        'risposta_utente_quiz',
        'utente'
    ];

    if (!in_array($tableName, $allowedTables)) {
        throw new Exception("Invalid table name");
    }

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

    // Get the table's structure with data types
    $structureQuery = "DESCRIBE " . $tableName;
    $structureResult = $conn->query($structureQuery);
    $columns = [];
    $columnTypes = [];

    while ($row = $structureResult->fetch_assoc()) {
        $columns[] = $row['Field'];
        $columnTypes[$row['Field']] = $row['Type'];
    }

    // Fetch all the table's records
    $query = "SELECT * FROM " . $tableName;
    $result = $conn->query($query);

    if ($result === false) {
        throw new Exception("Query failed: " . $conn->error);
    }

    $data = $result->fetch_all(MYSQLI_ASSOC);

    // Send successful response
    echo json_encode([
        'status' => 'success',
        'table' => $tableName,
        'columns' => $columns,
        'columnTypes' => $columnTypes,
        'data' => $data
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
