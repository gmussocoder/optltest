CREATE TABLE IF NOT EXISTS ordenes (
    id SERIAL PRIMARY KEY,
    descripcion VARCHAR(200)
);

INSERT INTO ordenes (descripcion) VALUES
('Compra de libros'),
('Pedido de computadora'),
('Renovación de hosting');

