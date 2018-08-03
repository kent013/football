<?php
use GraphAware\Neo4j\Client\ClientBuilder;
use Ramsey\Uuid\Uuid;
use Ramsey\Uuid\Exception\UnsatisfiedDependencyException;

function action_worker($request, $response, $service)
{
    $pdo = _get_connection();
    $id = $request->param('id');
    $is_noise = $request->param('is_noise');
    $token_type = $request->param('token_type', 0);

    $statement = $pdo->prepare("SELECT * FROM tokens WHERE id = :id");
    $statement->bindParam(':id', $id);
    $statement->execute();
    $token = $statement->fetch(PDO::FETCH_ASSOC);

    if ($token['hash'] != null && $is_noise) {
        return $response->json(["success" => 0, "message" => "You cannot set as noise"]);
    }

    if ($is_noise || ($token_type == 0 && $token['hash'] == null)   ) {
        $statement = $pdo->prepare("UPDATE tokens SET is_noise = :is_noise WHERE id = :id");
        $statement->bindParam(':id', $id);
        $statement->bindValue(':is_noise', $is_noise, PDO::PARAM_INT);
        $statement->execute();
    } else {
        try{
            $client = getNeo4jConnection();
            $pdo->beginTransaction();
            $tx = $client->transaction();
            $statement = $pdo->prepare("SELECT * FROM token_types WHERE id = :id");
            $statement->bindParam(':id', $token_type);
            $statement->execute();
            $token_type = $statement->fetch(PDO::FETCH_ASSOC);
            $result = $tx->run("MATCH (n) WHERE n.hash = {hash} RETURN n", ['hash' => $token['hash']]);
            $records = $result->getRecords();
            if(empty($records)){
                $hash = Uuid::uuid4();
                $tx->push("CREATE (n:{$token_type['display_name']}:Token {hash: {hash}, name: {name} })", ['hash' => $hash, 'name' => $token['base_form']]);
                $statement = $pdo->prepare("UPDATE tokens SET hash = :hash WHERE id = :id");
                $statement->bindParam(':id', $id);
                $statement->bindParam(':hash', $hash);
                $statement->execute();
            }else{
                $record = $records[0];
                $node = $record->get('n');
                foreach($node->labels() as $label){
                    if($label == "Token"){
                        continue;
                    }
                    $tx->push("MATCH (n) WHERE n.hash = {hash} REMOVE n:$label", ['hash' => $token['hash']]);
                }
                $tx->push("MATCH (n) WHERE n.hash = {hash} SET n:{$token_type['display_name']}", ['hash' => $token['hash']]);
            }

            $tx->commit();
            $pdo->commit();
        }catch(Exception $e){
            $pdo->rollback();
            return $response->json(["success => 0", "message" => $e->getMessage()]);
        }
        return $response->json(["success" => 1]);
    }

    return $response->json(["success" => 1]);
}
