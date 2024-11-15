# A dockerized Python script that polls Steam for new reviews, then sends the new reviews to Discord via Webhook.
https://hub.docker.com/r/thanathan1228/steamreviewdiscordnotifications
```
docker run \
-e DISCORD_WEBHOOK_URL='{your_discord_webhook}' \
-e STEAM_APP_ID='{your_steam_app_id}' \
thanathan1228/steamreviewdiscordnotifications
```
## Required Environment Variables
`DISCORD_WEBHOOK_URL` [Your Discord Channel's Webhook.](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)

`STEAM_APP_ID` [Your Game's Steam App ID.](https://steamdb.info/apps/)

## Optional Environment Variables
`STEAM_API_KEY` [Your Steam API Key.](https://steamcommunity.com/dev/apikey)
*Required if you wish to see the Steam usernames in the Discord notification*

`REPEAT_SECONDS` How long between each refresh.
*Default="60"*

`TIMESTAMP_FILE` Where the last recorded timestamp is saved (text file).
*Default=timestamp.txt*
