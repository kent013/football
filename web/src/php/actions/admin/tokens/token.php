<?php
use JasonGrimes\Paginator;

function action_worker($request, $response, $service) {
    $pdo = _get_connection();
    $id = $request->param('id', null);
    $hash = $request->param('hash', null);

    if(is_null($id) && is_null($hash)){
        return $response->json(['success' => 0, 'message' => 'you must specify id or hash']);
    }
    $output = ["success" => 1, "token" => null];
    if(is_null($id)){
        $output["token"] = get_token_by_hash($hash, $pdo);
    }else{
        $output["token"] = get_token_by_id($id, $pdo);
    }
    try{
        $output["token"]["type"] = get_token_type_by_token($output["token"]);
    }catch(Exception $e){
    }
    return $response->json($output);
}
