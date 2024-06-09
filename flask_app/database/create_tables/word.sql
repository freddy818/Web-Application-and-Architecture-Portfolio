CREATE TABLE IF NOT EXISTS `word` (
`date`           date         NOT NULL                    COMMENT 'the current date',
`word`           varchar(100) NOT NULL                    COMMENT 'the word of the day',
PRIMARY KEY (`date`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Contains daily word information";