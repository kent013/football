<?php
function get_token_by_id($token_id, $pdo = null){
    if(is_null($pdo)){
        $pdo =  _get_connection();
    }
    $statement = $pdo->prepare("SELECT * FROM tokens WHERE id = :id");
    $statement->bindParam(':id', $token_id);
    $statement->execute();
    $token = $statement->fetch(PDO::FETCH_ASSOC);
    return $token;
}

function get_token_by_hash($token_hash, $pdo = null){
    if(is_null($pdo)){
        $pdo =  _get_connection();
    }
    $statement = $pdo->prepare("SELECT * FROM tokens WHERE hash = :hash");
    $statement->bindParam(':hash', $token_hash);
    $statement->execute();
    $token = $statement->fetch(PDO::FETCH_ASSOC);
    return $token;
}

function get_token_type($type_id, $pdo = null){
    if(is_null($pdo)){
        $pdo =  _get_connection();
    }
    $statement = $pdo->prepare("SELECT id, display_name FROM token_types WHERE id = :id");
    $statement->bindParam(':id', $type_id);
    $statement->execute();
    $token_type = $statement->fetch(PDO::FETCH_ASSOC);
    return $token_type;
}
function get_token_type_by_display_name($display_name, $pdo = null){
    if(is_null($pdo)){
        $pdo =  _get_connection();
    }
    $statement = $pdo->prepare("SELECT id, display_name FROM token_types WHERE display_name = :display_name");
    $statement->bindParam(':display_name', $display_name);
    $statement->execute();
    $token_type = $statement->fetch(PDO::FETCH_ASSOC);
    return $token_type;
}

function get_token_relationship_type($type_id, $pdo = null){
    if(is_null($pdo)){
        $pdo =  _get_connection();
    }
    $statement = $pdo->prepare("SELECT id, display_name FROM token_relationship_types WHERE id = :id");
    $statement->bindParam(':id', $type_id);
    $statement->execute();
    $token_relationship_type = $statement->fetch(PDO::FETCH_ASSOC);
    return $token_relationship_type;
}

function get_token_relationship_type_by_display_name($display_name, $pdo = null){
    if(is_null($pdo)){
        $pdo =  _get_connection();
    }
    $statement = $pdo->prepare("SELECT id, display_name FROM token_relationship_types WHERE display_name = :display_name");
    $statement->bindParam(':display_name', $display_name);
    $statement->execute();
    $token_relationship_type = $statement->fetch(PDO::FETCH_ASSOC);
    return $token_relationship_type;
}

function get_token_type_by_token($token, $pdo = null){
    $client = _get_neo4j_connection();
    $tx = $client->transaction();
    $result = $tx->run("MATCH (n) WHERE n.hash = {hash} RETURN n", ['hash' => $token['hash']]);
    $record = $result->getRecord();
    $token = $record->get("n");
    $label = array_shift(array_filter($token->labels(), function($v){ return $v != "Token"; }));
    return get_token_type_by_display_name($label, $pdo);
}

function get_aliases_of($name){
    $names = mb_split('\s', $name);
    $client = _get_neo4j_connection();
    $result = $client->run("MATCH (a)-[r:AliasOf]-(b) WHERE b.name IN {names} RETURN a", ['names' => $names]);
    $records = $result->getRecords();
    $nodes = [];
    foreach($records as $record){
        $nodes[] = $record->get("a");
    }
    return $nodes;
}

function get_type_of_token($node){
    if(is_null($node)){
        return null;
    }
    foreach($node->labels() as $label){
        if($label != "Token"){
            return $label;
        }
    }
    return null;
}

function get_original_token($token){
    $client = _get_neo4j_connection();
    $result = $client->run("MATCH (a)-[:AliasOf]->(n) WHERE a.name = {name} RETURN n", ['name' => $token]);
    if($result->size() == 0){
        $result = $client->run("MATCH (n) WHERE n.name = {name} RETURN n", ['name' => $token]);
        if($result->size() == 0){
            return null;
        }
    }
    $record = $result->getRecord();

    return $record->get('n');
}