# Mileage Analysis

This is a small project to analyze the mileage of my car throughout the year.

The data is available [here](https://docs.google.com/spreadsheets/d/1x2Tmj_is1Rqp43LaTU8lHYl77qS3huiaiz9fWcfcJgA/edit?usp=sharing)

## Methodology

The data was collected using [Tasker](https://play.google.com/store/apps/details?id=net.dinglisch.android.taskerm&hl=en_US)

I have a Tasker profile set up to get the date and calculate the time between
when my phone connects to the car's bluetooth and when it disconnects.  When
the phone disconnects, Tasker prompts for the distance traveled and for the MPG
for the trip. It then appends this data to the Google Sheet above.
