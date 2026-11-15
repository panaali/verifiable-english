#!/bin/zsh
# Round r3: the Preparedness and agent-policy pairs again (PYTHONPATH per side), and beside them the Preparedness
# py_funcs "before" run with the base's own `ve`.
H=/home/seyran/code/ve-kb-10b-switch; B=$H-base; S=$H/docs/kernel/kb-10b-switch/evidence/scripts
export VE_LEAN_SERVICE=$H/lean/.lake/build/bin/ve_service
(cd $B && PYTHONPATH=$B zsh /home/seyran/code/manage-agents/iso.sh kb10bs-pf-before-prep 8G -- $H/.venv/bin/python \
   $S/py_funcs.py /tmp/kb10bs/pyfuncs-before-openai-preparedness.json usecases/openai-preparedness/run.py --check \
   > /tmp/kb10bs/pyfuncs-before-openai-preparedness.log 2>&1; echo "py_funcs before openai-preparedness rc=$?") &
zsh $S/pair5.sh r3 openai-preparedness agent-policy
wait
