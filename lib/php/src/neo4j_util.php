<?php
require_once(__DIR__ . "/util.php");
use GraphAware\Neo4j\Client\ClientBuilder;
function _get_neo4j_connection(){
    static $client = null;
    if(is_null($client)){
        $url = _get_setting("NEO4J_URL");
        $url = str_replace("bolt", "http", $url);
        $url = str_replace("7687", "7474", $url);
        $client = ClientBuilder::create()->addConnection('default', $url)->build();
    }
    return $client;
}