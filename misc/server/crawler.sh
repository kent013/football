#!/bin/bash -l
PID_PATH=/var/log/crawler/pid$1
if [ `ps ax | grep python | grep -v grep | wc | awk '{print $1}'` -ge 5 ]; then
  ps ax | egrep "python|football" | grep -v grep | awk '{print $1}' | xargs kill
  rm $PID_PATH
  exit
fi
cd /var/repos/football/

INTERVAL=60
START=$SECONDS
TIME_INTERVAL=`expr $INTERVAL / $CRAWLER_SEPARATION_COUNT`
while [ `expr $SECONDS - $START` -lt 60 ];
do
  sleep ` awk 'BEGIN{srand();print rand() * ('$TIME_INTERVAL'-'$TIME_INTERVAL'/2) + '$TIME_INTERVAL'/2}'`
  if [ ! -e $PID_PATH ]; then
    touch $PID_PATH
    echo $$ > $PID_PATH
    /home/ec2-user/.pyenv/versions/2.7.10/bin/python \
      /home/ec2-user/.pyenv/versions/2.7.10/bin/scrapy \
        crawl all \
          -a pid_path=$PID_PATH \
          -a notify=$CRAWLER_NOTIFY \
      2>&1 | \
      /usr/sbin/rotatelogs /var/log/crawler/crawllog_%Y%m%d 86400 &
  fi
done
