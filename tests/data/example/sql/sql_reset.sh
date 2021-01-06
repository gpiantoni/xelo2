
echo "SET FOREIGN_KEY_CHECKS = 0; -- disable a foreign keys check" > full.sql
echo "SET AUTOCOMMIT = 0; -- disable autocommit" >> full.sql
echo "START TRANSACTION; -- begin transaction" >> full.sql

echo "DROP TABLE IF EXISTS subjects, protocols, sessions, runs, recordings;" >> full.sql
echo "DROP TABLE IF EXISTS allowed_values, intended_for, subject_codes, events, experimenters, runs_experimenters, runs_protocols;" >> full.sql
echo "DROP TABLE IF EXISTS files, subjects_files, protocols_files, sessions_files, runs_files, recordings_files;" >> full.sql
echo "DROP TABLE IF EXISTS channels, channel_groups, electrodes, electrode_groups;" >> full.sql
echo "DROP TABLE IF EXISTS sessions_mri, sessions_or, sessions_iemu, runs_sensorimotor, runs_mario, runs_speak, recordings_ephys, recordings_epi, recordings_mri;" >> full.sql

cd tests/data/example/sql/
cat allowed_values.sql subjects.sql protocols.sql sessions.sql runs.sql channels.sql electrodes.sql recordings.sql files.sql extra_sessions.sql extra_runs.sql extra_recordings.sql >> ../../../../full.sql
cd -

echo "SET FOREIGN_KEY_CHECKS = 1; -- enable a foreign keys check" >> full.sql
echo "COMMIT;  -- make a commit" >> full.sql
echo "SET AUTOCOMMIT = 1 ;" >> full.sql

ssh blue1 "mysql -u giovanni --password=password \"$1\" " < full.sql
rm full.sql
