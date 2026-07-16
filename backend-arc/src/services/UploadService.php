<?php
class UploadService {
    private static string $dir = '';

    private static function uploadDir(): string {
        if (self::$dir === '') {
            self::$dir = rtrim(getenv('UPLOAD_DIR') ?: __DIR__ . '/../../uploads', '/');
            if (!is_dir(self::$dir)) mkdir(self::$dir, 0775, true);
        }
        return self::$dir;
    }

    public static function guardar(array $file, int $uid): array {
        if ($file['error'] !== UPLOAD_ERR_OK) {
            throw new \RuntimeException("Error al subir archivo (código {$file['error']})");
        }
        $ext     = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
        $allowed = ['pdf', 'doc', 'docx', 'txt', 'odt'];
        if (!in_array($ext, $allowed, true)) {
            throw new \RuntimeException("Extensión no permitida: .$ext");
        }

        $name = sprintf('%d_%s_%s.%s', $uid, date('Ymd_His'), bin2hex(random_bytes(4)), $ext);
        $dest = self::uploadDir() . '/' . $name;

        if (!move_uploaded_file($file['tmp_name'], $dest)) {
            throw new \RuntimeException("No se pudo mover el archivo");
        }

        return [
            'nombre_archivo' => $file['name'],
            'tipo_documento' => $ext,
            'ruta_archivo'   => $dest,
            'hash_documento' => hash_file('sha256', $dest),
            'tamano_bytes'   => filesize($dest),
        ];
    }

    public static function leerTexto(string $ruta): string {
        $ext = strtolower(pathinfo($ruta, PATHINFO_EXTENSION));
        return match ($ext) {
            'pdf'   => (string)shell_exec('pdftotext ' . escapeshellarg($ruta) . ' - 2>/dev/null'),
            default => (string)file_get_contents($ruta),
        };
    }
}
