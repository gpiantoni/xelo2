CREATE TABLE `recordings_ieeg` (
  `recording_id` int(11) DEFAULT NULL,
  `channel_group_id` int(11) DEFAULT NULL,
  `electrode_group_id` int(11) DEFAULT NULL,
  `Manufacturer` text DEFAULT NULL,
  `Reference` text DEFAULT NULL,
  UNIQUE KEY `recording_id` (`recording_id`),
  KEY `channel_group_id` (`channel_group_id`),
  KEY `electrode_group_id` (`electrode_group_id`),
  CONSTRAINT `recordings_ieeg_ibfk_1` FOREIGN KEY (`recording_id`) REFERENCES `recordings` (`id`) ON DELETE CASCADE,
  CONSTRAINT `recordings_ieeg_ibfk_2` FOREIGN KEY (`channel_group_id`) REFERENCES `channel_groups` (`id`) ON DELETE CASCADE,
  CONSTRAINT `recordings_ieeg_ibfk_3` FOREIGN KEY (`electrode_group_id`) REFERENCES `electrode_groups` (`id`) ON DELETE CASCADE
) ;

INSERT INTO `allowed_values` VALUES ('recordings_ieeg','Manufacturer','BlackRock'),('recordings_ieeg','Manufacturer','Micromed');

DELIMITER ;;

CREATE TRIGGER validate_Manufacturer_before_insert_to_recordings_ieeg
  BEFORE INSERT ON recordings_ieeg
  FOR EACH ROW
BEGIN
  IF NEW.Manufacturer NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_ieeg'
    AND column_name = 'Manufacturer')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column Manufacturer is not allowed in table recordings_ieeg';
  END IF;
END ;;

CREATE TRIGGER validate_Manufacturer_before_update_to_recordings_ieeg
  BEFORE UPDATE ON recordings_ieeg
  FOR EACH ROW
BEGIN
  IF NEW.Manufacturer NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_ieeg'
    AND column_name = 'Manufacturer')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column Manufacturer is not allowed in table recordings_ieeg';
  END IF;
END ;;

DELIMITER ;

CREATE TABLE `recordings_mri` (
  `recording_id` int(11) DEFAULT NULL,
  `region_of_interest` text DEFAULT NULL,
  `Sequence` text DEFAULT NULL,
  `MultibandAccelerationFactor` int(11) DEFAULT NULL,
  `PhaseEncodingDirection` text DEFAULT NULL,
  `SliceEncodingDirection` text DEFAULT NULL,
  `SliceOrder` text DEFAULT NULL,
  UNIQUE KEY `recording_id` (`recording_id`),
  CONSTRAINT `recordings_mri_ibfk_1` FOREIGN KEY (`recording_id`) REFERENCES `recordings` (`id`) ON DELETE CASCADE
) ;

INSERT INTO `allowed_values` VALUES ('recordings_mri','PhaseEncodingDirection','LR'),('recordings_mri','PhaseEncodingDirection','RL'),('recordings_mri','PhaseEncodingDirection','AP'),('recordings_mri','PhaseEncodingDirection','PA'),('recordings_mri','PhaseEncodingDirection','SI'),('recordings_mri','PhaseEncodingDirection','IS');
INSERT INTO `allowed_values` VALUES ('recordings_mri','SliceEncodingDirection','LR'),('recordings_mri','SliceEncodingDirection','RL'),('recordings_mri','SliceEncodingDirection','AP'),('recordings_mri','SliceEncodingDirection','PA'),('recordings_mri','SliceEncodingDirection','SI'),('recordings_mri','SliceEncodingDirection','IS');
INSERT INTO `allowed_values` VALUES ('recordings_mri','SliceOrder','Sequential'),('recordings_mri','SliceOrder','Interleaved');
INSERT INTO `allowed_values` VALUES ('recordings_mri','Sequence','3T FLAIR'),('recordings_mri','Sequence','3T T1w'),('recordings_mri','Sequence','3T Gradient-Echo Multiband'),('recordings_mri','Sequence','7T Gradient-Echo Head Coil'),('recordings_mri','Sequence','7T Wouter 1.6s'),('recordings_mri','Sequence','3T DWI'),('recordings_mri','Sequence','3T Spin-Echo Multiband'),('recordings_mri','Sequence','7T Gradient-Echo Surface Coil'),('recordings_mri','Sequence','7T Spin-Echo Surface Coil'),('recordings_mri','Sequence','3T PRESTO'),('recordings_mri','Sequence','7T Standard 2.1s'),('recordings_mri','Sequence','7T MP2RAGE');

DELIMITER ;;

CREATE TRIGGER `validate_PhaseEncodingDirection_before_insert_to_recordings_mri` BEFORE INSERT ON `recordings_mri` FOR EACH ROW
BEGIN
  IF NEW.PhaseEncodingDirection NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_mri'
    AND column_name = 'PhaseEncodingDirection')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column PhaseEncodingDirection is not allowed in table recordings_mri';
  END IF;
END ;;

CREATE TRIGGER `validate_SliceEncodingDirection_before_insert_to_recordings_mri` BEFORE INSERT ON `recordings_mri` FOR EACH ROW
BEGIN
  IF NEW.SliceEncodingDirection NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_mri'
    AND column_name = 'SliceEncodingDirection')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column SliceEncodingDirection is not allowed in table recordings_mri';
  END IF;
END ;;

CREATE TRIGGER `validate_Sequence_before_insert_to_recordings_mri` BEFORE INSERT ON `recordings_mri` FOR EACH ROW
BEGIN
  IF NEW.Sequence NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_mri'
    AND column_name = 'Sequence')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column Sequence is not allowed in table recordings_mri';
  END IF;
END ;;

CREATE TRIGGER `validate_SliceOrder_before_insert_to_recordings_mri` BEFORE INSERT ON `recordings_mri` FOR EACH ROW
BEGIN
  IF NEW.SliceOrder NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_mri'
    AND column_name = 'SliceOrder')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column SliceOrder is not allowed in table recordings_mri';
  END IF;
END ;;

CREATE TRIGGER `validate_SliceEncodingDirection_before_update_to_recordings_mri` BEFORE UPDATE ON `recordings_mri` FOR EACH ROW
BEGIN
  IF NEW.SliceEncodingDirection NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_mri'
    AND column_name = 'SliceEncodingDirection')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column SliceEncodingDirection is not allowed in table recordings_mri';
  END IF;
END ;;

CREATE TRIGGER `validate_Sequence_before_update_to_recordings_mri` BEFORE UPDATE ON `recordings_mri` FOR EACH ROW
BEGIN
  IF NEW.Sequence NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_mri'
    AND column_name = 'Sequence')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column Sequence is not allowed in table recordings_mri';
  END IF;
END ;;

CREATE TRIGGER `validate_PhaseEncodingDirection_before_update_to_recordings_mri` BEFORE UPDATE ON `recordings_mri` FOR EACH ROW
BEGIN
  IF NEW.PhaseEncodingDirection NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_mri'
    AND column_name = 'PhaseEncodingDirection')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column PhaseEncodingDirection is not allowed in table recordings_mri';
  END IF;
END ;;

CREATE TRIGGER `validate_SliceOrder_before_update_to_recordings_mri` BEFORE UPDATE ON `recordings_mri` FOR EACH ROW
BEGIN
  IF NEW.SliceOrder NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_mri'
    AND column_name = 'SliceOrder')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column SliceOrder is not allowed in table recordings_mri';
  END IF;
END ;;

DELIMITER ;

CREATE TABLE `recordings_epi` (
  `recording_id` int(11) DEFAULT NULL,
  `RepetitionTime` float DEFAULT NULL,
  `NumberOfVolumesDiscardedByScanner` int(11) DEFAULT NULL,
  UNIQUE KEY `recording_id` (`recording_id`),
  CONSTRAINT `recordings_epi_ibfk_1` FOREIGN KEY (`recording_id`) REFERENCES `recordings` (`id`) ON DELETE CASCADE
) ;

DELIMITER ;;

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

DELIMITER ;
