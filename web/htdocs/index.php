<?php
require_once(__DIR__ . '/../vendor/autoload.php');
require_once(__DIR__ . "/../../lib/php/util.php");

$klein = new \Klein\Klein();
$klein->respond('GET', '/', action_root);
$klein->dispatch();

function action_root() {
    $pdo = _get_connection();
    $results = $pdo->query("SELECT a.*, f.title AS site_title, f.site_url, f.language, f.site_category_id, f.site_type_id FROM articles AS a, feeds AS f WHERE f.id= a.feed_id ORDER BY a.published_at DESC LIMIT 500 ");
    $articles = $results->fetchAll();
    return render_template("index", ["articles" => $articles]);
}

function render_template($template, $vars){
    $webdir = __DIR__ . "/../";
    $loader = new Twig_Loader_Filesystem("$webdir/src/twig");
    $twig = new Twig_Environment($loader, array(
        'cache' => "$webdir/var/twig",
        'debug' => true
    ));
    $twig->addExtension(new Twig_Extensions_Extension_Text());
    $template = $twig->load("$template.twig");
    return $template->render($vars);
}
