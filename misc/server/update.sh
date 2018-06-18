#!/bin/bash -l
update() {
  cd /var/repos/football
  git pull origin master
}

uglify() {
  nvm use stable
  uglifyjs /var/repos/football/web/property_analytics_viewer/js/index.js -c -m -o /var/repos/football/web/property_analytics_viewer/js/index.min.js
  uglifycss /var/repos/football/web/property_analytics_viewer/css/index.css > /var/repos/football/web/property_analytics_viewer/css/index.min.css
}

update_config_file(){
  sed "s/$1 *= *.\+/$1=$2/" -i $3
  cat $3 | grep $1
}
CMDNAME=`basename $0`

while getopts ugf:i:v: OPT
do
  case $OPT in
    "u" ) FLG_UPDATE="TRUE" ;;
    "g" ) FLG_UGLIFY="TRUE" ;;
    "f" ) FLG_FLAGNAME="TRUE" ; VALUE_FLAGNAME="$OPTARG" ;;
    "v" ) FLG_VALUE="TRUE" ; VALUE_FLAG="$OPTARG" ;;
    "i" ) FLG_FILENAME="TRUE" ; VALUE_FILENAME="$OPTARG" ;;
      * ) echo "Usage: $CMDNAME [-u] [-g] [-s FLAG]" 1>&2
          exit 1 ;;
  esac
done

if [ "$FLG_UPDATE" = "TRUE" ]; then
  update
fi

if [ "$FLG_UGLIFY" = "TRUE" ]; then
  uglify
fi

if [ "$FLG_VALUE" = "TRUE" ]; then
  if [ "$FLG_FLAGNAME" = "TRUE" ]; then
    if [ "$FLG_FILENAME" = "TRUE" ]; then
      update_config_file $VALUE_FLAGNAME $VALUE_FLAG $VALUE_FILENAME
    fi
  fi
fi
