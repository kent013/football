<?php
use JasonGrimes\Paginator;

function action_worker($request, $response, $service) {
    $pdo = _get_connection();

    $hash = $request->param('hash', null);
    $result = $pdo->query("SELECT a.*, f.title AS site_title, f.site_url, f.language, f.site_category_id, f.site_type_id, ac.primary_image_url FROM articles AS a, feeds AS f, article_contents AS ac WHERE f.id = a.feed_id AND ac.article_hash = a.hash AND a.hash = '$hash'");
    $article = $result->fetch();
    if(!$article){
        return $response->redirect('/', 302)->send();
    }
    $article["thumbnail_url"] = getImageURL($article);

    $itemsPerPage = getSettings("related.similar_items_per_item");
    $results = $pdo->query("SELECT a.*, f.title AS site_title, f.site_url, f.language, f.site_category_id, f.site_type_id, ac.primary_image_url FROM similar_articles AS sa, articles AS a, feeds AS f, article_contents AS ac WHERE sa.article_hash = '{$article['hash']}' AND sa.similar_article_hash = a.hash AND f.id = a.feed_id AND ac.article_hash = a.hash ORDER BY a.published_at DESC LIMIT " . $itemsPerPage);
    $similar_articles = $results->fetchAll();
    if(!$similar_articles){
        $similar_articles = [];
    }
    foreach($similar_articles as $i => $similar_article){
        $similar_articles[$i]["thumbnail_url"] = getImageURL($similar_article);
    }

    return render_template("related", ["article" => $article, "similar_articles" => $similar_articles]);
}
