# TUTORIAL XELO2API

## Connect to the database
To connect to the database (in localhost), you need to specify the `DATABASE_NAME`, the MySQL `USERNAME` and the MySQL `PASSWORD`.

```python
>>> from xelo2.database import access_database
>>> db = access_database(DATABASE_NAME, USERNAME, PASSWORD)
```

### Create one task with recordings for one participant

#### Subject
First we create a subject, called `participant01`. 
It will be assigned an index (which is not important in Python, but it's used in the database)

```python
>>> from xelo2.api import Subject
>>> subj = Subject.add(db, code='participant01')
>>> subj
Subject(db, id=1)
```
`id` refers to the index in the `subjects` table.

#### Session
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

See the [instructions](../instructions.md#Sessions) for the description of these values and for their fields.
For example, when the session is `IEMU`, we can also store `date_of_implantation`:
```python
>>> sess.date_of_implantation
# None, it's empty
>>> from datetime import datetime
>>> sess.date_of_implantation = datetime(2022, 4, 1)
>>> sess.date_of_implantation
datetime.date(2022, 4, 1)
```

#### Run
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
We can then add some information about the run, e.g. about the performance or some aspects of the acquisition.
```python
>>> run.start_time = datetime(2022, 4, 10, 10, 0, 0)
>>> run.duration = 180

>>> run.task_description = 'the screen was 90cm away'
>>> run.performance = 'information about the performance'
>>> run.acquisition = 'information about the acquisition'
```
All of these fields are optional, but `start_time` and `duration` are very useful.
The fields available for all the runs are described in the [instructions](../instructions.md#Runs). 

Some runs (depending on `task_name`) might have additional fields. 
For example, when a run has the task name called `motor`, then you can also specify `body_part` or `left_right`:
```python
>>> run1 = sess.add_run('motor')
>>> run1.start_time = datetime(2022, 4, 10, 11, 0, 0)
>>> run1.duration = 210
>>> run1.body_part = 'hand'
>>> run1.left_right = 'right'
```

You can also add the experimenters (the people who performed the experiment) using this syntax:
```python
>>> run.experimenters = ['Gio', ]
```
You need to make sure that the experimenter is on the list. 
To look up the list of experimenters, use:
```python
>>> from xelo2.api import list_experimenters
>>> list_experimenters(db)
['Gio', 'Ryder']
```
See the [instructions](../instructions.md#Experimenters) on how to add experimenters.


#### Recordings








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
