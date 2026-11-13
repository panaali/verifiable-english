cd /home/seyran/code/ve-gate-tie-test-split
echo "load start: $(cat /proc/loadavg)"; date -u
uv run pytest -q -n 0 -p no:randomly tests/test_consolidation_tools.py -k test_mutated_committed_ties --durations=0 > /tmp/gtts/new.log 2>&1; echo "new rc $?"
echo "load mid: $(cat /proc/loadavg)"; date -u
uv run pytest -q -n 0 tests/test_zz_main_consolidation_tmp.py -k test_mutated_committed_ties --durations=0 > /tmp/gtts/old.log 2>&1; echo "old rc $?"
echo "load end: $(cat /proc/loadavg)"; date -u
