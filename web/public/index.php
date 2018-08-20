<?php
require_once(__DIR__ . '/../vendor/autoload.php');
require_once(__DIR__ . "/../src/php/web_util.php");
require_once(__DIR__ . "/../src/php/db_util.php");
require_once(__DIR__ . "/../../lib/php/src/neo4j_util.php");

use JasonGrimes\Paginator;

$klein = new \Klein\Klein();
$klein->respond('GET', '/', 'action_root');
$klein->respond('GET', '/[i:page]?', 'action_root');
$klein->respond('GET', '/about', 'action_about');
$klein->respond('GET', '/related/[*:hash]', 'action_related_articles');
$klein->respond('GET', '/search/[*:query]/[i:page]?', 'action_search_articles');
$klein->respond('GET', '/admin/', 'action_admin');
$klein->respond('GET', '/admin/tokens', 'action_admin_tokens');
$klein->respond('GET', '/admin/token', 'action_admin_token');
$klein->respond('POST', '/admin/token', 'action_admin_patch_token');
$klein->respond('DELETE', '/admin/token', 'action_admin_delete_token');
$klein->respond('GET', '/admin/token_relationships', 'action_admin_token_relationships');
$klein->respond('GET', '/admin/token_relationship', 'action_admin_token_relationship');
$klein->respond('POST', '/admin/token_relationship', 'action_admin_patch_token_relationship');
$klein->respond('DELETE', '/admin/token_relationship', 'action_admin_delete_token_relationship');
$klein->respond('GET', '/admin/graph', 'action_admin_graph');
$klein->dispatch();

function action_root($request, $response, $service) {
    return call_action_worker("root", $request, $response, $service);
}

function action_related_articles($request, $response, $service){
    return call_action_worker("related_articles", $request, $response, $service);
}

function action_about($request, $response, $service) {
    return call_action_worker("about", $request, $response, $service);
}

function action_search_articles($request, $response, $service) {
    return call_action_worker("search_articles", $request, $response, $service);
}

function action_admin($request, $response, $service) {
    return call_admin_action_worker("admin/root", $request, $response, $service);
}

function action_admin_tokens($request, $response, $service) {
    return call_admin_action_worker("admin/tokens/tokens", $request, $response, $service);
}
function action_admin_token($request, $response, $service) {
    return call_admin_action_worker("admin/tokens/token", $request, $response, $service);
}
function action_admin_patch_token($request, $response, $service) {
    return call_admin_action_worker("admin/tokens/patch_token", $request, $response, $service);
}
function action_admin_delete_token($request, $response, $service) {
    return call_admin_action_worker("admin/tokens/delete_token", $request, $response, $service);
}

function action_admin_token_relationships($request, $response, $service) {
    return call_admin_action_worker("admin/token_relationships/token_relationships", $request, $response, $service);
}
function action_admin_token_relationship($request, $response, $service) {
    return call_admin_action_worker("admin/token_relationships/token_relationship", $request, $response, $service);
}
function action_admin_patch_token_relationship($request, $response, $service) {
    return call_admin_action_worker("admin/token_relationships/patch_token_relationship", $request, $response, $service);
}
function action_admin_delete_token_relationship($request, $response, $service) {
    return call_admin_action_worker("admin/token_relationships/delete_token_relationship", $request, $response, $service);
}
function action_admin_graph($request, $response, $service) {
    return call_admin_action_worker("admin/graph/graph", $request, $response, $service);
}