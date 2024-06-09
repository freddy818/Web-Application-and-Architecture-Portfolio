CREATE TABLE IF NOT EXISTS `leaderboard` (
`email`           varchar(100) NOT NULL            		  COMMENT 'the email',
`time`            float(11)    NOT NULL                   COMMENT 'amount of time it took to complete',
PRIMARY KEY (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Contains wordle leaderboard information";