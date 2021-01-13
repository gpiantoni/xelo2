CREATE TABLE `experimenters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ;

INSERT INTO `experimenters` (`name`) VALUES ('Gio'),('Ryder');

CREATE TABLE `runs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `session_id` int(11) DEFAULT NULL,
  `task_name` text NOT NULL COMMENT "Task Name: Name of the task",
  `start_time` timestamp(3) NULL DEFAULT NULL COMMENT "Start Time: Clock time of the beginning of the task",
  `duration` float DEFAULT NULL COMMENT "Duration: Length of the recording in seconds",
  `xelo_stem` text DEFAULT NULL COMMENT "Xelo Stem: Name of the .xml xelo file associated with this run (without .xml)",
  `performance` text DEFAULT NULL COMMENT "Performance: How the patient performed. Legacy from xelo",
  `task_description` text DEFAULT NULL COMMENT "Task Description: Longer description of the task",
  `acquisition` text DEFAULT NULL COMMENT "Acquisition: Comments about data acquisition. Legacy from xelo",
  PRIMARY KEY (`id`),
  KEY `session_id` (`session_id`),
  CONSTRAINT `runs_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE CASCADE
) ;

INSERT INTO `allowed_values` VALUES ('runs','task_name','DTI'),('runs','task_name','MIQ'),('runs','task_name','P300'),('runs','task_name','abled'),('runs','task_name','action_selection'),('runs','task_name','angiography_scan'),('runs','task_name','animal'),('runs','task_name','audcomsent'),('runs','task_name','audcomword'),('runs','task_name','auditory_attention'),('runs','task_name','auditory_localizer'),('runs','task_name','bair_hrfpattern'),('runs','task_name','bair_prf'),('runs','task_name','bair_spatialobject'),('runs','task_name','bair_spatialpattern'),('runs','task_name','bair_temporalpattern'),('runs','task_name','bargrasp'),('runs','task_name','bci_cursor_control_attent'),('runs','task_name','bci_cursor_control_motor'),('runs','task_name','bci_cursor_control_taal'),('runs','task_name','bci_cursor_control_visual'),('runs','task_name','bci_cursor_control_wm'),('runs','task_name','boldfinger'),('runs','task_name','boldhand'),('runs','task_name','boldsat'),('runs','task_name','calc'),('runs','task_name','checkerboard'),('runs','task_name','chill'),('runs','task_name','clickaway'),('runs','task_name','count'),('runs','task_name','deleted'),('runs','task_name','divatt'),('runs','task_name','eccentricity_mapping'),('runs','task_name','emotion'),('runs','task_name','error_potential'),('runs','task_name','eye_task'),('runs','task_name','eyes_open_close'),('runs','task_name','faces_emotion'),('runs','task_name','faces_houses'),('runs','task_name','facial_expressions'),('runs','task_name','feedback_wm'),('runs','task_name','finger_mapping'),('runs','task_name','gestures'),('runs','task_name','instant_aud_recall'),('runs','task_name','knottask'),('runs','task_name','language'),('runs','task_name','letter_picture_matching'),('runs','task_name','line_bisection'),('runs','task_name','mario'),('runs','task_name','mental_rotation'),('runs','task_name','mickey_task'),('runs','task_name','mooney'),('runs','task_name','motionmapper'),('runs','task_name','motor'),('runs','task_name','mouth_movements'),('runs','task_name','move_imagine_rest'),('runs','task_name','move_three_conditions'),('runs','task_name','movi'),('runs','task_name','movie_watching'),('runs','task_name','movieben'),('runs','task_name','multi_localizer'),('runs','task_name','music'),('runs','task_name','natural_rest'),('runs','task_name','notask'),('runs','task_name','noun'),('runs','task_name','number'),('runs','task_name','numerosity'),('runs','task_name','phonemes'),('runs','task_name','picnam'),('runs','task_name','pokemotor'),('runs','task_name','polar_mapping'),('runs','task_name','portem'),('runs','task_name','pulse'),('runs','task_name','reading_task'),('runs','task_name','reference_scan'),('runs','task_name','rest'),('runs','task_name','retinotopic_map'),('runs','task_name','rotating_sphere'),('runs','task_name','rotmotion'),('runs','task_name','saccade'),('runs','task_name','sendkeys'),('runs','task_name','single_words'),('runs','task_name','sleep'),('runs','task_name','smartbrain'),('runs','task_name','soc_patterns'),('runs','task_name','somatosensory'),('runs','task_name','sternberg'),('runs','task_name','stimulation'),('runs','task_name','story'),('runs','task_name','sweeptone'),('runs','task_name','switchspeed'),('runs','task_name','syllables'),('runs','task_name','t1_anatomy_scan'),('runs','task_name','t2_anatomy_scan'),('runs','task_name','t2star_anatomy_scan'),('runs','task_name','threshold'),('runs','task_name','tongue_movements'),('runs','task_name','touchy'),('runs','task_name','vardy_beeps'),('runs','task_name','verb'),('runs','task_name','verb_it'),('runs','task_name','visual_attention'),('runs','task_name','visual_field_map'),('runs','task_name','visual_left_right_map'),('runs','task_name','visual_speed_task'),('runs','task_name','visual_task_Serge'),('runs','task_name','visual_up_down_map'),('runs','task_name','vowels'),('runs','task_name','woezel_pip'),('runs','task_name','NOTE'),('runs','task_name','bair_finger_mapping'),('runs','task_name','ct_anatomy_scan'),('runs','task_name','flair_anatomy_scan'),('runs','task_name','frontal_eye_field'),('runs','task_name','MP2RAGE'),('runs','task_name','pd_anatomy_scan'),('runs','task_name','pRF_alessio'),('runs','task_name','top_up'),('runs','task_name','vts_prf'),('runs','task_name','vts_temporalpattern'),('runs','task_name','sixcatlocisidiff'),('runs','task_name','sixcatloctemporal');

DELIMITER ;;

CREATE TRIGGER validate_task_name_before_insert_to_runs
  BEFORE INSERT ON runs
  FOR EACH ROW
BEGIN
  IF NEW.task_name IS NOT NULL AND
    BINARY NEW.task_name NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'runs'
    AND column_name = 'task_name')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column task_name is not allowed in table runs';
  END IF;
END ;;

CREATE TRIGGER validate_task_name_before_update_to_runs
  BEFORE UPDATE ON runs
  FOR EACH ROW
BEGIN
  IF NEW.task_name IS NOT NULL AND
    BINARY NEW.task_name NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'runs'
    AND column_name = 'task_name')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column task_name is not allowed in table runs';
  END IF;
END ;;

DELIMITER ;

CREATE TABLE `intended_for` (
  `run_id` int(11) DEFAULT NULL COMMENT 'ID of runs table: this should point to the original task (top_up)',
  `target` int(11) DEFAULT NULL COMMENT 'Target: this should point to the "intended-for" task (bold task)',
  KEY `run_id` (`run_id`),
  KEY `target` (`target`),
  CONSTRAINT `intended_for_ibfk_1` FOREIGN KEY (`run_id`) REFERENCES `runs` (`id`) ON DELETE CASCADE,
  CONSTRAINT `intended_for_ibfk_2` FOREIGN KEY (`target`) REFERENCES `runs` (`id`) ON DELETE CASCADE
) ;


CREATE TABLE `runs_experimenters` (
  `run_id` int(11) DEFAULT NULL,
  `experimenter_id` int(11) DEFAULT NULL,
  UNIQUE KEY `runs_experimenters_unique` (`run_id`,`experimenter_id`),
  KEY `experimenter_id` (`experimenter_id`),
  CONSTRAINT `runs_experimenters_ibfk_1` FOREIGN KEY (`run_id`) REFERENCES `runs` (`id`) ON DELETE CASCADE,
  CONSTRAINT `runs_experimenters_ibfk_2` FOREIGN KEY (`experimenter_id`) REFERENCES `experimenters` (`id`) ON DELETE CASCADE
) ;


CREATE TABLE `runs_protocols` (
  `run_id` int(11) DEFAULT NULL,
  `protocol_id` int(11) DEFAULT NULL,
  UNIQUE KEY `runs_protocols_unique` (`run_id`,`protocol_id`),
  KEY `protocol_id` (`protocol_id`),
  CONSTRAINT `runs_protocols_ibfk_1` FOREIGN KEY (`run_id`) REFERENCES `runs` (`id`) ON DELETE CASCADE,
  CONSTRAINT `runs_protocols_ibfk_2` FOREIGN KEY (`protocol_id`) REFERENCES `protocols` (`id`) ON DELETE CASCADE
) ;

CREATE TABLE `events` (
  `run_id` int(11) DEFAULT NULL,
  `onset` float DEFAULT NULL COMMENT 'Onset: Onset (in seconds) of the event measured from the beginning of the acquisition of the first volume in the corresponding task imaging data file. Negative numbers in "onset" are allowed.',
  `duration` float DEFAULT NULL COMMENT 'Duration: Duration of the event (measured from onset) in seconds. Must always be either zero or positive. A "duration" value of zero implies that the delta function or event is so short as to be effectively modeled as an impulse.',
  `trial_type` text DEFAULT NULL COMMENT 'Trial Type: Primary categorisation of each trial to identify them as instances of the experimental conditions. For example: for a response inhibition task, it could take on values "go" and "no-go" to refer to response initiation and response inhibition experimental conditions.',
  `response_time` text DEFAULT NULL COMMENT 'Response Time: Response time measured in seconds. A negative response time can be used to represent preemptive responses and "n/a" denotes a missed response.',
  `value` text DEFAULT NULL COMMENT 'Value: Marker value associated with the event (e.g., the value of a TTL trigger that was recorded at the onset of the event).',
  KEY `run_id` (`run_id`),
  CONSTRAINT `events_ibfk_1` FOREIGN KEY (`run_id`) REFERENCES `runs` (`id`) ON DELETE CASCADE
) ;
