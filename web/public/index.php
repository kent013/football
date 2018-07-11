<?php
require_once(__DIR__ . '/../vendor/autoload.php');
require_once(__DIR__ . "/../src/php/web_util.php");

use JasonGrimes\Paginator;

$klein = new \Klein\Klein();
$klein->respond('GET', '/', action_root);
$klein->respond('GET', '/[i:page]?', action_root);
$klein->respond('GET', '/about', action_about);
$klein->respond('GET', '/related/[*:hash]', action_related);
$klein->respond('GET', '/search/[*:query]/[i:page]?', action_search);
$klein->dispatch();

function action_root($request, $response, $service) {
    return call_action_worker("root", $request, $response, $service);
}

function action_related($request, $response, $service){
    return call_action_worker("related", $request, $response, $service);
}

function action_about($request, $response, $service) {
    return call_action_worker("about", $request, $response, $service);
}

function action_search($request, $response, $service) {
    return call_action_worker("search", $request, $response, $service);
}
