-- phpMyAdmin SQL Dump
-- version 4.5.1
-- http://www.phpmyadmin.net
--
-- Host: 127.0.0.1
-- Generation Time: Sep 30, 2021 at 12:35 AM
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

--
-- Table structure for table `chatrooms`
--

CREATE TABLE `chatrooms` (
  `ID_ChatRoom` int(11) NOT NULL,
  `RoomName` varchar(45) NOT NULL,
  `RoomOwner` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------
ALTER TABLE users
ADD COLUMN Image VARCHAR(255) AFTER Email;

--
-- Table structure for table `roommembers`
--

CREATE TABLE `roommembers` (
  `ID_RoomMembers` int(11) NOT NULL,
  `ChatRoomID` int(11) NOT NULL,
  `ChatRoomMember` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `ID_User` int(10) UNSIGNED NOT NULL,
  `Handle` varchar(45) NOT NULL,
  `Password` varchar(16) NOT NULL DEFAULT '',
  `Email` varchar(45) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`ID_User`, `Handle`, `Password`, `Email`) VALUES
(1, 'TesterMann', 'test', 'test@gmail.com');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `chatrooms`
--
ALTER TABLE `chatrooms`
  ADD PRIMARY KEY (`ID_ChatRoom`);

--
-- Indexes for table `roommembers`
--
ALTER TABLE `roommembers`
  ADD PRIMARY KEY (`ID_RoomMembers`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`ID_User`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `chatrooms`
--
ALTER TABLE `chatrooms`
  MODIFY `ID_ChatRoom` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `roommembers`
--
ALTER TABLE `roommembers`
  MODIFY `ID_RoomMembers` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `ID_User` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
