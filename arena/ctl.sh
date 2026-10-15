#!/bin/sh
# ./ctl.sh bump | cmd <target> <shot|diag|reload|home> | diag | shots
D=$(dirname "$0")
case "$1" in
 bump) f="$D/extension/VERSION"; echo $(( $(cat "$f") + 1 )) > "$f"; echo "VERSION=$(cat "$f")";;
 cmd) curl -s -X POST localhost:8765/cmdset -H "content-type: application/json" -d "{\"target\":\"$2\",\"cmd\":\"$3\"}";;
 diag) tail -n ${2:-5} "$D/diag.log";;
 shots) ls -t "$D/shots" | head;;
esac
