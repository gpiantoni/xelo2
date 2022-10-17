#!/usr/bin/env bash

cat << EOF
Use as ./sql_reset.sh DBNAME SQLUSER
Where DBNAME is the name of the database and SQLUSER is the sql username.
EOF

DBNAME=$1
SQLUSER=$2

mysql -u $SQLUSER -p $DBNAME <<'EOF'
SET FOREIGN_KEY_CHECKS = 0; -- disable a foreign keys check
SET AUTOCOMMIT = 0; -- disable autocommit
START TRANSACTION; -- begin transaction

DROP TABLE IF EXISTS subjects, protocols, sessions, runs, recordings;
DROP TABLE IF EXISTS allowed_values, intended_for, subject_codes, events, experimenters, runs_experimenters, runs_protocols;
DROP TABLE IF EXISTS files, subjects_files, protocols_files, sessions_files, runs_files, recordings_files;
DROP TABLE IF EXISTS channels, channel_groups, electrodes, electrode_groups;
DROP TABLE IF EXISTS sessions_mri, sessions_or, sessions_iemu, runs_sensorimotor, runs_mario, runs_speak, recordings_ephys, recordings_epi, recordings_mri;

SET FOREIGN_KEY_CHECKS = 1; -- enable a foreign keys check
COMMIT;  -- make a commit
SET AUTOCOMMIT = 1
EOF
