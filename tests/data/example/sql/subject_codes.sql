CREATE TABLE `subject_codes` (
  `subject_id` int(11) DEFAULT NULL,
  `code` varchar(256) NOT NULL,
  UNIQUE KEY `code` (`code`),
  KEY `subject_id` (`subject_id`),
  CONSTRAINT `subject_codes_ibfk_1` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`) ON DELETE CASCADE
) ;

