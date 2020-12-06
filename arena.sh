#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

mkdir -p ./www/logs

while :
do
	fight_id=$(date +%s)

	# run a fight, .txt so the browser can show it without triggering a download (dirty hack)
	python ./engine.py ${fight_id} |& tee ./www/logs/${fight_id}.txt

	# update results on index.html ?

	sleep 1
done
