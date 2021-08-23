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
  `guild` VARCHAR(18) NOT NULL,
  `channel` VARCHAR(18) DEFAULT NULL,
  `message` VARCHAR(1850) NULL DEFAULT 'Welcome user_ping to server_name !',
  UNIQUE KEY `guild` (`guild`),
  UNIQUE KEY `channel` (`channel`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Table structure for table `economy`
--

DROP TABLE IF EXISTS `economy`;


CREATE TABLE `economy` (
  `guild` VARCHAR(18) NOT NULL,
  `user` VARCHAR(18) NOT NULL,
  `balance` INT NOT NULL DEFAULT 0,
  `items` JSON DEFAULT '{}'
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;
