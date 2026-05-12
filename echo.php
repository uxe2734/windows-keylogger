<?php
header('Content-Type: text/html; charset=utf-8');

$file = 'messages.json';

$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (isset($data['message'])) {
    $messages = [];

    if (file_exists($file)) {
        $messages = json_decode(file_get_contents($file), true) ?: [];
    }

    $ip = $_SERVER['REMOTE_ADDR'];

    $messages[] = [
        'ip' => $ip,
        'message' => $data['message'],
        'time' => date('Y-m-d H:i:s')
    ];

    file_put_contents(
        $file,
        json_encode(
            $messages,
            JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT
        )
    );
}

if (file_exists($file)) {
    $messages = json_decode(file_get_contents($file), true);

    foreach ($messages as $msg) {
        echo "<div style='margin-bottom:20px;'>";
        echo "<b>[{$msg['time']}]</b><br>";
        echo "<b>IP:</b> {$msg['ip']}<br><br>";
        echo nl2br(htmlspecialchars($msg['message'], ENT_QUOTES, 'UTF-8'));
        echo "</div><hr>";
    }
}
?>