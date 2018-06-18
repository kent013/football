<?php
require_once(__DIR__ . '/../lib/php/util.php');


function _execAWSCommand($command){
    exec($command, $result);
    $result = implode($result, "\n");
    $result = json_decode($result, true);
    return $result;
}

function _listInstanceIds($filter){
    $command = <<< EOC
aws ec2 describe-tags \
  --filters "Name=resource-type,Values=instance" \
            "Name=key,Values=Name" \
            "Name=tag-value,Values={$filter}" \
  --query "Tags[*]" \
  --output json
EOC;
    return _execAWSCommand($command);
}

function _listIpAddresses($instances){
    $ids = [];
    foreach($instances as $i){
        $ids[] = $i['ResourceId'];
    }
    $ids = implode('" "', $ids);
    $command = <<< EOC
aws ec2 describe-instances \
  --instance-ids "{$ids}" \
  --query "Reservations[].Instances[]" \
  --output json
EOC;
    $results = _execAWSCommand($command);
    $instances = [];
    foreach($results as $r){
        $instances[] = ['ip' => isset($r['PublicIpAddress']) ? $r['PublicIpAddress'] : '', 'id' => $r['InstanceId'], 'name' => $r['Tags'][0]['Value'], 'data' => $r];
    }
    usort($instances, function($a, $b){
        return strcmp($a['name'], $b['name']);
    });
    return $instances;
}

function _stopIntances($instances){
    $ids = _getInstanceIds($instances);
    $command = <<< EOC
aws ec2 stop-instances \
  --instance-ids "{$ids}" \
EOC;
    return _execAWSCommand($command);
}

function _startIntances($instances){
    $ids = _getInstanceIds($instances);
    $command = <<< EOC
aws ec2 start-instances \
  --instance-ids "{$ids}" \
EOC;
    return _execAWSCommand($command);
}

function _getInstanceIds($instances){
    $ids = [];
    foreach($instances as $i){
        $ids[] = $i['id'];
    }
    return implode('" "', $ids);
}

function _listInstances($filter){
    $ids = _listInstanceIds($filter);
    return _listIpAddresses($ids);

}

$instances = _listInstances('property_*,football_crawler*,pms_conductor');
$names = [];

$resolver = [
    'football_crawler_1' => ['alias' => 'fc1', 'key' => 'kentaro.pem']
];

$category = _getArg('category', null);
$group = _getArg('group', null);
$alias = _getArg('alias', null);
$name = _getArg('name', null);

$targets = [];
foreach($instances as $k => $i){
    if(!isset($resolver[$i['name']])){
        continue;
    }
    $instances[$k] = $i + $resolver[$i['name']];
}
foreach($instances as $i){
    if(!is_null($name) && preg_match('/' . $name . '/', $i['name'])){
        $targets[] = $i;
    }else if(!is_null($alias) && preg_match('/' . $alias . '/', $i['alias'])){
        $targets[] = $i;
    }
}

usort($targets, function($a, $b)
{
    if ($a['alias'] == $b['alias'])
    {
        return 0;
    }
    else if ($a['alias'] > $b['alias'])
    {
        return -1;
    }
    else {
        return 1;
    }
});

$action = _getArg('action', null);
$interval = (int)_getArg('interval', 10);
if($action == 'ssh'){
    $template = <<<EOT
Host %s
  Hostname %s
  User ec2-user
  Port 22
  UserKnownHostsFile /dev/null
  StrictHostKeyChecking no
  PasswordAuthentication no
  IdentityFile ~/.ssh/%s
  IdentitiesOnly yes
  LogLevel FATAL%s
EOT;
    $configs = [];
    foreach($targets as $target){
        $options = "";
        if(empty($target['ip'])){
            continue;
        }
        if(isset($target['ssh-options'])){
            $options = [];
            foreach($target['ssh-options'] as $o){
                $options[] = '  ' . $o;
            }
            $options = "\n" . implode("\n", $options);
        }
        $configs[] = sprintf($template, $target['alias'], $target['ip'], $target['key'], $options);
    }
    echo implode("\n", $configs) . "\n";
}else if($action == 'dump'){
    var_dump($targets);
}else if($action == 'status'){
    foreach($targets as $t){
        echo "{$t['alias']}:{$t['data']['LaunchTime']}, {$t['data']['State']['Name']}\n";
    }
}else if($action == "start"){
    $result = _startIntances($targets);
}else if($action == "stop"){
    $result = _stopIntances($targets);
}else if($action == "round-robin-restart"){
    $startInstance = false;
    foreach($targets as $t){
        if($t['data']['State']['Name'] == "stopped"){
            $result = _startIntances([$t]);
            echo 'starting ' . $t['alias'] . "\n";
            $startInstance = true;
        }
    }
    if($startInstance){
        echo "instance is started";
        return;
    }
    date_default_timezone_set("UTC");
    $count = count($targets);
    $time = 180 / $count;
    $date = getdate();
    $minute = $date['hours'] * 60 + $date['minutes'];
    $index = floor($minute / $time) % $count;
    $target = $targets[$index];
    $elapsed = time() - strtotime($target['data']['LaunchTime']);
    if($elapsed / 60 / 60 > $interval){
        _stopIntances([$target]);
        echo 'stopping ' . $target['alias'] . "\n";
    }
}
?>
