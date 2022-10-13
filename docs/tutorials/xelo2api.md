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

Before we can add tasks, we need to add a session



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
