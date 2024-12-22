# Backlink-Checker

A simple tool in order to check backlinks and send results on Discord server.

## Installation

```
docker build -t backlink-checker .
docker run --rm -e DISCORD_WEBHOOK_URL="DISCORD_WEBHOOK_URL" backlink-checker
```
