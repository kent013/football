<?php
use JasonGrimes\Paginator;

function action_worker($request, $response, $service) {
    $pdo = _get_connection();
    $results = $pdo->query("SELECT * FROM token_types ORDER BY id");
    $token_types = $results->fetchAll(PDO::FETCH_ASSOC);
    $results = $pdo->query("SELECT * FROM token_relationship_types ORDER BY id");
    $token_replationship_types = $results->fetchAll(PDO::FETCH_ASSOC);
    return render_template("admin/index", ["token_types" => $token_types, "token_relationship_types" => $token_replationship_types]);
}
