<?php
require_once(__DIR__ . '/../vendor/autoload.php');
require_once(__DIR__ . "/../../lib/php/util.php");
require_once(__DIR__ . "/../src/php/settings.php");

$klein = new \Klein\Klein();
$klein->respond('GET', '/', action_root);
$klein->respond('GET', '/about', action_about);
$klein->dispatch();

function action_root() {
    $pdo = _get_connection();
    $results = $pdo->query("SELECT a.*, f.title AS site_title, f.site_url, f.language, f.site_category_id, f.site_type_id, ac.primary_image_url FROM articles AS a, feeds AS f, article_contents AS ac WHERE f.id = a.feed_id AND ac.article_hash = a.hash ORDER BY a.published_at DESC LIMIT 100");
    $articles = $results->fetchAll();
    foreach($articles as $k => $article){
        $articles[$k]["thumbnail_url"] = getImageURL($article);

        $s_results = $pdo->query("SELECT a.*, f.title AS site_title, f.site_url, f.language, f.site_category_id, f.site_type_id, ac.primary_image_url FROM similar_articles AS sa, articles AS a, feeds AS f, article_contents AS ac WHERE sa.article_hash = '{$article['hash']}' AND sa.similar_article_hash = a.hash AND f.id = a.feed_id AND ac.article_hash = a.hash ORDER BY a.published_at DESC LIMIT 10");
        $similar_articles = $s_results->fetchAll();
        foreach($similar_articles as $i => $similar_article){
            $similar_articles[$i]["thumbnail_url"] = getImageURL($similar_article);
        }
        $articles[$k]["similar_articles"] = $similar_articles;
    }
    return render_template("index", ["articles" => $articles]);
}

function action_about() {
    return render_template("about");
}

function render_template($template, $vars = []){
    $webdir = __DIR__ . "/../";
    $loader = new Twig_Loader_Filesystem("$webdir/src/twig");
    $twig = new Twig_Environment($loader, array(
        'cache' => "$webdir/var/twig",
        'debug' => true
    ));
    $twig->addExtension(new Twig_Extensions_Extension_Text());
    $template = $twig->load("$template.twig");
    global $football_web_settings;
    return $template->render($vars + $football_web_settings);
}

function getImageURL($article){
    if(empty($article["primary_image_url"])){
        return "https://placeimg.com/50/50/animals";
    }else if(preg_match('/.gif$/', $article["primary_image_url"])){
        return $article["primary_image_url"];
    }
    $thumbnail_url = preg_replace('/https?:\/\//', '', $article["primary_image_url"]);
    preg_match('/(https?)/', $article["primary_image_url"], $regs);
    return "{$regs[1]}://rsz.io/{$thumbnail_url}?width=50&aspect=1";
}
