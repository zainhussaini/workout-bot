# workout-bot

This creates a Discord bot that you can use to track workouts, and show a leaderboard based on who has tracked the most points.

### Setup
1. Clone the repository
```bash
git clone https://github.com/zainhussaini/workout-bot.git
```

2. Create a Discord bot and generate a token at https://discord.com/developers/docs/topics/oauth2. At this step you can also add it to your Discord sever(s).
   1. Select `bot` in scopes
   2. Select `Send Messages` and `Read Message History` in bot permissions
3. Set up redis server
```bash
sudo apt install redis
redis-cli
set 'DISCORD_TOKEN' '<insert token here>'
```
4. Install python packages
```bash
pip3 install -U discord.py tabulate pandas datetime redis
```
5. Test the program
```bash
python3 main.py
```
6. Run the program in background
```bash
nohup python3 main.py &
```

### Usage

Once you add the bot to the Discord channel, you can log workouts by `!point`.

![Screenshot 2023-12-12 at 1 00 15 AM](https://github.com/zainhussaini/workout-bot/assets/6494905/370954ec-c4ea-4658-bb73-68714b7783b8)

You can check the rankings by `!scoreboard`. The users with logged workouts are shown ranked by score.

![Screenshot 2023-12-12 at 1 00 15 AM](https://github.com/zainhussaini/workout-bot/assets/6494905/7bd6b7b5-ffe4-4e67-a7e2-54249a60b0c0)

The full list of commands is found by by `!help`.

![image](https://github.com/zainhussaini/workout-bot/assets/6494905/bd911ab2-4598-4853-a83f-99dbe052a1a1)
