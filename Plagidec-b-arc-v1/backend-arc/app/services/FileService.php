<?php
class FileService {
    private static string $uploadDir = '';

    public static function init(): void {
        self::$uploadDir = getenv('UPLOAD_DIR') ?: ROOT . '/storage/uploads';
        if (!is_dir(self::$uploadDir)) mkdir(self::$uploadDir, 0755, true);
    }

    public static function upload(array $file): array {
        self::init();
        $allowed = ['application/pdf','text/plain','application/msword',
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];

        if (!in_array($file['type'], $allowed)) {
            throw new RuntimeException('Tipo de archivo no permitido');
        }
        if ($file['size'] > 10 * 1024 * 1024) {
            throw new RuntimeException('El archivo supera 10MB');
        }

        $ext      = pathinfo($file['name'], PATHINFO_EXTENSION);
        $filename = uniqid('file_', true) . '.' . $ext;
        $dest     = self::$uploadDir . '/' . $filename;

        if (!move_uploaded_file($file['tmp_name'], $dest)) {
            throw new RuntimeException('Error al guardar el archivo');
        }

        return ['name' => $file['name'], 'path' => $dest,
                'mime' => $file['type'], 'size' => $file['size']];
    }

    public static function remove(string $path): void {
        if (file_exists($path)) unlink($path);
    }
}
