# TUTORIAL XELO2API

## Connect to the database
To connect to the database (in localhost), you need to specify the `DATABASE_NAME`, the MySQL `USERNAME` and the MySQL `PASSWORD`.

```python
>>> from xelo2.database import access_database
>>> db = access_database(DATABASE_NAME, USERNAME, PASSWORD)
```

### Create one task for one participant
First we create a subject, called `participant01`. 
It will be assigned an index (which is not important in Python, but it's used in the database)

```python
>>> from xelo2.api import Subject
>>> subj = Subject.add(db, code='participant01')
>>> subj
Subject(db, id=1)
```
`id` refers to the index in the `subjects` table.

Before we can add tasks, we need to add a session:
```python
>>> sess = subj.add_session('IEMU')
Session(db, id=1)
```
Note that `id` refers to the index in the `sessions` table.

The name of the session can only be one of the allowed values. 
To look up the list of allowed names for session do:

```python
>>> from xelo2.database.tables import lookup_allowed_values
>>> lookup_allowed_values(db['db'], 'sessions', 'name')
['IEMU', 'OR', 'MRI', 'CT']
```

See the [instructions](../instructions.md#Sessions) for the description of these values.

Now, we can add one task.
It's sufficient to add the task name.
We'll add extra information (start and duration) later:
```python
>>> run = sess.add_run('chill')
>>> run
Run(db, id=1)
```
Note that `id` refers to the index in the `runs` table.
The `run` object contains the `session` and `subject` parents for convenience:
```python
>>> run.session.subject
Subject(db, id=1)

>>> run.session.subject == subj
True
``` 


## Look up MRI files for one subject
Here you can look up one of the files associated with the T1 of one subject. 
Specify the subject code in the `SUBJECT_CODE` as a string.

```python
from xelo2.bids.root import prepare_subset
from xelo2.api import Subject, Run

subj = Subject(db, code=SUBJECT_CODE)

main_search = f"`runs`.`task_name` = 't1_anatomy_scan' AND `subjects`.`id` = {subj.id}"
subset = prepare_subset(db, main_search)

for run_id in subset['runs']:
    run = Run(db, run_id)
    recs = run.list_recordings()
    if len(recs) == 0:
        print('no recordings for this run')
        
    rec = recs[0]
    files = rec.list_files()
    if len(files) == 0:
        print('no files for this run')
    
    file = files[0]
    print(file.path)
```

## Navigation
  - Go to [`xelo2gui` tutorial](xelo2gui.md)
  - Go to [`xelo2db` tutorial](xelo2db.md)
  - Back to [index](../index.md)
