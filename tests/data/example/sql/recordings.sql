CREATE TABLE `recordings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `run_id` int(11) DEFAULT NULL,
  `modality` text DEFAULT NULL COMMENT 'Modality: Name of recording modality (this is BIDS specific)' ,
  `offset` float DEFAULT 0 COMMENT 'Offset: Offset between the run time and the time stamp in the dataset file. When you use only one recording system (say Micromed), there is no issue but if you use two recording systems (Micromed, Blackrock, Dataglove), you can use this value to correct the offset between the clock time of the run (and events) and the clock time of this specific recording',
  PRIMARY KEY (`id`),
  KEY `run_id` (`run_id`),
  CONSTRAINT `recordings_ibfk_1` FOREIGN KEY (`run_id`) REFERENCES `runs` (`id`) ON DELETE CASCADE
) ;

INSERT INTO `allowed_values` VALUES ('recordings','modality','ieeg'),('recordings','modality','meg'),('recordings','modality','eeg'),('recordings','modality','bold'),('recordings','modality','T1w'),('recordings','modality','T2w'),('recordings','modality','T2star'),('recordings','modality','PD'),('recordings','modality','FLAIR'),('recordings','modality','angio'),('recordings','modality','epi'),('recordings','modality','dwi'),('recordings','modality','ct'),('recordings','modality','physio'),('recordings','modality','stim');

DELIMITER ;;

CREATE TRIGGER validate_modality_before_insert_to_recordings
  BEFORE INSERT ON recordings
  FOR EACH ROW
BEGIN
  IF NEW.modality IS NOT NULL AND
    BINARY NEW.modality NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings'
    AND column_name = 'modality')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column modality is not allowed in table recordings';
  END IF;
END ;;

CREATE TRIGGER validate_modality_before_update_to_recordings
  BEFORE UPDATE ON recordings
  FOR EACH ROW
BEGIN
  IF NEW.modality IS NOT NULL AND
    BINARY NEW.modality NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings'
    AND column_name = 'modality')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column modality is not allowed in table recordings';
  END IF;
END ;;

DELIMITER ;
