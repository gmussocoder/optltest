CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100)
);

INSERT INTO items (nombre) VALUES
('Item A'),
('Item B'),
('Item C');

