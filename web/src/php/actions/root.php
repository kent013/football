<?php
use JasonGrimes\Paginator;

function action_worker($request, $response, $service) {
    $pdo = _get_connection();

    $page = $request->param('page', 1);

    $result = $pdo->query("SELECT count(a.id) FROM articles AS a, article_contents AS ac WHERE ac.article_hash = a.hash");
    $result = $result->fetch();
    $itemsPerPage = getSettings("root.items_per_page");
    $totalItems = $result[0];
    $currentPage = $page;

    $results = $pdo->query("SELECT a.*, f.title AS site_title, f.site_url, f.language, f.site_category_id, f.site_type_id, ac.primary_image_url FROM articles AS a, feeds AS f, article_contents AS ac WHERE f.id = a.feed_id AND ac.article_hash = a.hash ORDER BY a.published_at DESC LIMIT " . $itemsPerPage . " OFFSET " . (($currentPage - 1)* $itemsPerPage));
    $articles = $results->fetchAll();

    $similarItemsPerItem = getSettings("root.similar_items_per_item");
    foreach($articles as $k => $article){
        $articles[$k]["thumbnail_url"] = getImageURL($article);

        $s_results = $pdo->query("SELECT a.*, f.title AS site_title, f.site_url, f.language, f.site_category_id, f.site_type_id, ac.primary_image_url FROM similar_articles AS sa, articles AS a, feeds AS f, article_contents AS ac WHERE sa.article_hash = '{$article['hash']}' AND sa.similar_article_hash = a.hash AND f.id = a.feed_id AND ac.article_hash = a.hash ORDER BY a.published_at DESC LIMIT {$similarItemsPerItem}");
        $similar_articles = $s_results->fetchAll();
        foreach($similar_articles as $i => $similar_article){
            $similar_articles[$i]["thumbnail_url"] = getImageURL($similar_article);
        }
        $articles[$k]["similar_articles"] = $similar_articles;
    }
    $urlPattern = '/(:num)';

    $paginator = new Paginator($totalItems, $itemsPerPage, $currentPage, $urlPattern);
    $paginator->setMaxPagesToShow(6);
    return render_template("index", ["articles" => $articles, "paginator" => $paginator]);
}
