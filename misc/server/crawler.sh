#!/bin/bash -l
MASTER_PID_PATH=/var/log/crawler/mpid$1
CRAWLER_PID_PATH=/var/log/crawler/pid$1
PYTHON_PATH=/home/ec2-user/.pyenv/versions/3.5.4/bin
SCRIPT_PATH=/home/ec2-user/football/misc/server

if [ -e $MASTER_PID_PATH ]; then
  echo "process is running."
  cat $MASTER_PID_PATH
  exit
fi

touch $MASTER_PID_PATH
echo $$ > $MASTER_PID_PATH

while true
do
  if [ ! -e $CRAWLER_PID_PATH ]; then
    touch $CRAWLER_PID_PATH
    echo $$ > $CRAWLER_PID_PATH
    $PYTHON_PATH/python $PYTHON_PATH/scrapy \
      crawl all \
        -a pid_path=$CRAWLER_PID_PATH \
        -a notify=$CRAWLER_NOTIFY \
      2>&1 | \
      /usr/sbin/rotatelogs /var/log/crawler/crawllog_%Y%m%d 86400 &
      sleep 1
  fi
done
