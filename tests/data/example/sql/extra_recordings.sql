CREATE TABLE `recordings_ephys` (
  `recording_id` int(11) DEFAULT NULL,
  `channel_group_id` int(11) DEFAULT NULL,
  `electrode_group_id` int(11) DEFAULT NULL,
  `Manufacturer` text DEFAULT NULL COMMENT 'Manufacturer: Manufacturer of the amplifier system (e.g., "TDT", "Blackrock")',
  UNIQUE KEY `recording_id` (`recording_id`),
  KEY `channel_group_id` (`channel_group_id`),
  KEY `electrode_group_id` (`electrode_group_id`),
  CONSTRAINT `recordings_ephys_ibfk_1` FOREIGN KEY (`recording_id`) REFERENCES `recordings` (`id`) ON DELETE CASCADE,
  CONSTRAINT `recordings_ephys_ibfk_2` FOREIGN KEY (`channel_group_id`) REFERENCES `channel_groups` (`id`) ON DELETE CASCADE,
  CONSTRAINT `recordings_ephys_ibfk_3` FOREIGN KEY (`electrode_group_id`) REFERENCES `electrode_groups` (`id`) ON DELETE CASCADE
) ;

INSERT INTO `allowed_values` VALUES ('recordings_ephys','Manufacturer','BlackRock'),('recordings_ephys','Manufacturer','Micromed');

DELIMITER ;;

CREATE TRIGGER add_id_to_subtable_recordings_ephys
  AFTER INSERT ON recordings
  FOR EACH ROW
BEGIN
  IF NEW.modality IN ('ieeg', 'eeg', 'meg')
  THEN
    INSERT INTO recordings_ephys (recording_id) VALUES (NEW.id) ;
  END IF;
END ;;

CREATE TRIGGER `replace_id_to_subtable_recordings_ephys` AFTER UPDATE ON `recordings` FOR EACH ROW
BEGIN
  IF NEW.modality <> OLD.modality AND
    NEW.modality IN ('ieeg', 'eeg', 'meg') AND
    NEW.id NOT IN (SELECT recording_id FROM recordings_ephys)
  THEN
    INSERT INTO recordings_ephys (recording_id) VALUES (NEW.id) ;
  END IF;
END ;;

CREATE TRIGGER validate_Manufacturer_before_insert_to_recordings_ephys
  BEFORE INSERT ON recordings_ephys
  FOR EACH ROW
BEGIN
  IF NEW.Manufacturer IS NOT NULL AND
    BINARY NEW.Manufacturer NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_ephys'
    AND column_name = 'Manufacturer')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column Manufacturer is not allowed in table recordings_ephys';
  END IF;
END ;;

CREATE TRIGGER validate_Manufacturer_before_update_to_recordings_ephys
  BEFORE UPDATE ON recordings_ephys
  FOR EACH ROW
BEGIN
  IF NEW.Manufacturer IS NOT NULL AND
    BINARY NEW.Manufacturer NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_ephys'
    AND column_name = 'Manufacturer')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column Manufacturer is not allowed in table recordings_ephys';
  END IF;
END ;;

DELIMITER ;

CREATE TABLE `recordings_mri` (
  `recording_id` int(11) DEFAULT NULL,
  `region_of_interest` text DEFAULT NULL COMMENT 'Region of Interest: Free text to describe the ROI ("whole brain", "occipital cortex")',
  `Sequence` text DEFAULT NULL COMMENT 'Sequence: Scanning sequence used',
  `MultibandAccelerationFactor` int(11) DEFAULT NULL COMMENT 'Multiband Acceleration Factor: 1 means No multiband',
  `SliceEncodingDirection` text DEFAULT NULL COMMENT 'Slice Encoding Direction: ',
  `SliceOrder` text DEFAULT NULL COMMENT 'Slice Order: This parameter is not in BIDS but it is used to compute SliceTiming. Use "Sequential" when Multiband is present',
  `PhaseEncodingDirection` text DEFAULT NULL COMMENT 'Phase Encoding Direction: If Philips scanner says "P", you should enter "AP"',
  UNIQUE KEY `recording_id` (`recording_id`),
  CONSTRAINT `recordings_mri_ibfk_1` FOREIGN KEY (`recording_id`) REFERENCES `recordings` (`id`) ON DELETE CASCADE
) ;

INSERT INTO `allowed_values` VALUES ('recordings_mri','PhaseEncodingDirection','LR'),('recordings_mri','PhaseEncodingDirection','RL'),('recordings_mri','PhaseEncodingDirection','AP'),('recordings_mri','PhaseEncodingDirection','PA'),('recordings_mri','PhaseEncodingDirection','SI'),('recordings_mri','PhaseEncodingDirection','IS');
INSERT INTO `allowed_values` VALUES ('recordings_mri','SliceEncodingDirection','LR'),('recordings_mri','SliceEncodingDirection','RL'),('recordings_mri','SliceEncodingDirection','AP'),('recordings_mri','SliceEncodingDirection','PA'),('recordings_mri','SliceEncodingDirection','SI'),('recordings_mri','SliceEncodingDirection','IS');
INSERT INTO `allowed_values` VALUES ('recordings_mri','SliceOrder','Sequential'),('recordings_mri','SliceOrder','Interleaved'),('recordings_mri','SliceOrder','3D');
INSERT INTO `allowed_values` VALUES ('recordings_mri','Sequence','3T FLAIR'),('recordings_mri','Sequence','3T T1w'),('recordings_mri','Sequence','3T Gradient-Echo Multiband'),('recordings_mri','Sequence','7T Gradient-Echo Head Coil'),('recordings_mri','Sequence','7T Wouter 1.6s'),('recordings_mri','Sequence','3T DWI'),('recordings_mri','Sequence','3T Spin-Echo Multiband'),('recordings_mri','Sequence','7T Gradient-Echo Surface Coil'),('recordings_mri','Sequence','7T Spin-Echo Surface Coil'),('recordings_mri','Sequence','3T PRESTO'),('recordings_mri','Sequence','7T Standard 2.1s'),('recordings_mri','Sequence','7T MP2RAGE');

DELIMITER ;;

CREATE TRIGGER add_id_to_subtable_recordings_mri
  AFTER INSERT ON recordings
  FOR EACH ROW
BEGIN
  IF NEW.modality IN ('bold', 'T1w', 'T2w', 'T2star', 'PD', 'FLAIR', 'angio', 'epi', 'dwi', 'ct')
  THEN
    INSERT INTO recordings_mri (recording_id) VALUES (NEW.id) ;
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

CREATE TRIGGER `validate_PhaseEncodingDirection_before_insert_to_recordings_mri` 
  BEFORE INSERT ON `recordings_mri` 
  FOR EACH ROW
BEGIN
  IF NEW.PhaseEncodingDirection IS NOT NULL AND
    BINARY NEW.PhaseEncodingDirection NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_mri'
    AND column_name = 'PhaseEncodingDirection')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column PhaseEncodingDirection is not allowed in table recordings_mri';
  END IF;
END ;;

CREATE TRIGGER `validate_PhaseEncodingDirection_before_update_to_recordings_mri` 
  BEFORE UPDATE ON `recordings_mri` 
  FOR EACH ROW
BEGIN
  IF NEW.PhaseEncodingDirection IS NOT NULL AND
    BINARY NEW.PhaseEncodingDirection NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_mri'
    AND column_name = 'PhaseEncodingDirection')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column PhaseEncodingDirection is not allowed in table recordings_mri';
  END IF;
END ;;

CREATE TRIGGER `validate_SliceEncodingDirection_before_insert_to_recordings_mri` 
  BEFORE INSERT ON `recordings_mri` 
  FOR EACH ROW
BEGIN
  IF NEW.SliceEncodingDirection IS NOT NULL AND
    BINARY NEW.SliceEncodingDirection NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_mri'
    AND column_name = 'SliceEncodingDirection')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column SliceEncodingDirection is not allowed in table recordings_mri';
  END IF;
END ;;

CREATE TRIGGER `validate_SliceEncodingDirection_before_update_to_recordings_mri` 
  BEFORE UPDATE ON `recordings_mri` 
  FOR EACH ROW
BEGIN
  IF NEW.SliceEncodingDirection IS NOT NULL AND
    BINARY NEW.SliceEncodingDirection NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_mri'
    AND column_name = 'SliceEncodingDirection')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column SliceEncodingDirection is not allowed in table recordings_mri';
  END IF;
END ;;

CREATE TRIGGER `validate_Sequence_before_insert_to_recordings_mri` 
  BEFORE INSERT ON `recordings_mri` 
  FOR EACH ROW
BEGIN
  IF NEW.Sequence IS NOT NULL AND
    BINARY NEW.Sequence NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_mri'
    AND column_name = 'Sequence')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column Sequence is not allowed in table recordings_mri';
  END IF;
END ;;

CREATE TRIGGER `validate_Sequence_before_update_to_recordings_mri` 
  BEFORE UPDATE ON `recordings_mri` 
  FOR EACH ROW
BEGIN
  IF NEW.Sequence IS NOT NULL AND
    BINARY NEW.Sequence NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_mri'
    AND column_name = 'Sequence')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column Sequence is not allowed in table recordings_mri';
  END IF;
END ;;

CREATE TRIGGER `validate_SliceOrder_before_insert_to_recordings_mri` 
  BEFORE INSERT ON `recordings_mri` 
  FOR EACH ROW
BEGIN
  IF NEW.SliceOrder IS NOT NULL AND
    BINARY NEW.SliceOrder NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_mri'
    AND column_name = 'SliceOrder')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column SliceOrder is not allowed in table recordings_mri';
  END IF;
END ;;

CREATE TRIGGER `validate_SliceOrder_before_update_to_recordings_mri` 
  BEFORE UPDATE ON `recordings_mri` 
  FOR EACH ROW
BEGIN
  IF NEW.SliceOrder IS NOT NULL AND
    BINARY NEW.SliceOrder NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_mri'
    AND column_name = 'SliceOrder')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column SliceOrder is not allowed in table recordings_mri';
  END IF;
END ;;

CREATE TRIGGER `update_SliceOrder_before_insert_to_recordings_mri`
  BEFORE INSERT ON recordings_mri
  FOR EACH ROW
BEGIN
  IF NEW.Sequence = '3T PRESTO'
  THEN
    SET NEW.SliceOrder = '3D' ;
  END IF;
END ;;

CREATE TRIGGER `update_SliceOrder_before_update_to_recordings_mri`
  BEFORE UPDATE ON recordings_mri
  FOR EACH ROW
BEGIN
  IF NEW.Sequence = '3T PRESTO'
  THEN
    SET NEW.SliceOrder = '3D' ;
  END IF;
END ;;

DELIMITER ;

CREATE TABLE `recordings_epi` (
  `recording_id` int(11) DEFAULT NULL,
  `RepetitionTime` float DEFAULT NULL COMMENT 'Repetition Time: Philips calls it "Dynamic scan time"',
  UNIQUE KEY `recording_id` (`recording_id`),
  CONSTRAINT `recordings_epi_ibfk_1` FOREIGN KEY (`recording_id`) REFERENCES `recordings` (`id`) ON DELETE CASCADE
) ;

DELIMITER ;;

CREATE TRIGGER add_id_to_subtable_recordings_epi
  AFTER INSERT ON recordings
  FOR EACH ROW
BEGIN
  IF NEW.modality IN ('bold', 'epi')
  THEN
    INSERT INTO recordings_epi (recording_id) VALUES (NEW.id) ;
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

DELIMITER ;
