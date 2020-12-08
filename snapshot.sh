#!/bin/bash

name="$1"

if [ -z "$name" ]; then
	echo "No gen specified. :("
	exit 1
fi

rsync -r --exclude=__pycache__ --exclude=.git -v bots/ "$name/"
zip -mr www/"$name".zip "$name/"
