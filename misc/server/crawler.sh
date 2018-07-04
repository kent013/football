#!/bin/bash -l
PID_PATH=/var/log/crawler/pid$1
PYTHON_PATH=/home/ec2-user/.pyenv/versions/3.5.4/bin
SCRIPT_PATH=/home/ec2-user/football/misc/server

if [ -e $PID_PATH ]; then
  echo "process is running."
  cat $PID_PATH
  exit
fi

while true
do
  if [ ! -e $PID_PATH ]; then
    touch $PID_PATH
    echo $$ > $PID_PATH
    $PYTHON_PATH/python $PYTHON_PATH/scrapy
      crawl all \
        -a pid_path=$PID_PATH \
        -a notify=$CRAWLER_NOTIFY \
      2>&1 | \
      /usr/sbin/rotatelogs /var/log/crawler/crawllog_%Y%m%d 86400 &
  fi
done
