#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

mkdir -p ./www/logs

while :
do
	tournament_id=$(date +%s)

	echo "Begin round $tournament_id"

	for i in `seq 1 7`; do
		echo "Checking out team$i"
		(
			cd bots/team$i
			git fetch
			git reset --hard origin/master
			git clean -f
		)
	done

	(
		for i in `seq 1 7`; do
			(
				cd bots/team$i
				echo "Team$i is running: $(git rev-parse HEAD)"
			)
		done

		# run a tournament, .txt so the browser can show it without triggering a download (dirty hack)
		python3 ./engine.py ${tournament_id}

		# update results on index.html ?
	) |& tee ./www/logs/${tournament_id}.txt

	if [ -n "$OFFICAL" ]; then
		sqlite3 hack.db "insert into official (tournament_id) values ('$tournament_id');"
		break
	fi

	# update www
	make -j4

	sleep 1
done
