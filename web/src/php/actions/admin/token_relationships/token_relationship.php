<?php
use JasonGrimes\Paginator;
use GraphAware\Neo4j\Client\ClientBuilder;

function action_worker($request, $response, $service) {
    $pdo = _get_connection();
    $subject_token_id = $request->param('subject_token_id');
    $object_token_id = $request->param('object_token_id');

    $subject_token = get_token_by_id($subject_token_id);
    $object_token = get_token_by_id($object_token_id);

    try{
        $client = _get_neo4j_connection();
        $tx = $client->transaction();
        $result = $tx->run("MATCH (a:Token)-[r]->(b:Token) WHERE a.hash = {subject_hash} AND b.hash = {object_hash} RETURN r", ['subject_hash' => $subject_token['hash'], 'object_hash' => $object_token['hash']]);
        $records = $result->getRecords();

        if(empty($records)){
            return $response->json(["success" => 1, "message" => "empty"]);
        }else{
            $record = $records[0];
            $relation = $record->get(r);
            $result = $relation->values();
            $result['id'] = $relation->identity();
            $result['type'] =  get_token_relationship_type_by_display_name($relation->type());
            $result['subject_token'] = $subject_token;
            $result['object_token'] = $object_token;
            return $response->json(["success" => 1, "token_relationship" => $result]);
        }

        $tx->commit();
    }catch(Exception $e){
        return $response->json(["success => 0", "message" => $e->getMessage()]);
    }

    return $response->json($token);
}
