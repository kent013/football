#!/bin/bash
#
# ssh into a machine and automatically set the background
# color of Mac OS X Terminal depending on the hostname.
#
# Installation:
# 1. Save this script to /usr/local/bin/ssh-host-color
# 2. chmod 755 /usr/local/bin/ssh-host-color
# 3. alias ssh=/usr/local/bin/ssh-host-color
# 4. export PRODUCTION_HOST="<hostname_production_server>"
# 5. Configure your host colors below.
#
# Taken from http://talkfast.org/2011/01/10/ssh-host-color
#
set_term_bgcolor(){
  local R=$1
  local G=$2
  local B=$3
  /usr/bin/osascript <<EOF
tell application "iTerm"
  tell the current terminal
    tell the current session
      set background color to {$(($R*65535/255)), $(($G*65535/255)), $(($B*65535/255))}
    end tell
  end tell
end tell
EOF
}

if [[ "$@" =~ $PRODUCTION_HOST ]]; then
  set_term_bgcolor 50 0 0
else
  set_term_bgcolor 0 40 0
fi

ssh $@ 

set_term_bgcolor 0 0 0
