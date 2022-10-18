# TUTORIAL XELO2API

## Connect to the database
To connect to the database (in localhost), you need to specify the `DATABASE_NAME`, the MySQL `USERNAME` and the MySQL `PASSWORD`.

```python
>>> from xelo2.database import access_database
>>> db = access_database(DATABASE_NAME, USERNAME, PASSWORD)
```

## Add one iEEG recording

### Subject
First we create a subject, called `participant01`. 
It will be assigned an index (which is not important in Python, but it's used in the database)

```python
>>> from xelo2.api import Subject
>>> subj = Subject.add(db, code='participant01')
>>> subj
Subject(db, id=1)
```
`id` refers to the index in the `subjects` table.

Then, you can some information about the subject:
```python
>>> subj.sex = 'Female'
```

### Session
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

### Run
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

### iEEG Recordings
Let's add some iEEG recordings manually.
```python
>>> rec = run.add_recording('ieeg')
>>> rec
Recording(db, id=1)
```
We can also add one additional field when the `modality` is `ieeg`:
```python
>>> rec.Manufacturer = 'Micromed'
```
Recordings which are `ieeg`, `eeg` and `meg` can also have channels and electrodes.
Channels and electrodes are stored in a similar way in the xelo2 database, so let's look at channels first as an example:
```python
>>> from xelo2.api import Channels
>>> chan_group = Channels.add(db)
>>> chan_group.name = 'some test channels'
>>> channels = chan_group.empty(5)  # let's assume that there are 5 channels
>>> channels['name'] = [f'chan{x:03d}' for x in range(5)]
>>> channels['type'] = 'SEEG'
>>> chan_group.data = channels  # this is necessary to assign the channels back into the channel group
>>> chan_group.data
array([('chan000', 'SEEG', '', nan, nan, '', '', '', nan, '', ''),
       ('chan001', 'SEEG', '', nan, nan, '', '', '', nan, '', ''),
       ('chan002', 'SEEG', '', nan, nan, '', '', '', nan, '', ''),
       ('chan003', 'SEEG', '', nan, nan, '', '', '', nan, '', ''),
       ('chan004', 'SEEG', '', nan, nan, '', '', '', nan, '', '')],
      dtype=[('name', '<U4096'), ('type', '<U4096'), ('units', '<U4096'), ('low_cutoff', '<f8'), ('high_cutoff', '<f8'), ('reference', '<U4096'), ('groups', '<U4096'), ('description', '<U4096'), ('notch', '<f8'), ('status', '<U4096'), ('status_description', '<U4096')])
```
We have now create one channel group, which contains the labels for 5 channels.
We can now attach (i.e. link) this channel group to our iEEG recording:
```python
>>> rec.attach_channels(chan_group)
```
You can only attach one channel group to a recording.
However, many recordings can have the same channel group, so that when you modify one channel group, all the recordings that are linked to that channel group have the updated list of channels.

We can also an electrode group using a similar syntax:
```python
>>> from xelo2.api import Electrodes
>>> elec_group = Electrodes.add(db)
>>> elec_group.name = 'low density grid'
>>> electrodes = elec_group.empty(4)
>>> electrodes['name'] = [f'chan{x:03d}' for x in range(4)]
>>> electrodes['material'] = 'gold'
>>> elec_group.data = electrodes
>>> elec_group.data
array([('chan000', nan, nan, nan, nan, 'gold', '', '', '', '', nan, ''),
       ('chan001', nan, nan, nan, nan, 'gold', '', '', '', '', nan, ''),
       ('chan002', nan, nan, nan, nan, 'gold', '', '', '', '', nan, ''),
       ('chan003', nan, nan, nan, nan, 'gold', '', '', '', '', nan, '')],
      dtype=[('name', '<U4096'), ('x', '<f8'), ('y', '<f8'), ('z', '<f8'), ('size', '<f8'), ('material', '<U4096'), ('manufacturer', '<U4096'), ('groups', '<U4096'), ('hemisphere', '<U4096'), ('type', '<U4096'), ('impedance', '<f8'), ('dimension', '<U4096')]).
```

## Adding an MRI recording
We will now create an MRI session with a T1 recording (acquisition). 
We do not need to create a participant again but we will look up the name in the database:
```python
>>> from xelo2.api import Subject
>>> subj = Subject(db, code='participant01')
```
We now create a new MRI session and a task:
```python
>>> from datetime import datetime
>>> sess = subj.add_session('MRI')
>>> sess.MagneticFieldStrength = '3T'  # only when session is MRI
>>> run = sess.add_run('t1_anatomy_scan')
>>> run.start_time = datetime(2022, 4, 9, 16, 0, 0)
>>> run.duration = 400
>>> run.performance = 'participant did not move too much'
```
Now, we can add a new recording (which actually contains the data):
```python
>>> rec = run.add_recording('T1w')
```
Note that the modality in the recording does NOT need to match the task name of the run.
You could have used another name for the task name. 
The task name in the run tells you what the subject was doing, while the modality of the recording tells you how the data was acquired.

We have quite some additional fields for MRI recordings:
```python
>>> rec.Sequence = '3T T1w'
>>> rec.region_of_interest = 'brain'  # free text
>>> rec.SliceEncodingDirection = 'AP'
>>> rec.PhaseEncodingDirection = 'LR'
>>> rec.SliceOrder = 'Interleaved'
```
The fields available for the MRI recordings are described in the [instructions](../instructions.md#MRI_Recordings). 

### METC protocol
You can also create a signed informed consent for each participant (because participants signed the informed consent) in this way:
```python
>>> subj = Subject(db, id=1)
>>> metc = subj.add_protocol('14-420')
>>> metc.date_of_signature = datetime(2022, 4, 1)  # optional
>>> metc.version = 'free text'  # optional, but try to be consistent
```
Because participants might sign multiple informed consents and even within the same IEMU period, they might do tasks under different METC protocols, the right level where you need to link the protocol is at the run level.
So, for each run, you can specify which protocol was used:
```python
>>> run.attach_protocol(metc)
```

## Navigation
  - Go to [`xelo2gui` tutorial](xelo2gui.md)
  - Go to [`xelo2db` tutorial](xelo2db.md)
  - Back to [index](../index.md)
