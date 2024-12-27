CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    image TEXT NOT NULL,
    category TEXT NOT NULL
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    username TEXT NOT NULL,
    text TEXT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products (id)
);

INSERT INTO products (name, price, image, category) VALUES
('Gaming PC Pro', 1200, 'images/pc1.webp', 'PCs'),
('Office PC', 800, 'images/pc22.webp', 'PCs'),
('Budget Gaming PC', 600, 'images/pc3.webp', 'PCs'),
('ASUS ROG Strix Z790-E ', 150, 'images/motherboard1.jpg', 'Motherboards'),
('MSI MPG B550 Gaming Edge', 200, 'images/motherboard2.webp', 'Motherboards'),
('Gigabyte A520 Aorus Elite ', 250, 'images/motherboard3.jpg', 'Motherboards'),
('Intel Core i9-12900K', 300, 'images/cpu1.jpg', 'CPUs'),
('AMD Ryzen 9 5900X', 350, 'images/cpu2.webp', 'CPUs'),
('Intel Core i5-12600K', 400, 'images/cpu3.webp', 'CPUs'),
('NVIDIA GeForce RTX 4090', 500, 'images/gpu1.png', 'GPUs'),
('AMD Radeon RX 7900 XT', 600, 'images/gpu2.webp', 'GPUs'),
('NVIDIA GeForce RTX 4060 Ti', 700, 'images/gpu3.webp', 'GPUs');
