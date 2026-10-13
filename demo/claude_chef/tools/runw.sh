#!/bin/bash
# usage: runw.sh <logfile> <python args...>   -- ONE sim process, RSS watchdog kills above LIMIT_MB (default 3000), records peak RSS
LOG=$1; shift
PY=${PY:-~/Documents/gyj_work/kitchen_robot/build_day/.venv_mj325/bin/python}   # MuJoCo 3.2.5, same as the Windows runs
cd ~/Documents/gyj_work/kitchen_robot/robot_rail/sim/r10/claude; mkdir -p logs/mac
$PY "$@" > "$LOG" 2>&1 & P=$!
PEAK=0
while kill -0 $P 2>/dev/null; do R=$(ps -o rss= -p $P | tr -d ' '); R=${R:-0}; [ "$R" -gt "$PEAK" ] && PEAK=$R; [ "$R" -gt $((${LIMIT_MB:-3000}*1000)) ] && { echo "WATCHDOG KILL rss=$R" >> "$LOG"; kill $P; }; sleep 2; done
wait $P; RC=$?
echo "$(date '+%F %T')	$LOG	rc=$RC	peak_rss_kb=$PEAK" >> logs/mac/peak_rss.tsv
echo "rc=$RC peak_rss_mb=$((PEAK/1024))"
