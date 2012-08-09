-- phpMyAdmin SQL Dump
-- version 3.4.10.1deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jul 22, 2012 at 11:28 PM
-- Server version: 5.5.24
-- PHP Version: 5.3.10-1ubuntu3.2

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `troll`
--

-- --------------------------------------------------------

--
-- Table structure for table `items`
--

CREATE TABLE IF NOT EXISTS `items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `params` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COMMENT='Информация о предметах (оружии и броне)' AUTO_INCREMENT=4 ;

--
-- Dumping data for table `items`
--

INSERT INTO `items` (`id`, `params`) VALUES
(1, '{"id":1, "type":1, "name":"Тапки милосердия", "cost":10, "weight":2, "damage":"1k+1", "precision":9, "range":1, "damageRange":0, "points":2}'),
(2, '{"id":2, "type":2, "name":"Фуфайка", "cost":10, "weight":4, "resistance":1}'),
(3, '{"id":3, "type":3, "name":"Colin''s Jeans", "cost":10, "weight":3, "resistance":1}');

-- --------------------------------------------------------

--
-- Table structure for table `perks`
--

CREATE TABLE IF NOT EXISTS `perks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `params` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Информация о перках' AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `traps`
--

CREATE TABLE IF NOT EXISTS `traps` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `params` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Информация о ловушках' AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE IF NOT EXISTS `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id игрока',
  `login` varchar(16) NOT NULL COMMENT 'логин, он же ник',
  `password` varchar(32) NOT NULL COMMENT 'Пароль в MD5',
  `is_playing` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Online ли игрок?',
  `params` text NOT NULL COMMENT 'Параметры игрока',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COMMENT='Информация об игроках' AUTO_INCREMENT=3 ;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id`, `login`, `password`, `is_playing`, `params`) VALUES
(2, 'a', 'c4ca4238a0b923820dcc509a6f75849b', 0, '{"deviation": 8, "dexterity": 10, "armour": 0, "strength": 12, "handWeapon": 1, "pants": 0, "money": 123, "energy": 75, "resistance": 0, "maxLoad": 28, "backpack": {"1": 5}, "actPoints": 5, "perks": {}, "health": 13, "beltWeapon": 0, "usedOP": 50, "hitPoints": 13, "speed": 5.75, "intellect": 10, "unusedOP": 0}');

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
