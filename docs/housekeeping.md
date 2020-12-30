## Allowed values
Possible values are stored in `tables.json` and also in the table `allowed_values`. 
The best way is to keep everything in `allowed_values`.

The only exception is the name of the experimenters.
You need to change the `experimenters` directly (because we use the `id` from that table).

### Constraints
You should make sure that for each `allowed_values`, there is a constraint in the corresponding table.

## Alias and Doc
You can add a more informative name (including spaces) and documentation to each column. 
You need to edit `column_comment` from the `columns` table in `information_schema`. 
Make sure that you use the right syntax: `alias: documentation` (use only one column to separate the alias from the doc). 
So, for example, "`Date of Birth: Date of birth of the participant`".

