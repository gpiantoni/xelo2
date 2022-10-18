# TUTORIAL GUI

## Connect to database
To connect to a SQL database, you can do:
```bash
xelo2
```
and then log in with the prompt screen. Or you can pass the credentials directly (in plain text...):
```bash
xelo2 --mysql DATABASE_NAME -U USERNAME -P PASSWORD
```
When you start up a new database, the database is completely empty.
However, for this GUI tutorial, I already ran the commands of the [`xelo2api` tutorial](xelo2api.md), so that there is already some information available.

## Overview

![Overview][overview]

The GUI presents a useful overview of the data in the database. 
The panels `Subjects`, `Sessions`, `Runs`, `Recordings` follow the hierarchy of the BIDS format.
In addition, the panel `Protocols` is used to stored information about the informed consents that the participant signed.
The panels `Channels` and `Electrodes` will be discussed below.
On the right-hand side, the `Parameters` panel shows all the fields for each level (from subject to recording).



## Navigation
  - Go to [`xelo2api` tutorial](xelo2api.md)
  - Go to [`xelo2db` tutorial](xelo2db.md)
  - Back to [index](../index.md)

[overview]: img/overview.png "Overview"
