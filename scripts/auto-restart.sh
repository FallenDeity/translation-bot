PID=`ps -ef | grep -v grep | grep "python3 main.py"| awk '{print $2}'`

if ! ps -p $PID > /dev/null
then
  nowtime=$(date)

  pkill -f tmux
  killall python3
  pgrep procname && killall python3
  tmux new-session -d -s ENTER
  tmux detach -s ENTER
  tmux send-keys -t 0 "cd /home/ubuntu/translation-bot;python3 main.py" ENTER
  echo "$USER : started bot at $nowtime">>/home/ubuntu/logs
#else
# echo "already running"
fi