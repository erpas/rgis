#!/bin/bash

########################################################################################################################
# Link QGIS fibre network design plugin to .qgis2/python/plugin directory (with all python deps linked)
########################################################################################################################

set -u # Exit if we try to use an uninitialised variable
set -e # Return early if any command returns a non-0 exit status

echo "ADD PLUGIN TO QGIS (dev version -- link)"

PWD=`pwd`
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

PLUGIN=rivergis
SRC=$DIR/$PLUGIN

DEST=~/.local/share/QGIS/QGIS3/profiles/default/python/plugins
DEST_PLUGIN=$DEST/$PLUGIN

if [ ! -d "$SRC" ]; then
  echo "Missing directory $SRC"
  exit 1
fi

rm -rf $DEST_PLUGIN

ln -s $SRC $DEST_PLUGIN

echo "$DEST_PLUGIN created"

cd $PWD
