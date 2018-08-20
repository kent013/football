<?php
use GraphAware\Neo4j\Client\ClientBuilder;

function action_worker($request, $response, $service)
{
    $pdo = _get_connection();
    $id = $request->param('id', null);
    if(is_null($id) || preg_match('/^[0-9]+$/', $id) == false){
        return $response->json(['success' => 0, 'message' => 'id is invalid or not specified']);
    }

    try{
        $client = _get_neo4j_connection();
        $pdo->beginTransaction();
        $tx = $client->transaction();
        $result = $tx->push("MATCH ()-[r]-() WHERE ID(r) = {id} DELETE r", ['id' => (int)$id]);
        $tx->commit();
    }catch(Exception $e){
        return $response->json(["success => 0", "message" => $e->getMessage()]);
    }
    return $response->json(["success" => 1, 'id' => $id]);
}
