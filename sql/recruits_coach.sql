SET NAMES latin1;
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE `recruits_coach` (
  `id` int(11) NOT NULL auto_increment,
  `first_name` varchar(75) NOT NULL,
  `last_name` varchar(90) NOT NULL,
  `birth_date` date default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;

insert into `recruits_coach` values('1','Mike','Cain',null),
 ('2','Urban','Meyer',null);

SET FOREIGN_KEY_CHECKS = 1;