<?php
require_once __DIR__ . '/../middlewares/AuthMiddleware.php';
require_once __DIR__ . '/../models/UsuarioModel.php';
require_once __DIR__ . '/../models/LogModeloModel.php';

class UsuarioController {

    public static function listar(): void {
        AuthMiddleware::role(['admin']);
        echo json_encode(UsuarioModel::listar());
    }

    public static function obtener(int $uid): void {
        $payload = AuthMiddleware::require();
        if ($payload['rol'] !== 'admin' && $payload['uid'] !== $uid) {
            http_response_code(403); echo json_encode(['error' => 'Sin permisos']); return;
        }
        $u = UsuarioModel::porId($uid);
        if (!$u) { http_response_code(404); echo json_encode(['error' => 'No encontrado']); return; }
        echo json_encode($u);
    }

    public static function actualizar(int $uid): void {
        $payload = AuthMiddleware::require();
        if ($payload['rol'] !== 'admin' && $payload['uid'] !== $uid) {
            http_response_code(403); echo json_encode(['error' => 'Sin permisos']); return;
        }
        $body = json_decode(file_get_contents('php://input'), true) ?? [];
        if ($payload['rol'] !== 'admin') unset($body['rol']);

        $u = UsuarioModel::actualizar($uid, $body);
        if (!$u) { http_response_code(404); echo json_encode(['error' => 'No encontrado']); return; }
        LogSistemaModel::registrar('usuarios', 'INFO', "Usuario $uid actualizado", $payload['uid']);
        echo json_encode($u);
    }

    public static function eliminar(int $uid): void {
        AuthMiddleware::role(['admin']);
        UsuarioModel::eliminar($uid);
        LogSistemaModel::registrar('usuarios', 'WARNING', "Usuario $uid desactivado");
        echo json_encode(['mensaje' => 'Usuario desactivado']);
    }
}
