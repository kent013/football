<?php
use GraphAware\Neo4j\Client\ClientBuilder;

function action_worker($request, $response, $service)
{
    $pdo = _get_connection();
    $id = $request->param('id');

    $statement = $pdo->prepare("SELECT * FROM tokens WHERE id = :id");
    $statement->bindParam(':id', $id);
    $statement->execute();
    $token = $statement->fetch(PDO::FETCH_ASSOC);

    try{
        $client = getNeo4jConnection();
        $pdo->beginTransaction();
        $tx = $client->transaction();
        $tx->push("MATCH (n) WHERE n.hash = {hash} DELETE n", ['hash' => $token['hash']]);
        $statement = $pdo->prepare("UPDATE tokens SET hash = NULL WHERE id = :id");
        $statement->bindParam(':id', $id);
        $statement->execute();

        $tx->commit();
        $pdo->commit();
    }catch(Exception $e){
        $pdo->rollback();
        return $response->json(["success" => 0, "message" => $e->getMessage()]);
    }
    return $response->json(["success" => 1, 'id' => $id]);
}
