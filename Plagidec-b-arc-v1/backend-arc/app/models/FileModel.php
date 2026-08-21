<?php
class FileModel {
    public static function all(): array {
        return getDB()
            ->query('SELECT * FROM uploads ORDER BY created_at DESC')
            ->fetchAll();
    }

    public static function find(int $id): array|false {
        $stmt = getDB()->prepare('SELECT * FROM uploads WHERE id = ?');
        $stmt->execute([$id]);
        return $stmt->fetch();
    }

    public static function create(string $name, string $path, string $mime, int $size): int {
        $stmt = getDB()->prepare(
            'INSERT INTO uploads (name, path, mime, size) VALUES (?, ?, ?, ?) RETURNING id'
        );
        $stmt->execute([$name, $path, $mime, $size]);
        return (int) $stmt->fetchColumn();
    }

    public static function update(int $id, string $name): bool {
        $stmt = getDB()->prepare('UPDATE uploads SET name = ? WHERE id = ?');
        return $stmt->execute([$name, $id]);
    }

    public static function delete(int $id): bool {
        $stmt = getDB()->prepare('DELETE FROM uploads WHERE id = ?');
        return $stmt->execute([$id]);
    }
}
