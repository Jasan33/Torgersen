CREATE TABLE IF NOT EXISTS brukere (
    id INT AUTO_INCREMENT PRIMARY KEY,
    navn VARCHAR(255) unique,
    epost VARCHAR(255),
    password VARBINARY(255),
    role ENUM('user', 'admin') DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS arbeid (
    arbeid_id INT AUTO_INCREMENT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    navn VARCHAR(255),
    messages VARCHAR(380),
    bruker_id INT,
    FOREIGN KEY (navn) REFERENCES brukere(navn) ON DELETE CASCADE,
    FOREIGN KEY (bruker_id) REFERENCES brukere(id) ON DELETE CASCADE
);