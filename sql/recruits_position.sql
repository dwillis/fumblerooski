SET NAMES latin1;
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE `recruits_position` (
  `id` int(11) NOT NULL auto_increment,
  `abbrev` varchar(5) NOT NULL,
  `name` varchar(25) NOT NULL,
  `position_type` varchar(1) NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=15 DEFAULT CHARSET=latin1;

insert into `recruits_position` values('1','QB','Quarterback','O'),
 ('2','RB','Running Back','O'),
 ('3','OL','Offensive Line','O'),
 ('4','TE','Tight End','O'),
 ('5','WR','Wide Receiver','O'),
 ('6','DL','Defensive Line','D'),
 ('7','LB','Linebacker','D'),
 ('8','DB','Defensive Back','D'),
 ('9','S','Safety','D'),
 ('10','P','Punter','S'),
 ('11','K','Kicker','S'),
 ('12','FB','Fullback','O'),
 ('13','DT','Defensive Tackle','D'),
 ('14','DE','Defensive End','D');

SET FOREIGN_KEY_CHECKS = 1;