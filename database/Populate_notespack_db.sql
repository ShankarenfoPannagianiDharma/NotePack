-- phpMyAdmin SQL Dump
-- version 4.5.1
-- http://www.phpmyadmin.net
--
-- Host: 127.0.0.1
-- Generation Time: Nov 06, 2021 at 01:33 AM
-- Server version: 10.1.19-MariaDB
-- PHP Version: 5.6.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `notespack_db`
--

-- --------------------------------------------------------

-- Delete old tables if exists
DROP TABLE IF EXISTS notespack_db.chatmessages;
DROP TABLE IF EXISTS notespack_db.roommembers;
DROP TABLE IF EXISTS notespack_db.chatrooms;
DROP TABLE IF EXISTS notespack_db.users;

--
-- Table structure for table `users`
--
CREATE TABLE `users` (
  `ID_User` int(10) NOT NULL AUTO_INCREMENT,
  `Handle` varchar(45) NOT NULL,
  `Password` varchar(45) NOT NULL DEFAULT '',
  `Email` varchar(45) NOT NULL,
  PRIMARY KEY (`ID_User`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Table structure for table `chatrooms`
--
CREATE TABLE `chatrooms` (
  `ID_ChatRoom` int(11) NOT NULL AUTO_INCREMENT,
  `RoomName` varchar(45) NOT NULL,
  `ID_RoomOwner` int(11) NOT NULL,
  `isPrivate` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`ID_ChatRoom`),
  FOREIGN KEY (`ID_RoomOwner`) REFERENCES users(`ID_User`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Table structure for table `roommembers`
--
CREATE TABLE `roommembers` (
  `ID_RoomMembers` int(11) NOT NULL AUTO_INCREMENT,
  `ID_ChatRoom` int(11) NOT NULL,
  `ID_Members` int(11) NOT NULL,
  PRIMARY KEY (`ID_RoomMembers`),
  FOREIGN KEY (`ID_ChatRoom`) REFERENCES chatrooms(`ID_Chatroom`),
  FOREIGN KEY (`ID_Members`) REFERENCES users(`ID_User`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Table structure for table `chatmessages`
--
CREATE TABLE `chatmessages` (
  `ID_Msg` int(11) NOT NULL AUTO_INCREMENT,
  `ID_ChatRoom` int(11) NOT NULL,
  `ID_User` int(10) NOT NULL,
  `Content_Msg` text NOT NULL,
  `Timestamp_Msg` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID_Msg`),
  FOREIGN KEY (`ID_ChatRoom`) REFERENCES chatrooms(`ID_Chatroom`),
  FOREIGN KEY (`ID_User`) REFERENCES users(`ID_User`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- --------------------------------------------------------

--
-- Dumping data for table `users`
--
INSERT INTO `users` (`ID_User`, `Handle`, `Password`, `Email`) VALUES
(1, 'TesterMann', 'test', 'test@gmail.com');
