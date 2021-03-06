<?php
require_once(__DIR__ . "/../../../lib/php/src/util.php");
require_once(__DIR__ . "/settings.php");

function call_action_worker($name, $request, $response, $service){
    require_once(__DIR__ . "/actions/{$name}.php");
    try{
        return action_worker($request, $response, $service);
    }catch(Exception $e){
        var_dump($e);
    }
}

function call_admin_action_worker($name, $request, $response, $service){
    if(!auth_admin()){
        header('Content-Type: text/plain; charset=utf-8');
        die('ログインが必要です');
    }
    return call_action_worker($name, $request, $response, $service);
}

function auth_admin(){
    header('WWW-Authenticate: Basic realm="Enter username and password."');
    if(!isset($_SERVER['PHP_AUTH_USER'], $_SERVER['PHP_AUTH_PW'])){
        return false;
    }
    if($_SERVER['PHP_AUTH_USER'] !== getSettings('admin.username')){
        return false;
    }
    if($_SERVER['PHP_AUTH_PW'] !== getSettings('admin.password')){
        return false;
    }
    return true;
}

function render_template($template, $vars = []){
    $webdir = __DIR__ . "/../../";
    $loader = new Twig_Loader_Filesystem("$webdir/src/twig");
    $twig = new Twig_Environment($loader, array(
        'cache' => "$webdir/var/twig",
        'debug' => true
    ));
    $twig->addExtension(new Twig_Extensions_Extension_Text());
    $template = $twig->load("$template.twig");
    return $template->render($vars + getSettings());
}

function getImageURL($article){
    if(empty($article["primary_image_url"])){
        return "https://placeimg.com/50/50/animals?rand=" . rand(0, 100);
    }else if(preg_match('/.gif$/', $article["primary_image_url"])){
        return "https://images1-focus-opensocial.googleusercontent.com/gadgets/proxy?url=" . urlencode($article["primary_image_url"]) ."&container=focus";
    }
    $thumbnail_url = preg_replace('/https?:\/\//', '', $article["primary_image_url"]);
    $thumbnail_url = urlencode($thumbnail_url);
    return "https://images.weserv.nl/?url={$thumbnail_url}&w=50&h=50&t=square";
}

function getSettings($key = null){
    global $football_web_settings;
    if(is_null($key)){
        return $football_web_settings;
    }
    return $football_web_settings[$key];
}