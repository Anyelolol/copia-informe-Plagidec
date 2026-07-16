-- Tabla de archivos subidos
CREATE TABLE IF NOT EXISTS uploads (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(255) NOT NULL,
    path       TEXT NOT NULL,
    mime       VARCHAR(100),
    size       INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
