# Caltrain Status

Use the blink(1) to communicate the status of incoming Caltrain trains.

Green is local trains, Yellow is express trains, and Red is bullet trains.

The blink(1) blinks slowly when it's time to pack up leave for the station.
It blinks more quickly if you need to hurry to make the train.
When it stops blinking, it's most likely too late to make the train.

Check caltrain_status.py for some variables you can use to configure things like source/destination stations of
interest, Caltrain travel direction of interest, minutes it takes you to get ready, etc.

## Setup

Install pip requirements:

```
pip install -r requirements.txt
```

Install the `nextcaltrain` program (https://github.com/parshap/nextcaltrain):

```
npm install -g nextcaltrain
```

Lastly, follow the steps to setup the daemon in the README in the root of this repository.

## Updating Caltrain schedule data

If there is new Caltrain schedule data, you should be able to fetch it by updating `nextcaltrain`
(assuming the author of that tool has published a new version of it):

```
npm update -g nextcaltrain
```

If that doesn't fetch a new schedule update, you can update the data yourself using the `update-data` script provided
with `nextcaltrain`. The process of doing that is left as an exercise for the reader.
