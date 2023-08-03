cd /home/ec2-user/
rm -rf translation-bot
sleep 1
git clone  git@github.com:Ajurahul/translation-bot.git
echo "$USER : Updated git. bot will restart after this">>/home/ec2-user/logs