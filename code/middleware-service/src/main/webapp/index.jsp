<%@page contentType="text/html" pageEncoding="UTF-8"%>
<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <title>Data Migration Tool</title>
        <!-- Local stylesheet -->
        <link rel="stylesheet" type="text/css" href="css/style.css">
        <!-- jQuery -->
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
        <!-- Local scripts -->
        <script src="js/script.js"></script>
    </head>
    <body>
        <div id="header">
            <h1>Data Migration Tool</h1>
        </div>
        <div id="selection">
            <h3>Select a table to migrate to your local database:</h3>
            <div id="table-container"></div>
        </div>
        <div id="stage">
            <p id="message" class="${status}">${message}</p>
        </div>
    </body>
</html>
