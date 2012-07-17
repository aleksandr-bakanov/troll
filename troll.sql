-- phpMyAdmin SQL Dump
-- version 3.3.10
-- http://www.phpmyadmin.net
--
-- Хост: localhost
-- Время создания: Июл 17 2012 г., 16:26
-- Версия сервера: 5.5.11
-- Версия PHP: 5.3.5

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- База данных: `troll`
--

-- --------------------------------------------------------

--
-- Структура таблицы `items`
--

CREATE TABLE IF NOT EXISTS `items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `params` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Информация о предметах (оружии и броне)' AUTO_INCREMENT=1 ;

--
-- Дамп данных таблицы `items`
--


-- --------------------------------------------------------

--
-- Структура таблицы `perks`
--

CREATE TABLE IF NOT EXISTS `perks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `params` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Информация о перках' AUTO_INCREMENT=1 ;

--
-- Дамп данных таблицы `perks`
--


-- --------------------------------------------------------

--
-- Структура таблицы `traps`
--

CREATE TABLE IF NOT EXISTS `traps` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `params` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Информация о ловушках' AUTO_INCREMENT=1 ;

--
-- Дамп данных таблицы `traps`
--


-- --------------------------------------------------------

--
-- Структура таблицы `user`
--

CREATE TABLE IF NOT EXISTS `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id игрока',
  `login` varchar(16) NOT NULL COMMENT 'логин, он же ник',
  `password` varchar(32) NOT NULL COMMENT 'Пароль в MD5',
  `is_playing` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Online ли игрок?',
  `params` text NOT NULL COMMENT 'Параметры игрока',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Информация об игроках' AUTO_INCREMENT=1 ;

--
-- Дамп данных таблицы `user`
--

