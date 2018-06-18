#!/bin/sh -l
ssh_exec() {
  ssh $SSH_OPTION $1 $2
}

update() {
  echo "updating server" $1
  ssh_exec $1 "/var/repos/football/misc/server/update.sh -u" &
  if [ "$1" = "pv" ]; then
    ssh_exec $1 "/var/repos/football/misc/server/update.sh -g"
  fi
}

check_process() {
  echo 'checking python process on server' $1
  ssh_exec $1 'ps ax' | grep python
}

clear_pid() {
  echo 'clear pid file on server' $1
  ssh_exec $1 'rm /var/log/crawler/pid1'
  ssh_exec $1 'rm /var/log/crawler/pid2'
}


tail_log() {
  echo 'tail log' $1 $2
  ssh_exec $1 'tail -30 /var/log/crawler/crawllog_'$2
}

grep_log() {
  echo 'grep log' $1 $2
  ssh_exec $1 'grep '$3' /var/log/crawler/crawllog_'$2
}

yum() {
  echo 'yum update' $1
  ssh_exec $1 'sudo yum update -y' &
}

show_crawler_settings() {
  echo 'show settings' $1 $2
  ssh_exec $1 'crontab -l'
  ssh_exec $1 'cat ~/.bashrc' | grep CRAWLER
}

update_flag(){
  echo 'toggle viewer flag' $1 $2 $3
  ssh_exec $1 "/var/repos/football/misc/server/update.sh -f $2 -v $3 -i $4"
}
