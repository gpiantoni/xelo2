## Database

## Open the connection to the MySQL server

If the MySQL database is not stored in the local machine, you need to forward the local port of the remote database:

```bash
ssh -L 3306:localhost:3306 -o ServerAliveInterval=240 user@remote
```

## Recording Offset
Here is how to compute the offset for the recordings. 
Event should refer to the same event in the recordings (TRC) and in the run.events.

```python3
run = Run(db, id=i_run)
run_start = run.start_time
run_event = run.events[i_event_run]['onset']

d = Dataset(path_to_dat)
rec_start = d.header['start_time']
rec_event = d.read_markers()[i_event_dat]['start']

offset = (rec_start - run_start).total_seconds() + (rec_event - run_event)
print(offset)
```
