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
        <div class="container">
            <div id="header">
                <h1>Data Migration Tool</h1>
            </div>
            <div id="selection">
                <h3>Select a table to migrate to your local database:</h3>
                <div id="table-container"></div>
            </div>
            <div id="stage">
                <p id="message"></p>
            </div>
            <div id="footer">
                <div class="practical-info">
                    <h4>Practical information</h4>
                    <p>You don't need to worry about creating a PostgreSQL database: the Python server, which can be started by launching <i>run.py</i> from the <i>destination-service</i> project folder, will take care of it.</p>
                    <p>Please just ensure you don't currently own a database named '<b>target_db</b>' by looking at pgAdmin 4's Object Explorer section (inside Servers\PostgreSQL 17\Databases for the latest Postgres release).</p>
                </div>
                <div class="copyright"></div>
            </div>
        </div>
    </body>
</html>
