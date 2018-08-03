<?php
use GraphAware\Neo4j\Client\ClientBuilder;
use Ramsey\Uuid\Uuid;
use Ramsey\Uuid\Exception\UnsatisfiedDependencyException;

function action_worker($request, $response, $service)
{
    $pdo = _get_connection();
    $subject_token_id = $request->param('subject_token_id');
    $object_token_id = $request->param('object_token_id');
    $token_relationship_type_id = $request->param('token_relationship_type_id');
    $token_relationship_from = $request->param('token_relationship_from', null);
    $token_relationship_to = $request->param('token_relationship_to', null);

    $subject_token = get_token_by_id($subject_token_id);
    $object_token = get_token_by_id($object_token_id);

    if ($subject_token['hash'] == null){
        return $response->json(["success" => 0, "message" => "subject token in not saved in neo4j"]);
    }else if($object_token['hash'] == null) {
        return $response->json(["success" => 0, "message" => "object token in not saved in neo4j"]);
    }

    $token_relationship_type = get_token_relationship_type($token_relationship_type_id);

    try{
        $client = getNeo4jConnection();
        $tx = $client->transaction();
        $result = $tx->run("MATCH (a:Token)-[r:" . $token_relationship_type['display_name'] . "]-(b:Token) WHERE a.hash = {subject_hash} AND b.hash = {object_hash} RETURN r", ['subject_hash' => $subject_token['hash'], 'object_hash' => $object_token['hash']]);
        $records = $result->getRecords();

        if(empty($records)){
            $parameter = ['subject_hash' => $subject_token['hash'], 'object_hash' => $object_token['hash']];
            $attribute_query = [];
            if(!empty($token_relationship_from)){
                $attribute_query[] = "from: {from}";
                $parameter['from'] = $token_relationship_from;
            }
            if(!empty($token_relationship_to)){
                $attribute_query[] = "to: {to}";
                $parameter['to'] = $token_relationship_to;
            }
            $attribute_query = implode(",", $attribute_query);
            $tx->push("MATCH (a:Token), (b:Token) WHERE a.hash = {subject_hash} AND b.hash = {object_hash} CREATE (a)-[:" . $token_relationship_type['display_name'] . " { $attribute_query }]->(b)", $parameter);
        }else{
            $record = $records[0];
            $relation = $record->get(r);
            $parameter = ['id' => $relation->identity()];
            $attribute_query = [];
            if(!empty($token_relationship_from)){
                $attribute_query[] = "r.from = {from}";
                $parameter['from'] = $token_relationship_from;
            }
            if(!empty($token_relationship_to)){
                $attribute_query[] = "r.to = {to}";
                $parameter['to'] = $token_relationship_to;
            }
            $attribute_query = implode(",", $attribute_query);
            $tx->push("MATCH ()-[r]-() WHERE id(r) = {id} SET $attribute_query", $parameter);
        }

        $tx->commit();
    }catch(Exception $e){
        return $response->json(["success => 0", "message" => $e->getMessage()]);
    }

    return $response->json(["success" => 1]);
}
