CREATE DATABASE users;
\c users;

CREATE TABLE account(
    username VARCHAR(50) PRIMARY KEY,
    hashed_password VARCHAR(255) NOT NULL
);

INSERT INTO account (username, hashed_password) VALUES ('admin', '$2y$10$Fxi.qVv8Y9jK9ivO1xJN8OyRgK9gZfQNhYWimSnjToK2L0xcY6h/.');
INSERT INTO account (username, hashed_password) VALUES ('other', '$2y$10$ARSTZKmiD5JXhaae9FolAuy06KJGHupFgjWei4ucW2gUGLbywo1HC');