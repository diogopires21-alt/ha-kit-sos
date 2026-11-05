# Kit SOS — Home Assistant app

[![Open your Home Assistant instance and show the add app repository dialog with this repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fdiogopires21-alt%2Fha-kit-sos)

A simple, good-looking way to track an emergency kit (or pantry, or medicine cabinet) in Home Assistant: quantities, locations and expiry dates, with alerts before things expire.

![Supports aarch64 Architecture](https://img.shields.io/badge/aarch64-yes-green.svg)
![Supports amd64 Architecture](https://img.shields.io/badge/amd64-yes-green.svg)

## Install

1. In Home Assistant go to **Settings → Apps → Install app → ⋮ → Repositories** and add `https://github.com/diogopires21-alt/ha-kit-sos` (or use the button above).
2. Find **Kit SOS**, install it, start it and enable **Show in sidebar**.

> Kit SOS is an **app** (formerly add-on). Apps are installed from app repositories, not from the Marketplace (ex-HACS), which only handles integrations, dashboard cards, themes and templates.

## Apps in this repository

### [Kit SOS](./kit_sos)

Emergency-kit and expiry-date tracker with Grocy import, Telegram/notify alerts and sensors. Interface in Portuguese and English.

## Development

```bash
python3 -m unittest discover -s tests -v       # tests with a fake Home Assistant and Grocy
python3 tests/fake_services.py &               # fake HA on :18123 and Grocy on :18080
KIT_SOS_DEV=1 KIT_SOS_DATA=/tmp/kitsos SUPERVISOR_TOKEN=test-token \
  KIT_SOS_HA_API=http://127.0.0.1:18123/api python3 kit_sos/app/server.py   # http://localhost:8099
```

The server only uses the Python standard library. Data is stored in SQLite in the app's `/data` folder; schema changes go through the `MIGRATIONS` list in `server.py`.

## License

MIT
