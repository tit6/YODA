DROP TABLE IF EXISTS `documents`;
DROP TABLE IF EXISTS `folders`;
DROP TABLE IF EXISTS `logs`;
DROP TABLE IF EXISTS `users`;


-- 1) users
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(45) NOT NULL,
  `prenom` varchar(45) NOT NULL,
  `email` varchar(45) NOT NULL,
  `mdp` varchar(255) NOT NULL,
  `secret_a2f` varchar(128) DEFAULT NULL, 
  `statue_a2f` INT DEFAULT '0' NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `secret_a2f_UNIQUE` (`secret_a2f`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 2) logs
CREATE TABLE `logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_users` int NOT NULL,
  `statut` int NOT NULL,
  `action` varchar(100) NOT NULL,
  `timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `id_users_idx` (`id_users`),
  CONSTRAINT `fk_logs_users` FOREIGN KEY (`id_users`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 3) folders
CREATE TABLE `folders` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `id_users` INT NOT NULL,
  `nom` VARCHAR(255) NOT NULL,
  `parent_id` INT DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_folders_user` (`id_users`),
  KEY `idx_folders_parent` (`parent_id`),
  CONSTRAINT `fk_folders_users`
    FOREIGN KEY (`id_users`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_folders_parent`
    FOREIGN KEY (`parent_id`) REFERENCES `folders` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4) documents
CREATE TABLE `documents` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `id_users` INT NOT NULL,
  `id_folder` INT DEFAULT NULL,
  `nom_original` VARCHAR(255) NOT NULL,
  `extension` VARCHAR(10),
  `taille_octets` BIGINT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_documents_user` (`id_users`),
  KEY `idx_documents_folder` (`id_folder`),
  CONSTRAINT `fk_documents_users`
    FOREIGN KEY (`id_users`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_documents_folder`
    FOREIGN KEY (`id_folder`) REFERENCES `folders` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- données de test
INSERT INTO users VALUES (1,'admin', 'prenom','test@gmail.com','$2b$12$9Y1fjD.S3knC7Yu9l3IQ9Ox.02e.tt83R7enbDyYhSN4Cp2QExK0y','Null', 0);

