SET NAMES latin1;
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE `recruits_conference` (
  `id` int(11) NOT NULL auto_increment,
  `abbrev` varchar(10) NOT NULL,
  `name` varchar(90) NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=9 DEFAULT CHARSET=latin1;

insert into `recruits_conference` values('1','SEC','Southeastern Conference'),
 ('2','ACC','Atlantic Coast Conference'),
 ('3','big-east','Big East Conference'),
 ('4','pac-10','Pacific 10 Conference'),
 ('5','big-ten','Big Ten Conference'),
 ('6','CUSA','Conference USA'),
 ('7','big-12','Big 12 Conference'),
 ('8','WAC','Western Athletic Conference');

SET FOREIGN_KEY_CHECKS = 1;