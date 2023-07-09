nowtime=$(date)
echo "$USER : Restarting server at $nowtime">>/home/ubuntu/logs
sudo systemctl reboot