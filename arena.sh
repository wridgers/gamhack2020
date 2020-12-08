#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

mkdir -p ./www/logs

while :
do
	fight_id=$(date +%s)

	(
		echo "Begin round $fight_id"
		for i in `seq 1 7`; do
			echo "Checking out team$i"
			(
				cd bots/team$i
				git fetch
				git reset --hard origin/master
				git clean -f
			)
		done

		# run a fight, .txt so the browser can show it without triggering a download (dirty hack)
		python3 ./engine.py ${fight_id}

		# update results on index.html ?
	) |& tee ./www/logs/${fight_id}.txt

	winner=$(sqlite3 hack.db "select player from tournament_results where elimination_round = 0 and player like 'team%' order by tournament_id limit 1")
	if [ -n "$winner" ]; then
		break
	fi

	sleep 1
done
