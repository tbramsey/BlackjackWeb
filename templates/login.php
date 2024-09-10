<!DOCTYPE html>
<html>
<head>
    <title>Form Submission Confirmation</title>
</head>
<body>

<?php
function hashPassword($password) {
    return password_hash($password, PASSWORD_DEFAULT);
}
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = $_POST["username"];
    $password = $_POST["password"];
    $hashedPassword = hashPassword($password);
    echo "<h2>Form Submitted Successfully!</h2>";
    echo "<p>Username: $username</p>";
    echo "<p>Password: $hashedPassword</p>";
} else {
    echo "<h2>Error: Form Data Not Submitted</h2>";
}
?>

</body>
</html>
