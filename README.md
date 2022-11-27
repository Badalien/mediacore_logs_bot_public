# Description

This Project allow to monitor SBC Mediacore Action Logs to find changes mades with Dialpeers
Then sending change notifications to Telegram chat and Google sheets

## Modules

* google_api: allow to write data to Google sheets (need to declare api parameters in `google_keys.json` file and define spreadsheet id in __init__ method)
* telegram: allow to send messages via Telegram bot to telegram chat (need to define bot token and chat ID in `config.json` file in dir *telegram*)
* mediacore: main module to connect to SBC Mediacore api and get info from logs (need to define username and password in in `config.json` file in dir *mediacore*)

<br>

## Version history

Current Version 0.1 (24.08.2021):
- Alerting about TP add/delete in DP
- Alerting about ANI add/delete/update in DP

Version 0.2 (25.08.2021):
- Add feature to ingore Dialpeers by name
- Checking logs and Polling TG messages divided into separate files
- Some code fixes


Version 0.3 - STABLE (07.09.2021 19:00):
- add Priotrities to logs messages


Version 0.5 - STABLE (30.09.2021 16:00):
- add feature to store DP changes in MySQL database


Version 0.6 - STABLE (30.09.2021 16:00):
- add mysql connection_close after each query;
- add some feature for improving test capabilities;


Version 0.7 - STABLE (12.11.2021 13:00):
- send logs data to Google Sheet;

Version 0.8 - pre-STABLE (29.03.2022 19:00):
- add better logging (with logging module);
- prepare keyboard markups for further improval;

Version 0.81 - STABLE (12.04.2022 18:00):
- add acync mutliprocessing;
- add telegram message handler;
- add telegram command to restart application;

TO DO:
- fix logging for modules
- fix async for telegram
- add type hinting for all functions
