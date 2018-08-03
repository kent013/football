<?php
function action_worker($request, $response, $service) {

    $pdo = _get_connection();
    $id = $request->param('id');

    $results = $pdo->query("SELECT id, display_name FROM token_types");
    $results = $results->fetchAll(PDO::FETCH_ASSOC);
    $types = [];
    foreach($results as $result){
        $types[$result['display_name']] = $result;
    }

    $results = $pdo->query("SELECT id, display_name FROM token_relationship_types");
    $results = $results->fetchAll(PDO::FETCH_ASSOC);
    $rel_types = [];
    foreach($results as $result){
        $rel_types[$result['display_name']] = $result;
    }

    $client = getNeo4jConnection();
    $results = $client->run("MATCH (n) RETURN n");
    $records = $results->getRecords();

    $nodes = [];
    foreach($records as $record){
        $token = $record->get("n");
        $type = "Token";
        foreach($token->labels() as $label){
            if($type != $label){
                $type = $label;
                break;
            }
        }
        $nodes[] = ["id" => $token->identity(), "name" => $token->value("name"), "hash" => $token->value("hash"), "type" => $types[$type]];
    }

    $results = $client->run("MATCH (a)-[r]->(b) RETURN a, r, b");
    $records = $results->getRecords();

    $links = [];
    foreach($records as $record){
        $start = $record->get("a");
        $end = $record->get("b");
        $relation = $record->get("r");
        $links[] = ["id" => $relation->identity(), "source" => $start->value("hash"), "target" => $end->value("hash"), "value" => 1, "type" => $rel_types[$relation->type()]];
    }

    return $response->json(['nodes' => $nodes, 'links' => $links]);
}
