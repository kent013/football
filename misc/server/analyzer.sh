#!/bin/bash -l
PID_PATH=/var/log/crawler/pid$1
PYTHON_BIN=/home/ec2-user/.pyenv/versions/3.5.4/bin/python
SCRIPT_PATH=/home/ec2-user/football/misc/server

if [ -e $PID_PATH ]; then
  echo "process is running."
  cat $PID_PATH
  exit
fi

touch $PID_PATH
echo $$ > $PID_PATH

while true
do
  $PYTHON_BIN $SCRIPT_PATH/extract_content.py 2>&1 | \
    /usr/sbin/rotatelogs /var/log/crawler/analyzelog_%Y%m%d 86400
  $PYTHON_BIN $SCRIPT_PATH/tokenize_content.py 2>&1 | \
    /usr/sbin/rotatelogs /var/log/crawler/analyzelog_%Y%m%d 86400
  $PYTHON_BIN $SCRIPT_PATH/training.py 2>&1 | \
    /usr/sbin/rotatelogs /var/log/crawler/analyzelog_%Y%m%d 86400
  $PYTHON_BIN $SCRIPT_PATH/calc_content_similarity.py 2>&1 | \
    /usr/sbin/rotatelogs /var/log/crawler/analyzelog_%Y%m%d 86400
  sleep 2
done
