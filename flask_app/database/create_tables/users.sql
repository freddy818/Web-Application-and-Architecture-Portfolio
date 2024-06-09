CREATE TABLE IF NOT EXISTS `users` (
`user_id`         int(11)  	   NOT NULL auto_increment	  COMMENT 'the id of this user',
`role`            varchar(10)  NOT NULL                   COMMENT 'the role of the user; options include: owner and guest',
`email`           varchar(100) NOT NULL            		  COMMENT 'the email',
`password`        varchar(256) NOT NULL                   COMMENT 'the password',
`wordle_visits`   int(11)      NOT NULL                   COMMENT 'the amount of times the user visited the wordle page',
`completed_game`  int(11)      NOT NULL                   COMMENT 'whether or not the user has completed the wordle game',
PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Contains site user information";