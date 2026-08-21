<?php
class FileController {
    // GET /api/files
    public static function index(): void {
        Response::success(FileModel::all());
    }

    // GET /api/files/:id
    public static function show(int $id): void {
        $file = FileModel::find($id);
        if (!$file) Response::notFound('Archivo no encontrado');
        Response::success($file);
    }

    // POST /api/files
    public static function store(): void {
        $uploaded = Request::file('file');
        if (!$uploaded) Response::error('No se recibió ningún archivo');

        try {
            $data = FileService::upload($uploaded);
            $id   = FileModel::create($data['name'], $data['path'], $data['mime'], $data['size']);
            Response::success(['id' => $id, ...$data], 'Archivo subido');
        } catch (RuntimeException $e) {
            Response::error($e->getMessage());
        }
    }

    // PATCH /api/files/:id
    public static function update(int $id): void {
        $file = FileModel::find($id);
        if (!$file) Response::notFound('Archivo no encontrado');

        $body = Request::body();
        $name = trim($body['name'] ?? '');
        if (!$name) Response::error('El campo name es requerido');

        FileModel::update($id, $name);
        Response::success(null, 'Archivo actualizado');
    }

    // DELETE /api/files/:id
    public static function destroy(int $id): void {
        $file = FileModel::find($id);
        if (!$file) Response::notFound('Archivo no encontrado');

        FileService::remove($file['path']);
        FileModel::delete($id);
        Response::success(null, 'Archivo eliminado');
    }
}
