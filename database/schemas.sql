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
  `public_key` TEXT DEFAULT NULL,
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
  `ip` VARCHAR(100) NOT NULL,
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
  `object_name` VARCHAR(512) NOT NULL,
  `dek_encrypted` TEXT NOT NULL,
  `iv` VARCHAR(64) NOT NULL,
  `sha256` VARCHAR(64) NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_documents_user` (`id_users`),
  KEY `idx_documents_folder` (`id_folder`),
  UNIQUE KEY `uniq_documents_object` (`object_name`),
  CONSTRAINT `fk_documents_users`
    FOREIGN KEY (`id_users`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_documents_folder`
    FOREIGN KEY (`id_folder`) REFERENCES `folders` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



-- 5)  shared file
CREATE TABLE `shared_files` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name_document` VARCHAR(255) NOT NULL,      -- fichier partagé
  `id_owner` INT NOT NULL,         -- propriétaire (créateur du partage)
  `id_document` INT DEFAULT NULL,
  `object_name` VARCHAR(512) NOT NULL,
  `taille_octets` BIGINT NOT NULL,
  `token` VARCHAR(128) NOT NULL,   -- lien unique
  `SEK` VARCHAR(255) NOT NULL,
  `iv` VARCHAR(64) NOT NULL,
  `sha256` VARCHAR(64) NOT NULL,
  `destination_email` VARCHAR(255) DEFAULT NULL,
  `expires_at` DATETIME NOT NULL,  -- date d’expiration
  `max_views` INT DEFAULT NULL,    -- nombre max de vues (optionnel)
  `views_count` INT NOT NULL DEFAULT 0,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,

  PRIMARY KEY (`id`),
  UNIQUE KEY `token_UNIQUE` (`token`),
  KEY `idx_shared_owner` (`id_owner`),
  KEY `idx_shared_document` (`id_document`),

  CONSTRAINT `fk_shared_owner`
    FOREIGN KEY (`id_owner`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_shared_document`
    FOREIGN KEY (`id_document`) REFERENCES `documents` (`id`) ON DELETE CASCADE

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6)  shared file
CREATE TABLE `shared_acces_log` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `id_shared_file` INT NOT NULL,   -- référence au fichier partagé
  `accessed_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- date et heure de l’accès
  `ip_address` VARCHAR(45) NOT NULL,  -- adresse IP
  `user_agent` VARCHAR(1024) NOT NULL, -- user agent du visiteur
  PRIMARY KEY (`id`),
  KEY `idx_shared_access` (`id_shared_file`),
  CONSTRAINT `fk_shared_access`
    FOREIGN KEY (`id_shared_file`) REFERENCES `shared_files` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--7) failed login attempts
CREATE TABLE `failed_login_attempts` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `email` VARCHAR(255) NOT NULL,
    `ip` VARCHAR(100) NOT NULL,
    `timestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- données de test
INSERT INTO users VALUES (1,'admin', 'prenom','test@gmail.com','$2b$12$9Y1fjD.S3knC7Yu9l3IQ9Ox.02e.tt83R7enbDyYhSN4Cp2QExK0y','Null', 0, 'Null');

