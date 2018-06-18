#!/bin/bash
SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`
source $SCRIPTPATH/config.sh
source $SCRIPTPATH/util.sh

servers=("fc1")

CMDNAME=`basename $0`

while getopts auplyc:s:t:g:n:f:v:i: OPT
do
  case $OPT in
    "u" ) FLG_UPDATE="TRUE" ;;
    "p" ) FLG_PROCESS="TRUE" ;;
    "a" ) FLG_CLEARPID="TRUE" ;;
    "l" ) FLG_SHOW_CRAWLER_SETTINGS="TRUE" ;;
    "t" ) FLG_TAILLOG="TRUE" ; VALUE_DATE="$OPTARG" ;;
    "g" ) FLG_GREP="TRUE"; VALUE_GREP="$OPTARG" ;;
    "s" ) FLG_SERVER="TRUE" ; VALUE_SERVER="$OPTARG" ;;
    "c" ) FLG_CATEGORY="TRUE" ; VALUE_CATEGORY="$OPTARG" ;;
    "n" ) FLG_DELAY="TRUE" ; VALUE_FLAG="$OPTARG" ;;
    "f" ) FLG_FLAG="TRUE" ; VALUE_FLAG="$OPTARG" ;;
    "v" ) FLG_VALUE="TRUE" ; VALUE_VALUE="$OPTARG" ;;
    "i" ) FLG_FILENAME="TRUE" ; VALUE_FILENAME="$OPTARG" ;;
    "y" ) FLG_YUM="TRUE" ;;
      * ) echo "Usage: $CMDNAME [-u] [-p] [-l] [-t] [-f FLAG] [-t DATE]" 1>&2
          exit 1 ;;
  esac
done

if [ "$FLG_UPDATE" = "TRUE" ]; then
  if [ "$FLG_SERVER" = "TRUE" ]; then
    update $VALUE_SERVER
  else
    for server in ${servers[@]}
    do
      update $server
    done
  fi
fi

if [ "$FLG_PROCESS" = "TRUE" ]; then
  if [ "$FLG_SERVER" = "TRUE" ]; then
    check_process $VALUE_SERVER
  else
    for server in ${servers[@]}
    do
      check_process $server
    done
  fi
fi

if [ "$FLG_TAILLOG" = "TRUE" ]; then
  if [ "$FLG_GREP" = "TRUE" ]; then
    if [ "$FLG_SERVER" = "TRUE" ]; then
      grep_log $VALUE_SERVER $VALUE_DATE $VALUE_GREP
    else
      for server in ${servers[@]}
      do
        grep_log $server $VALUE_DATE $VALUE_GREP
      done
    fi
  fi
fi

if [ "$FLG_TAILLOG" = "TRUE" ]; then
  if [ "$FLG_SERVER" = "TRUE" ]; then
    tail_log $VALUE_SERVER $VALUE_DATE
  else
    for server in ${servers[@]}
    do
      tail_log $server $VALUE_DATE
    done
  fi
fi

if [ "$FLG_YUM" = "TRUE" ]; then
  if [ "$FLG_SERVER" = "TRUE" ]; then
    yum $VALUE_SERVER
  else
    for server in ${servers[@]}
    do
      yum $server
    done
  fi
fi

if [ "$FLG_SHOW_CRAWLER_SETTINGS" = "TRUE" ]; then
  if [ "$FLG_SERVER" = "TRUE" ]; then
    show_crawler_settings $VALUE_SERVER
  else
    for server in ${servers[@]}
    do
      show_crawler_settings $server
    done
  fi
fi

if [ "$FLG_DELAY" = "TRUE" ]; then
  if [ "$FLG_SERVER" = "TRUE" ]; then
    update_flag $VALUE_SERVER $VALUE_FLAG DOWNLOAD_DELAY /var/repos/football/football/settings.py
  else
    for server in ${servers[@]}
    do
      update_flag $server $VALUE_FLAG DOWNLOAD_DELAY /var/repos/football/football/settings.py
    done
  fi
fi

if [ "$FLG_CLEARPID" = "TRUE" ]; then
  if [ "$FLG_SERVER" = "TRUE" ]; then
    clear_pid $VALUE_SERVER
  else
    for server in ${servers[@]}
    do
      clear_pid $server
    done
  fi
fi


if [ "$FLG_FLAG" = "TRUE" ]; then
  if [ "$FLG_VALUE" = "TRUE" ]; then
    if [ "$FLG_FILENAME" = "TRUE" ]; then
      if [ "$FLG_SERVER" = "TRUE" ]; then
        update_flag $VALUE_SERVER $VALUE_FLAG $VALUE_VALUE $VALUE_FILENAME
      else
        if [ "$FLG_CATEGORY" = "TRUE" ]; then
          targets=`eval echo '${'${VALUE_CATEGORY}_crawlers[@]}`
        else
          targets=${servers[@]}
        fi
        for server in ${targets[@]}
        do
          update_flag $server $VALUE_FLAG $VALUE_VALUE $VALUE_FILENAME
        done
      fi
    fi
  fi
fi
