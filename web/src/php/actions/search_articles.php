<?php
use JasonGrimes\Paginator;

function action_worker($request, $response, $service) {
    $pdo = _get_connection();

    $page = $request->param('page', 1);
    $query = $request->param('query', null);
    if($page < 1){
        $page = 1;
    }

    $queries = mb_split('\s', $query);
    $token = $queries[0];
    $token = get_original_token($token);
    $token_type = get_type_of_token($token);

    $aliases = get_aliases_of($query);
    $words = mb_split('\s', $query);
    $queries = $words;
    foreach($words as $word){
        $nodes = get_aliases_of($word);
        $aliases = [];
        foreach($nodes as $node){
            $aliases[] = $node->name;
        }
        $queries = array_merge($words, $aliases);
    }
    $queries = array_unique($queries);
    $query = implode(' ', $queries);

    $statement = $pdo->prepare("SELECT count(a.id) FROM articles AS a, article_contents AS ac WHERE ac.article_hash = a.hash AND MATCH(ac.extracted_content) AGAINST(:query)");
    $statement->bindParam(':query', $query);
    $statement->execute();
    $result = $statement->fetch();

    $itemsPerPage = getSettings("root.items_per_page");
    $totalItems = $result[0];
    $currentPage = $page;

    $statement = $pdo->prepare("SELECT a.*, f.title AS site_title, f.site_url, f.language, f.site_category_id, f.site_type_id, ac.primary_image_url FROM articles AS a, feeds AS f, article_contents AS ac WHERE f.id = a.feed_id AND ac.article_hash = a.hash AND MATCH(ac.extracted_content) AGAINST(:query) ORDER BY a.published_at DESC LIMIT " . $itemsPerPage . " OFFSET " . ($currentPage - 1) * $itemsPerPage);
    $statement->bindParam(':query', $query);
    $statement->execute();
    $articles = $statement->fetchAll();

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
    $urlPattern = "/search/$query/(:num)";

    $paginator = new Paginator($totalItems, $itemsPerPage, $currentPage, $urlPattern);
    $paginator->setMaxPagesToShow(6);
    $render_vars = ["articles" => $articles, "paginator" => $paginator];
    $template_name = "index";
    if($token_type == "Person"){
        $template_name = strtolower($token_type) . "_index";
    }

    return render_template($template_name, $render_vars);
}
