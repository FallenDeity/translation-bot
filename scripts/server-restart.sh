nowtime=$(date)
echo "$USER : Restarting server at $nowtime">>/home/ubuntu/logs
aws ec2 reboot-instances --instance-ids i-025c10c1ed58f97b3 --profile admin
sudo systemctl reboot