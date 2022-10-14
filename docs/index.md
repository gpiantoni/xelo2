# XELO2

xelo2 allows you to organize electrophysiological and fMRI data in a well-structured database and to export the data in the BIDS format.
xelo2 consists of 3 parts:
  - `xelo2db`: the SQL database containing the information about the participants, sessions, tasks and experiments;
  - `xelo2api`: a set of Python scripts to interact with `xelo2db`, which does not require you to know SQL;
  - `xelo2gui`: the graphical user interface that will show you the data and will allow you to import and export data quickly (`xelo2gui` relies on `xelo2api`).

[Installation](installation.md)

[Tutorials](tutorial.md)

[Instructions](instructions.md)

[Advanced](advanced.md)

[API](xelo2/index.html)
