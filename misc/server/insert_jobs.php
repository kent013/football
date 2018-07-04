<?php
date_default_timezone_set("UTC");
require_once(__DIR__ . '/../../lib/php/util.php');
$pdo = _get_connection();
#_info('inserting crawer_jobs...');

$action = _getArg('action', null);
if($action == 'initial'){
    $result = $pdo->query("SELECT count(id) FROM crawler_jobs AS c WHERE c.started_at IS NULL AND c.type = 'initial'");
    $result = $result->fetch();
      if((int)$result[0] > 0){
        return;
    }
    $pdo->query("INSERT INTO crawler_jobs (type, priority, created_at, updated_at) values ('initial', 0, now(), now());");
}

#_info('Done.');
