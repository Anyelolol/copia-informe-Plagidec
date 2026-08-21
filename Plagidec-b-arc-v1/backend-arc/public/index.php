<?php
define('ROOT', dirname(__DIR__));
require_once ROOT . '/app/config/env.php';
require_once ROOT . '/app/config/db.php';
require_once ROOT . '/app/helpers/Response.php';
require_once ROOT . '/app/helpers/Request.php';
require_once ROOT . '/app/models/FileModel.php';
require_once ROOT . '/app/services/FileService.php';
require_once ROOT . '/app/controllers/FileController.php';
require_once ROOT . '/app/routes/api.php';
