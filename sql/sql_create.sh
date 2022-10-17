#!/usr/bin/env bash

cat << EOF
Use as ./sql_create.sh DBNAME SQLUSER 
Where DBNAME is the name of the database and SQLUSER is the sql username.

You'll be prompted to type the SQL password TWICE
EOF

DBNAME=$1
SQLUSER=$2

mysql -u $SQLUSER -p -e "CREATE DATABASE IF NOT EXISTS ${DBNAME};"
cat \
commands/allowed_values.sql \
commands/subjects.sql \
commands/protocols.sql \
commands/sessions.sql \
commands/runs.sql \
commands/channels.sql \
commands/electrodes.sql \
commands/recordings.sql \
commands/files.sql \
commands/extra_sessions.sql \
commands/extra_runs.sql \
commands/extra_recordings.sql \
| mysql -u $SQLUSER -p $DBNAME
