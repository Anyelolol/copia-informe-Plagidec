<?php
require_once __DIR__ . '/../config/db.php';

class UsuarioModel {

    public static function crear(array $d): array {
        $hash = password_hash($d['password'], PASSWORD_BCRYPT);
        $stmt = getDB()->prepare("
            INSERT INTO usuario (nombre, apellido, email, password_hash, rol)
            VALUES (?, ?, ?, ?, ?)
            RETURNING uid, nombre, apellido, email, rol, fecha_creacion, activo
        ");
        $stmt->execute([$d['nombre'], $d['apellido'], $d['email'], $hash, $d['rol'] ?? 'estudiante']);
        return $stmt->fetch();
    }

    public static function porEmail(string $email): ?array {
        $stmt = getDB()->prepare("SELECT * FROM usuario WHERE email = ? AND activo = TRUE");
        $stmt->execute([$email]);
        return $stmt->fetch() ?: null;
    }

    public static function porId(int $uid): ?array {
        $stmt = getDB()->prepare(
            "SELECT uid, nombre, apellido, email, rol, fecha_creacion, ultimo_acceso, activo
             FROM usuario WHERE uid = ?"
        );
        $stmt->execute([$uid]);
        return $stmt->fetch() ?: null;
    }

    public static function actualizarAcceso(int $uid): void {
        getDB()->prepare("UPDATE usuario SET ultimo_acceso = NOW() WHERE uid = ?")
               ->execute([$uid]);
    }

    public static function listar(): array {
        return getDB()
            ->query("SELECT uid, nombre, apellido, email, rol, fecha_creacion, ultimo_acceso, activo
                     FROM usuario ORDER BY fecha_creacion DESC")
            ->fetchAll();
    }

    public static function actualizar(int $uid, array $d): ?array {
        $fields = [];
        $vals   = [];
        foreach (['nombre', 'apellido', 'email', 'rol', 'activo'] as $f) {
            if (array_key_exists($f, $d)) {
                $fields[] = "$f = ?";
                $vals[]   = $d[$f];
            }
        }
        if (!empty($d['password'])) {
            $fields[] = "password_hash = ?";
            $vals[]   = password_hash($d['password'], PASSWORD_BCRYPT);
        }
        if (empty($fields)) return self::porId($uid);
        $vals[] = $uid;
        $stmt = getDB()->prepare(
            "UPDATE usuario SET " . implode(', ', $fields) . " WHERE uid = ?
             RETURNING uid, nombre, apellido, email, rol, fecha_creacion, ultimo_acceso, activo"
        );
        $stmt->execute($vals);
        return $stmt->fetch() ?: null;
    }

    public static function eliminar(int $uid): void {
        getDB()->prepare("UPDATE usuario SET activo = FALSE WHERE uid = ?")->execute([$uid]);
    }
}
