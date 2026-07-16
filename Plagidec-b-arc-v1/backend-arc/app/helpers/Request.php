<?php
class Request {
    public static function method(): string {
        return strtoupper($_SERVER['REQUEST_METHOD']);
    }
    public static function uri(): string {
        return parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
    }
    public static function body(): array {
        $raw = file_get_contents('php://input');
        return json_decode($raw, true) ?? [];
    }
    public static function file(string $key): array|null {
        return $_FILES[$key] ?? null;
    }
}
