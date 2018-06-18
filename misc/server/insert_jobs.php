<?php
date_default_timezone_set("UTC");
require_once(dirname(__FILE__) . '/../lib/php/util.php');
$pdo = _get_connection();
#_info('inserting crawer_jobs...');

$action = _getArg('action', null);
if($action == 'initial'){
    $pdo->query("INSERT INTO crawler_jobs (type, priority, created_at, updated_at) values ('initial', 0, now(), now());");
}

#_info('Done.');
