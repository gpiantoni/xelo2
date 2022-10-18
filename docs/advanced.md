## Database

### Open the connection to the MySQL server

If the MySQL database is not stored in the local machine, you need to forward the local port of the remote database:

```bash
ssh -L 3306:localhost:3306 -o ServerAliveInterval=240 user@remote
```

## API

### Fields in subtables
Note that there is a subtle bug when setting and getting values that are present in subtables only.
Say that you have two tasks:
```python
>>> run.task_name
'chill'
>>> run1.task_name
'motor'
```
When you try to specify a value for a field that does not exist, you get an error:
>>> run.asdfasdf = 'asdf'
ValueError: adfasdf is not stored in this run
```
which is expected.

As explained in the [instructions](../instructions.md#Runs), the task `motor` also has additional fields which are stored in the subtable `runs_sensorimotor`, so that you can do:
```python
>>> run1.body_part = 'hand'
>>> run1.body_part
'hand'
```
The bug occurs when you try to specify a value for a field which is present only in a subtable. 
There is no error when setting the value (you should expect that), but you do get an error when trying to get the value.
```python
>>> run.task_name
'chill'
>>> run.body_part = 'hand'  # BUG: no error
>>> run.body_part
Could not get body_part from runs_sensorimotor for id = '1'
```
It should be possible to fix this bug but it's tricky because the setting of the values in subtables relies on SQL triggers, which are not easy to get in Python (although the information regarding the subtables of the SQL database is stored in `db['subtables']).

### Recording Offset
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

## Navigation
  - Back to [index](index.md)
