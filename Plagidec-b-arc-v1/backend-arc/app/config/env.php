<?php
$envFile = ROOT . '/.env';
if (!file_exists($envFile)) return;
foreach (file($envFile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) as $line) {
    if (str_starts_with(trim($line), '#')) continue;
    [$key, $val] = explode('=', $line, 2);
    putenv(trim($key) . '=' . trim($val));
}
