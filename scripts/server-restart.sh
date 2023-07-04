nowtime=$(date)
echo "Restarting server at $nowtime">>/home/ubuntu/logs
sudo systemctl reboot