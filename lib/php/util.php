<?php
function _create_min_max_queries($params){
    $queries = [];
    foreach($params as $p){
        $prefix = "r.";
        if(strpos($p, '.') !== FALSE){
            $prefix = '';
        }
        $np = preg_replace('/^[^.]+?\./', '', $p);
        $min = $np . "_min";
        $max = $np . "_max";
        if(_has_param($min) && !empty(_get_param($min, 0))){
            $queries[] = $prefix . "$p >= " . _get_param($min);
        }
        if(_has_param($max) && !empty(_get_param($max, 0))){
            $queries[] = $prefix . "$p <= " . _get_param($max);
        }
    }
    return $queries;
}
function _get_connection($tag = "DATABASE"){
    static $pdo = [];
    if(isset($pdo[$tag])){
        return $pdo[$tag];
    }

    $setting = file_get_contents(dirname(__FILE__) . '/../../football/settings.py');
    if(!preg_match('/' . $tag . ' = *\{(.+?)\}/ms', $setting, $regs)){
        _error('DATABASE setting does not exist');
    }
    if(!preg_match_all('/\'([^\']+)\' *: *\'([^\']*)\'/', $regs[1], $regs)){
        _error('could not parse setting');
    }
    $settings = [];
    foreach($regs[1] as $k => $v){
        $settings[$v] = $regs[2][$k];
    }

    $dsn = "";
    if($settings['drivername'] == 'postgres'){
        $dsn = "pgsql:dbname={$settings['database']} host={$settings['host']} port={$settings['port']}";
    }else if($settings['drivername'] == 'mysql'){
        $dsn = "mysql:host={$settings['host']};port={$settings['port']};dbname={$settings['database']};charset=utf8";
    }
    $pdo[$tag] = new PDO($dsn, $settings['username'], $settings['password']);
    $pdo[$tag]->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    return $pdo[$tag];
}
function _get_setting($name, $default = null){
    $setting = file_get_contents(dirname(__FILE__) . '/../../football/settings.py');
    if(!preg_match('/' . $name . ' = *(.+?)/', $setting, $regs)){
        return $default;
    }
    return $regs[1];
}
function _bind_param(&$stmt, $name){
    $value = _get_param($name);
    return $stmt->bindValue(':' . $name, $value);
}
function _bind_value(&$stmt, $name, $value){
    return $stmt->bindValue(':' . $name, $value);
}
function _get_param(){
    $args = func_get_args();
    $argc = count($args);
    $default = null;
    if($argc == 0){
        throw new Exception('at least 1 parameters expected');
    }
    if($argc > 1){
        $default = $args[1];
    }
    $name = $args[0];
    if(isset($_REQUEST[$name])){
        return $_REQUEST[$name];
    }

    if($argc == 1){
        _error("Parameter " . $name . " is required");
    }
    return $default;
}

function _has_param($name){
    return isset($_REQUEST[$name]);
}

function _db_error($msg = null){
    $db = _get_connection();
    var_dump($db->errorInfo());
    exit;
}
function _json_error($msg){
    _output_json(["error" => $msg]);
}
function _output_json($data){
    header("Content-Type: text/javascript; charset=utf-8");
    echo json_encode($data);
    exit;
}

function _getArgOrDie($name, $message){
    $value = _getArg($name, null);
    if(is_null($value)){
        _error($message);
    }
    return $value;
}

function _getArg($name, $default){
    foreach($_SERVER['argv'] as $k => $v){
        if(($v == "--" . $name || $v == "-" . $name) &&
        isset($_SERVER['argv'][$k + 1])){
            return $_SERVER['argv'][$k + 1];
        }
    }
    return $default;
}

function _findArg($name){
    return in_array("-" . $name, $_SERVER['argv']) || in_array("--" . $name, $_SERVER['argv']);
}

function _msg($msg, $indent = 0){
    $sp = '';
    for ($i = 0; $i < $indent; $i++){
        $sp .= '  ';
    }
    echo $sp . $msg . "\n";
}

function _info($msg, $indent = 0){
    $date = date('Y/m/d H:i:s');
    $msg = '[INFO] ' . $date . " : " . $msg;
    _msg($msg, $indent);
}

function _warn($msg, $indent = 0){
    $date = date('Y/m/d H:i:s');
    $msg = '[WARN] ' . $date . " : " . $msg;
    _msg($msg, $indent);
}

function _error($msg, $indent = 0){
    $date = date('Y/m/d H:i:s');
    $msg = '[FATAL] ' . $date . " : " . $msg;
    _exit($msg, $indent);
}

function _exit($msg, $indent = 0){
    _msg($msg, $indent);
    exit;
}
