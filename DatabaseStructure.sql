CREATE DATABASE IF NOT EXISTS `tragedy`;
USE `tragedy`;

--
-- Table structure for table `prefix`
--

DROP TABLE IF EXISTS `prefix`;


CREATE TABLE `prefix` (
  `guild` varchar(18) DEFAULT NULL,
  `prefix1` varchar(10) DEFAULT NULL,
  `prefix2` varchar(10) DEFAULT NULL,
  `prefix3` varchar(10) DEFAULT NULL,
  `prefix4` varchar(10) DEFAULT NULL,
  `prefix5` varchar(10) DEFAULT NULL,
  `defaultPrefix` varchar(3) DEFAULT 'xv ',
  UNIQUE KEY `guild` (`guild`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Table structure for table `warns`
--

DROP TABLE IF EXISTS `warns`;


CREATE TABLE `warns` (
  `id` varchar(10) NOT NULL,
  `guild` varchar(19) NOT NULL,
  `user` varchar(18) NOT NULL,
  `warner` varchar(18) NOT NULL,
  `reason` varchar(125) NOT NULL,
  `time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Table structure for table `temp-emails`
--

DROP TABLE IF EXISTS `temp-emails`;


CREATE TABLE `temp-emails` (
  `user` varchar(18) NOT NULL,
  `email` varchar(255),
  UNIQUE KEY `user` (`user`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Table structure for table `welcome`
--

DROP TABLE IF EXISTS `welcome`;


CREATE TABLE `welcome` (
  `guild` varchar(18) NOT NULL,
  `channel` varchar(18) DEFAULT NULL,
  `message` varchar(1850) NULL DEFAULT 'Welcome user_ping to server_name !',
  UNIQUE KEY `guild` (`guild`),
  UNIQUE KEY `channel` (`channel`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Table structure for table `economy`
--

DROP TABLE IF EXISTS `economy`;


CREATE TABLE `economy` (
  `guild` varchar(18) NOT NULL,
  `user` varchar(18) NOT NULL,
  `balance` INT NOT NULL DEFAULT 0,
  `items` JSON DEFAULT '{}'
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

--
-- Table structure for table `auto-mod`
--

DROP TABLE IF EXISTS `auto-mod`;


CREATE TABLE `auto-mod` (
  `guild` varchar(18) NOT NULL,
  `config` LONGBLOB NOT NULL DEFAULT '\x80\x04\x95\x90\x00\x00\x00\x00\x00\x00\x00\x8c\x08__main__\x94\x8c\rAutoModConfig\x94\x93\x94)\x81\x94}\x94(\x8c\x10profanity_filter\x94\x89\x8c\x0blink_filter\x94\x89\x8c\x0emention_filter\x94\x89\x8c\x0emention_length\x94K\x00\x8c\x0bspam_filter\x94\x89\x8c\nspam_ratio\x94K\x00K\x00\x86\x94ub.',
  UNIQUE KEY `guild` (`guild`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;