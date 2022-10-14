# TUTORIAL XELO2DB

### Privileges
Add permission to read the `xelo2` database but not to modify it.

```SQL
GRANT SELECT, SHOW VIEW, TRIGGER ON xelo2.* TO `user`@`localhost` ;
FLUSH PRIVILEGES ;
```

## Allowed values
Possible values are stored in the table `allowed_values`. 
To allow for additional values, you need to add a new row to the `allowed_values` table.

The only exception is the name of the experimenters.
You need to change the `experimenters` directly (because we use the `id` from that table).

### Constraints
You should make sure that for each `allowed_values`, there is a constraint in the corresponding table.

## Alias and Doc
You can add a more informative name (including spaces) and documentation to each column. 
You need to edit `column_comment` from the `columns` table in `information_schema`. 
Make sure that you use the right syntax: `alias: documentation` (use only one column to separate the alias from the doc). 
So, for example, "`Date of Birth: Date of birth of the participant`".

## Subtables
Subtables should follow the naming format `maintable_name`, so for example the subtable for the motor tasks should be `runs_motor`.
Note that `runs` should be plural, then underscore, then text without underscore.

For example, you can create a table like this:

```SQL
CREATE TABLE `runs_motor` (
  `runs_id` int(11) DEFAULT NULL,
  `overt_covert` text DEFAULT NULL COMMENT 'Overt / Covert',
  UNIQUE KEY `run_id` (`run_id`),
  CONSTRAINT `runs_flip_ibfk_1` FOREIGN KEY (`run_id`) REFERENCES `runs` (`id`) ON DELETE CASCADE
) ;
```

To make sure that subtables are correctly linked to the main table, you need to create two triggers for each table. 
Use this syntax:

### First trigger
In the `maintable` (f.e. `runs`), you should specify an `INSERT` / `AFTER` trigger (called it `insert_id_to_subtable_runs_motor`):

```SQL
BEGIN
  IF NEW.task_name = 'motor'
  THEN
    INSERT INTO runs_motor (run_id) VALUES (NEW.id) ;
  END IF;
END
```

You need to change:
  - `task_name` to the column name in the main table
  - `'motor'` to the value it needs to match
  - `runs_motor` is the name of the subtable
  - `run_id` which should have the syntax `(maintable)_id` (main table without trailing `s`)

If a condition matches multiple values, then you can use this syntax

```SQL
BEGIN
  IF NEW.task_name IN ('motor', 'sensory')
  THEN
    INSERT INTO runs_motor (run_id) VALUES (NEW.id) ;
  END IF;
END
```

### Second trigger
In the `maintable` (f.e. `runs`), you should specify an `UPDATE` / `AFTER` trigger (called it `replace_id_to_subtable_runs_motor`):

```SQL
BEGIN
  IF NEW.task_name <> OLD.task_name AND
    NEW.task_name = 'motor' AND
    NEW.id NOT IN (SELECT `run_id` FROM `runs_motor`)
  THEN
    INSERT INTO runs_motor (run_id) VALUES (NEW.id) ;
  END IF;
END
```

Change the values as in the first trigger.
The 3 conditions are:
   - check that the main condition related to the subtable has changed
   - check that the main condition has the correct value (you might need `IN` syntax instead of `=` when you have multiple values)
   - check whether the `id` already exists in the subtable. This happens when the task was `motor`, then it was changed to something else, then back to `motor`. The old info is still stored in the subtable even when the condition does not apply. This approach leaves some old data in the subtables (which is not shown and possibly not relevant) but it's useful when a user changes the condition by mistake, and then goes back. It would be disappointing to add the info in the subtable again.


## SQL examples

### 3T PRESTO
Update PRESTO sequence with the appropriate parameters:

```SQL
UPDATE `recordings_mri` SET  `SliceOrder` = '3D', `PhaseEncodingDirection` = 'PA', `SliceEncodingDirection` = 'RL' WHERE `Sequence` = '3T PRESTO';
```


### 3T T1w
If task is `3T T1w`, use this syntax

```SQL
UPDATE `recordings_mri` SET  `SliceOrder` = 'Sequential', `SliceEncodingDirection` = 'IS' WHERE `Sequence` = '3T T1w';
```

I don't think that `PhaseEncodingDirection` is relevant here.

### FLAIR
If task is `flair`, use this syntax

```SQL
UPDATE `recordings_mri` SET `Sequence` = '3T FLAIR' WHERE `recording_id` IN (SELECT `id` FROM `recordings` WHERE `run_id` IN (SELECT `id` FROM `runs` WHERE `task_name` = 'flair_anatomy_scan'));
```

