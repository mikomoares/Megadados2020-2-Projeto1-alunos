DROP TABLE IF EXISTS tasks;


DROP TABLE IF EXISTS users;
CREATE TABLE users (
    uuid BINARY(16) PRIMARY KEY,
    name NVARCHAR(64)
);




CREATE TABLE tasks (
    uuid BINARY(16) PRIMARY KEY,
    description NVARCHAR(1024),
    completed BOOLEAN,
    userID BINARY(16),
    FOREIGN KEY (userID) REFERENCES users(uuid)
);
