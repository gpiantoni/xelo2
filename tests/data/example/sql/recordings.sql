CREATE TABLE `recordings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `run_id` int(11) DEFAULT NULL,
  `modality` text DEFAULT NULL,
  `offset` float DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `run_id` (`run_id`),
  CONSTRAINT `recordings_ibfk_1` FOREIGN KEY (`run_id`) REFERENCES `` (`id`) ON DELETE CASCADE
) ;

DELIMITER ;;

CREATE TRIGGER validate_modality_before_insert_to_recordings
  BEFORE INSERT ON recordings
  FOR EACH ROW
BEGIN
  IF NEW.modality NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings'
    AND column_name = 'modality')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column modality is not allowed in table recordings';
  END IF;
END ;;

CREATE TRIGGER add_id_to_subtable_recordings_mri
  AFTER INSERT ON recordings
  FOR EACH ROW
BEGIN
  IF NEW.modality IN ('bold', 'T1w', 'T2w', 'T2star', 'PD', 'FLAIR', 'angio', 'epi', 'dwi', 'ct')
  THEN
    INSERT INTO recordings_mri (recording_id) VALUES (NEW.id) ;
  END IF;
END ;;

CREATE TRIGGER add_id_to_subtable_recordings_epi
  AFTER INSERT ON recordings
  FOR EACH ROW
BEGIN
  IF NEW.modality IN ('bold', 'epi')
  THEN
    INSERT INTO recordings_epi (recording_id) VALUES (NEW.id) ;
  END IF;
END ;;

CREATE TRIGGER add_id_to_subtable_recordings_ieeg
  AFTER INSERT ON recordings
  FOR EACH ROW
BEGIN
  IF NEW.modality = 'ieeg'
  THEN
    INSERT INTO recordings_ieeg (recording_id) VALUES (NEW.id) ;
  END IF;
END ;;

CREATE TRIGGER validate_modality_before_update_to_recordings
  BEFORE UPDATE ON recordings
  FOR EACH ROW
BEGIN
  IF NEW.modality NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings'
    AND column_name = 'modality')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column modality is not allowed in table recordings';
  END IF;
END ;;

CREATE TRIGGER `replace_id_to_subtable_recordings_mri` AFTER UPDATE ON `recordings` FOR EACH ROW
BEGIN
  IF NEW.modality <> OLD.modality AND
    NEW.modality IN ('bold', 'T1w', 'T2w', 'T2star', 'PD', 'FLAIR', 'angio', 'epi', 'dwi', 'ct') AND
    NEW.id NOT IN (SELECT `recording_id` FROM `recordings_mri`)
  THEN
    INSERT INTO recordings_mri (recording_id) VALUES (NEW.id) ;
  END IF;
END ;;

CREATE TRIGGER `replace_id_to_subtable_recordings_epi` AFTER UPDATE ON `recordings` FOR EACH ROW
BEGIN
  IF NEW.modality <> OLD.modality AND
    NEW.modality IN ('bold', 'epi') AND
    NEW.id NOT IN (SELECT recording_id FROM recordings_epi)
  THEN
    INSERT INTO recordings_epi (recording_id) VALUES (NEW.id) ;
  END IF;
END ;;

CREATE TRIGGER `replace_id_to_subtable_recordings_ieeg` AFTER UPDATE ON `recordings` FOR EACH ROW
BEGIN
  IF NEW.modality <> OLD.modality AND
    NEW.modality = 'ieeg' AND
    NEW.id NOT IN (SELECT recording_id FROM recordings_ieeg)
  THEN
    INSERT INTO recordings_ieeg (recording_id) VALUES (NEW.id) ;
  END IF;
END ;;

DELIMITER ;
