<?php
// Headers globales
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PATCH, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');

if (Request::method() === 'OPTIONS') { http_response_code(200); exit; }

$uri    = Request::uri();
$method = Request::method();

// GET /api/files
if ($uri === '/api/files' && $method === 'GET') {
    FileController::index();

// POST /api/files
} elseif ($uri === '/api/files' && $method === 'POST') {
    FileController::store();

// GET /api/files/:id
} elseif (preg_match('#^/api/files/(\d+)$#', $uri, $m) && $method === 'GET') {
    FileController::show((int)$m[1]);

// PATCH /api/files/:id
} elseif (preg_match('#^/api/files/(\d+)$#', $uri, $m) && $method === 'PATCH') {
    FileController::update((int)$m[1]);

// DELETE /api/files/:id
} elseif (preg_match('#^/api/files/(\d+)$#', $uri, $m) && $method === 'DELETE') {
    FileController::destroy((int)$m[1]);

// 404
} else {
    Response::notFound();
}
