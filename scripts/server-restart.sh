nowtime=$(date)
echo "$USER : Restarting server at $nowtime">>/home/ec2-user/logs
sudo systemctl reboot