CREATE TABLE IF NOT EXISTS brukere (
    id INT AUTO_INCREMENT PRIMARY KEY,
    navn VARCHAR(255),
    epost VARCHAR(255),
    password VARBINARY(255),
    role ENUM('user', 'admin') DEFAULT 'user'
);