#!/bin/bash
#export IPYTHON_KERNEL_IP=127.0.0.1
#export JUPYTER_CLIENT_PORT_RANGE="60000:61000"
#export JUPYTER_RUNTIME_DIR=/tmp/jupyter_runtime
#export PYTHONDONTWRITEBYTECODE=1
echo "[wrapper] Launching: $@" >> /tmp/kernel_wrapper.log
date >> /tmp/kernel_wrapper.log
#echo "Wrapper started; $@" >> /tmp/kernel_wrapper.log
#echo "Calling exec uenv run fdb/25.7:1895345912 /user-environment/venvs/fdb/bin/python3.11 -Xfrozen_modules=off -m ipykernel_launcher $@"
#echo "WW ; $0 $1 $2" >> /tmp/kernel_wrapper.log 2>&1
#echo "exec uenv run fdb/25.7:1895345912 /user-environment/venvs/fdb/bin/python3.11 -Xfrozen_modules=off -m ipykernel_launcher $@"  >> /tmp/kernel_wrapper.log 2>&1
#cat $@  >> /tmp/kernel_wrapper.log 2>&1

#sleep 0.2
#echo "[wrapper] Checking ports bound by current user:" >> /tmp/kernel_wrapper.log
#lsof -i -n -P -a -p $$ >> /tmp/kernel_wrapper.log
#echo "Ports " >> /tmp/kernel_wrapper.log
#ss -tlpn | grep 5[0-9][0-9][0-9][0-9] >> /tmp/kernel_wrapper.log

#echo "[wrapper] Connection file: $1" >> /tmp/kernel_wrapper.log
#cat "$1" >> /tmp/kernel_wrapper.log

#uenv run fdb/25.7:1895345912 -- /user-environment/venvs/fdb/bin/python3.11 
exec uenv run --view=fdb fdb/5.16:1907126596 -- /user-environment/venvs/fdb/bin/python3.11 "$@" > /tmp/kernel_wrapper.log 2>&1


