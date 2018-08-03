<?php
use JasonGrimes\Paginator;

function action_worker($request, $response, $service) {
    $pdo = _get_connection();
    $query = $request->param('term');
    $page = (int)$request->param('page', 0);
    $is_noise = $request->param('is_noise', null);
    $is_processed = $request->param('is_processed', null);
    $tokensPerPage = 25;

    $queries = [];
    $like_query = "";
    if($query){
        $queries[] = "t.base_form LIKE CONCAT('%', :query, '%')";
    }

    if($is_noise === "1"){
        $queries[] = "is_noise = 1";
    }else if($is_noise === "0"){
        $queries[] = "is_noise = 0";
    }

    if($is_processed === "1"){
        $queries[] = "t.hash IS NOT NULL";
    }else if($is_processed === "0"){
        $queries[] = "t.hash IS NULL";
    }

    $where = "";
    if(!empty($queries)){
        $where = " WHERE " . implode(" AND ", $queries);
    }

    $statement = $pdo->prepare("SELECT count(t.id) AS count FROM tokens AS t $where");
    if($query){
        $statement->bindParam(':query', $query);
    }
    $statement->execute();
    $result = $statement->fetch();
    $count = $result["count"];

    $statement = $pdo->prepare("SELECT * FROM tokens AS t $where ORDER BY occurrence_count DESC LIMIT $tokensPerPage OFFSET :page");
    if($query){
        $statement->bindParam(':query', $query);
    }
    $statement->bindValue(':page', $page * $tokensPerPage, PDO::PARAM_INT);
    $statement->execute();

    $results = $statement->fetchAll();
    $tokens = [];
    foreach($results as $result){
        $text = $result["base_form"] . " (" . $result["occurrence_count"]. ")";
        if(!is_null($result["hash"])){
            $text .= "*";
        }
        $tokens[] = ["id" => $result["id"], "text" => $text, "token" => $result];
    }

    $output = ["results" => $tokens];
    if($count > ($page + 1) * $tokensPerPage){
        $output["pagination"] = ["more" => true];
    }
    $output["count"] = $count;
    return $response->json($output);
}
