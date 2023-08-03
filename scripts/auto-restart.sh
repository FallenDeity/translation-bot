PID=`ps -ef | grep -v grep | grep "python3 main.py"| awk '{print $2}'`

if ! ps -p $PID > /dev/null
then
  pkill -f tmux
  killall python3
  sleep 1
  pgrep python3 && killall python3
  tmux new-session -d -s ENTER
  tmux detach -s ENTER
  tmux send-keys -t 0 "cd /home/ec2-user/translation-bot;python3 main.py" ENTER
  nowtime=$(date)
  echo "$USER : started bot at $nowtime">>/home/ec2-user/logs
#else
# echo "already running"
fi