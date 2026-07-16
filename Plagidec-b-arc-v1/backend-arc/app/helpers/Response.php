<?php
class Response {
    public static function json(mixed $data, int $status = 200): void {
        http_response_code($status);
        header('Content-Type: application/json');
        echo json_encode($data);
        exit;
    }
    public static function success(mixed $data = null, string $msg = 'OK'): void {
        self::json(['success' => true, 'message' => $msg, 'data' => $data]);
    }
    public static function error(string $msg, int $status = 400): void {
        self::json(['success' => false, 'message' => $msg], $status);
    }
    public static function notFound(string $msg = 'Not found'): void {
        self::error($msg, 404);
    }
}
