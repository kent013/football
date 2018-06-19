<?php
require_once("../misc/lib/php/util.php");
$pdo = _get_connection();
$results = $pdo->query("SELECT * FROM articles AS a ORDER BY published_at DESC LIMIT 500 ");
$articles = $results->fetchAll(PDO::FETCH_ASSOC);

foreach($articles as $article){
   echo "<h3><a href='{$article['url']}' target='_blank'>{$article['title']}</a></h3>";
} 
