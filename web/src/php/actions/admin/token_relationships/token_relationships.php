<?php
use JasonGrimes\Paginator;

function action_worker($request, $response, $service) {
    $pdo = _get_connection();
    $subject_token_id = $request->param('subject_token_id');
    $object_token_id = $request->param('object_token_id');

    $statement = $pdo->prepare("SELECT count(t.id) AS count FROM tokens AS t WHERE is_noise = :is_noise $check_node_query $like_query");
    if($query){
        $statement->bindParam(':query', $query);
    }
    $statement->bindPAram(':is_noise', $is_noise);
    $statement->execute();
    $result = $statement->fetch();
    $count = $result["count"];

    $statement = $pdo->prepare("SELECT * FROM tokens AS t WHERE is_noise = :is_noise $check_node_query $like_query ORDER BY occurrence_count DESC LIMIT $tokensPerPage OFFSET :page");
    if($query){
        $statement->bindParam(':query', $query);
    }
    $statement->bindValue(':page', $page * $tokensPerPage, PDO::PARAM_INT);
    $statement->bindPAram(':is_noise', $is_noise);
    $statement->execute();

    $results = $statement->fetchAll();
    $tokens = [];
    foreach($results as $result){
        $tokens[] = ["id" => $result["id"], "text" => $result["base_form"] . " (" . $result["occurrence_count"]. ")"];
    }

    $output = ["results" => $tokens];
    if($count > ($page + 1) * $tokensPerPage){
        $output["pagination"] = ["more" => true];
    }
    $output["count"] = $count;
    return $response->json($output);
}
