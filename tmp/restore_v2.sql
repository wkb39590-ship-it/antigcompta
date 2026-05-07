-- ============================================================
-- RESTAURATION POSTGRESQL v2 - Sans transaction globale
-- Chaque table s insere independamment
-- ============================================================

SET session_replication_role = replica;

-- === cabinets (depuis SQLite:cabinets, 3 lignes) ===
DELETE FROM "cabinets";
INSERT INTO "cabinets" ("id", "nom", "email", "telephone", "adresse", "logo_path", "created_at") VALUES (1, 'Cabinet Test', NULL, NULL, NULL, NULL, '2026-02-24 09:37:57') ON CONFLICT DO NOTHING;
INSERT INTO "cabinets" ("id", "nom", "email", "telephone", "adresse", "logo_path", "created_at") VALUES (2, 'Cabinet Expertise Comptable', 'contact@expertise-cpt.ma', '+212 5 24 12 34 56', '123 Avenue Hassan II, Casablanca', NULL, '2026-05-06 12:03:58') ON CONFLICT DO NOTHING;
INSERT INTO "cabinets" ("id", "nom", "email", "telephone", "adresse", "logo_path", "created_at") VALUES (3, 'Finances & Audit Maroc', 'info@finances-audit.ma', '+212 5 37 77 88 99', '45 Rue de Fès, Rabat', NULL, '2026-05-06 12:03:58') ON CONFLICT DO NOTHING;

-- === agents (depuis SQLite:agents, 4 lignes) ===
DELETE FROM "agents";
INSERT INTO "agents" ("id", "cabinet_id", "username", "email", "password_hash", "nom", "prenom", "is_active", "is_admin", "is_super_admin", "created_at", "updated_at") VALUES (1, 2, 'wissal', 'wissal@expertise-cpt.ma', '6e7dc04babbd98b9f4952084a4493ee2fc16d360df95c4594d91df694dc73a79$4f52f2448bb46593bf5fb62111fa7c07ccd9e62d7af6c0853c14800db9a88549', 'Bennani', 'Wissal', TRUE, FALSE, TRUE, '2026-05-06 12:03:59', '2026-05-06 12:03:59') ON CONFLICT DO NOTHING;
INSERT INTO "agents" ("id", "cabinet_id", "username", "email", "password_hash", "nom", "prenom", "is_active", "is_admin", "is_super_admin", "created_at", "updated_at") VALUES (2, 2, 'fatima', 'fatima@expertise-cpt.ma', '66c5ab48caf1bf7a1036e541046d4957c446ab28b7809a93448d726ac8677bc8$11e10d3fd1df2d37fce845dabc76aed0ec400057474dc643bfe5a7a220a5a8d8', 'El Oujdi', 'Fatima', TRUE, FALSE, FALSE, '2026-05-06 12:03:59', '2026-05-06 12:03:59') ON CONFLICT DO NOTHING;
INSERT INTO "agents" ("id", "cabinet_id", "username", "email", "password_hash", "nom", "prenom", "is_active", "is_admin", "is_super_admin", "created_at", "updated_at") VALUES (3, 3, 'ahmed', 'ahmed@finances-audit.ma', '5f1d9ec2c0e4e979d9186b5e8ee759cc3c9e4e4105ee50c2953c96351396e34e$0d64af04ca3d4a10b5ef55c4272447098099bd3d943432fa161db0ce9dd19eda', 'Ahmed', 'Kabil', TRUE, TRUE, FALSE, '2026-05-06 12:03:59', '2026-05-06 12:03:59') ON CONFLICT DO NOTHING;
INSERT INTO "agents" ("id", "cabinet_id", "username", "email", "password_hash", "nom", "prenom", "is_active", "is_admin", "is_super_admin", "created_at", "updated_at") VALUES (4, 2, 'fati', 'fati@expertise-cpt.ma', 'e8914c9c05eba70a5e514b611f21a057c8b0e243123c1a3ed7e569fd64b56901$ba6e6c3b455811bedbdd915e790fa70ace0fd05bcef5efee6090306df9487d63', 'Utilisateur', 'Fati', TRUE, TRUE, FALSE, '2026-05-06 12:09:30', '2026-05-06 12:09:30') ON CONFLICT DO NOTHING;

-- === societes (depuis SQLite:societes, 5 lignes) ===
DELETE FROM "societes";
INSERT INTO "societes" ("id", "cabinet_id", "raison_sociale", "ice", "if_fiscal", "rc", "patente", "adresse", "cnss", "logo_path", "created_at", "updated_at") VALUES (1, 1, 'Ma Societe Test', '123456789012345', NULL, NULL, NULL, NULL, NULL, NULL, '2026-02-24 09:37:57', '2026-02-24 09:37:57') ON CONFLICT DO NOTHING;
INSERT INTO "societes" ("id", "cabinet_id", "raison_sociale", "ice", "if_fiscal", "rc", "patente", "adresse", "cnss", "logo_path", "created_at", "updated_at") VALUES (2, 2, 'Ets. EL OUJDI & FILS', '001234567890001', '12345678', 'RC-12345', 'PAT-001', 'Quartier des Affaires, Casablanca', NULL, NULL, '2026-05-06 12:03:59', '2026-05-06 12:03:59') ON CONFLICT DO NOTHING;
INSERT INTO "societes" ("id", "cabinet_id", "raison_sociale", "ice", "if_fiscal", "rc", "patente", "adresse", "cnss", "logo_path", "created_at", "updated_at") VALUES (3, 2, 'COMPTOIRE ARRAHMA SARL', '002234567890002', '87654321', 'RC-54321', 'PAT-002', 'Zone Industrielle, Fès', NULL, NULL, '2026-05-06 12:03:59', '2026-05-06 12:03:59') ON CONFLICT DO NOTHING;
INSERT INTO "societes" ("id", "cabinet_id", "raison_sociale", "ice", "if_fiscal", "rc", "patente", "adresse", "cnss", "logo_path", "created_at", "updated_at") VALUES (4, 3, 'Entreprise Import-Export', '003234567890003', '11111111', 'RC-99999', 'PAT-003', 'Port de Casablanca', NULL, NULL, '2026-05-06 12:03:59', '2026-05-06 12:03:59') ON CONFLICT DO NOTHING;
INSERT INTO "societes" ("id", "cabinet_id", "raison_sociale", "ice", "if_fiscal", "rc", "patente", "adresse", "cnss", "logo_path", "created_at", "updated_at") VALUES (5, 2, 'Entreprise de Test SARL', '001234567890001', NULL, NULL, NULL, NULL, NULL, NULL, '2026-05-06 12:09:30', '2026-05-06 12:09:30') ON CONFLICT DO NOTHING;

-- === agents_societes (depuis SQLite:agents_societes, 5 lignes) ===
DELETE FROM "agents_societes";
INSERT INTO "agents_societes" ("agent_id", "societe_id") VALUES (3, 4) ON CONFLICT DO NOTHING;
INSERT INTO "agents_societes" ("agent_id", "societe_id") VALUES (1, 2) ON CONFLICT DO NOTHING;
INSERT INTO "agents_societes" ("agent_id", "societe_id") VALUES (1, 3) ON CONFLICT DO NOTHING;
INSERT INTO "agents_societes" ("agent_id", "societe_id") VALUES (2, 2) ON CONFLICT DO NOTHING;
INSERT INTO "agents_societes" ("agent_id", "societe_id") VALUES (4, 5) ON CONFLICT DO NOTHING;

-- === comptes_pcm (depuis SQLite:comptes_pcm, 192 lignes) ===
DELETE FROM "comptes_pcm";
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('1111', 'Capital social', 1, '11', 'PASSIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('1181', 'Résultat net en instance d''affectation', 1, '11', 'PASSIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('1411', 'Emprunts obligataires', 1, '14', 'PASSIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('1481', 'Emprunts auprès des établissements de crédit', 1, '14', 'PASSIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2210', 'Terrains nus', 2, '22', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2321', 'Bâtiments', 2, '23', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2340', 'Matériel de transport', 2, '23', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2350', 'Matériel de bureau et mobilier', 2, '23', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2351', 'Mobilier de bureau', 2, '23', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2352', 'Matériel de bureau', 2, '23', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2355', 'Matériel informatique', 2, '23', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2360', 'Agencements et installations', 2, '23', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2400', 'Immobilisations incorporelles', 2, '24', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2823', 'Amortissements des bâtiments', 2, '28', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2834', 'Amortissements du matériel de transport', 2, '28', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2835', 'Amortissements du matériel de bureau, mobilier et améng', 2, '28', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('28351', 'Amortissements du mobilier de bureau', 2, '28', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('28352', 'Amortissements du matériel de bureau', 2, '28', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('28355', 'Amortissements du matériel informatique', 2, '28', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('3111', 'Marchandises', 3, '31', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('3121', 'Matières premières', 3, '31', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('3421', 'Clients', 3, '34', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('3441', 'Personnel — débiteur', 3, '34', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('3451', 'Subventions à recevoir', 3, '34', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('34551', 'TVA récupérable sur charges', 3, '345', 'TIERS', TRUE, 'RECUPERABLE') ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('34552', 'TVA récupérable sur immobilisations', 3, '345', 'TIERS', TRUE, 'IMMOBILISATION') ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('3456', 'Etat - Crédit de TVA', 3, '34', 'TIERS', TRUE, 'RECUPERABLE') ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4411', 'Fournisseurs', 4, '44', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4417', 'Fournisseurs - Retenues de garantie', 4, '44', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4441', 'Personnel - Oppositions', 4, '44', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4451', 'État — TVA facturée', 4, '44', 'TIERS', TRUE, 'COLLECTEE') ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4455', 'TVA facturée', 4, '44', 'TIERS', TRUE, 'COLLECTEE') ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4456', 'Etat - TVA due', 4, '44', 'TIERS', TRUE, 'COLLECTEE') ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4481', 'Dettes sur acquisitions d''immobilisations', 4, '44', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('5141', 'Banques (soldes débiteurs)', 5, '51', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('5161', 'Caisse (solde débiteur)', 5, '51', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6111', 'Achats de marchandises (groupe A)', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6121', 'Achats de matières premières', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6123', 'Achats d''emballages', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6124', 'Achats de fournitures non stockables (eau, électricité)', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6125', 'Achats de fournitures d''entretien', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6131', 'Locations et charges locatives', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6132', 'Redevances de crédit-bail (leasing)', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6133', 'Entretien et réparations', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6135', 'Rémunérations d''intermédiaires et honoraires', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6141', 'Etudes, recherches et documentation', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6142', 'Transports (personnel, marchandises)', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6143', 'Déplacements, missions et réceptions', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6144', 'Publicité, publications et relations publiques', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6145', 'Frais postaux et frais de télécommunications', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6146', 'Cotisations et dons', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6147', 'Services bancaires', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6148', 'Autres charges externes des exercices précédents', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6152', 'Honoraires', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6161', 'Impôts, taxes et droits d''enregistrement', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6171', 'Appointements et salaires', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6174', 'Charges sociales', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6181', 'Jetons de présence', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6193', 'D.E.A des immobilisations corporelles', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6300', 'Impôts sur les résultats', 6, '63', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7111', 'Ventes de marchandises au Maroc', 7, '71', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7121', 'Ventes de produits finis', 7, '71', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7122', 'Ventes de produits intermédiaires', 7, '71', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7124', 'Ventes de services produits au Maroc', 7, '71', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7161', 'Subventions d''exploitation', 7, '71', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7181', 'Jetons de présence reçus', 7, '71', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7300', 'Produits financiers', 7, '73', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7500', 'Produits non courants', 7, '75', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('8100', 'Résultat d''exploitation', 8, '81', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('8200', 'Résultat financier', 8, '82', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('8800', 'Résultat net de l''exercice', 8, '88', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('1117', 'Capital appelé non versé', 1, '11', 'PASSIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('1119', 'Actionnaires capital souscrit - non appelé', 1, '11', 'PASSIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('1121', 'Primes d''émission', 1, '11', 'PASSIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('1131', 'Réserve légale', 1, '11', 'PASSIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('1140', 'Réserves statutaires ou contractuelles', 1, '11', 'PASSIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('1151', 'Réserves facultatives', 1, '11', 'PASSIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('1161', 'Report à nouveau (solde créditeur)', 1, '11', 'PASSIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('1169', 'Report à nouveau (solde débiteur)', 1, '11', 'PASSIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('1191', 'Résultat net de l''exercice (créditeur)', 1, '11', 'PASSIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('1199', 'Résultat net de l''exercice (débiteur)', 1, '11', 'PASSIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('1311', 'Subventions d''investissement reçues', 1, '13', 'PASSIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('1482', 'Avances de l''Etat', 1, '14', 'PASSIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('1486', 'Fournisseurs d''immobilisations (comptes de financement)', 1, '14', 'PASSIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('1511', 'Provisions pour litiges', 1, '15', 'PASSIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('1512', 'Provisions pour garanties données aux clients', 1, '15', 'PASSIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('1555', 'Provisions pour impôts', 1, '15', 'PASSIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2111', 'Frais de constitution', 2, '21', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2113', 'Frais d''augmentation de capital', 2, '21', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2220', 'Terrains aménagés', 2, '22', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2230', 'Terrains bâtis', 2, '22', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2311', 'Terrains', 2, '23', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2331', 'Installations techniques', 2, '23', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2332', 'Matériel et outillage', 2, '23', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2356', 'Agencements, installations et aménagements divers', 2, '23', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2358', 'Autres matériels, mobiliers et agencements', 2, '23', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2380', 'Immobilisations corporelles en cours', 2, '23', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2411', 'Titres de participation', 2, '24', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2481', 'Prêts au personnel', 2, '24', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2483', 'Dépôts et cautionnements versés', 2, '24', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2486', 'Créances immobilisées', 2, '24', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2510', 'Titres de participation', 2, '25', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2710', 'Frais d''acquisition des immobilisations', 2, '27', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2811', 'Amortissements des frais de constitution', 2, '28', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2832', 'Amortissements des bâtiments', 2, '28', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('2833', 'Amortissements du matériel et outillage', 2, '28', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('3122', 'Matières et fournitures consommables', 3, '31', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('3123', 'Emballages', 3, '31', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('3131', 'Produits en cours', 3, '31', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('3151', 'Produits finis', 3, '31', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('3411', 'Fournisseurs débiteurs (avances et acomptes)', 3, '34', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('3424', 'Clients - Créances douteuses ou litigieuses', 3, '34', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('3425', 'Clients - Effets à recevoir', 3, '34', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('3427', 'Clients - Factures à établir', 3, '34', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('3431', 'Avances et acomptes au personnel', 3, '34', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('3453', 'Acomptes sur impôts sur les résultats', 3, '34', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('3458', 'Etat - Autres comptes débiteurs', 3, '34', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('3461', 'Associés - Comptes courants débiteurs', 3, '34', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('3481', 'Créances sur cessions d''immobilisations', 3, '34', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('3482', 'Créances sur cessions de titres et valeurs de placement', 3, '34', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('3487', 'Débiteurs divers', 3, '34', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('3491', 'Charges constatées d''avance', 3, '34', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('3500', 'Titres et valeurs de placement', 3, '35', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4413', 'Fournisseurs - Effets à payer', 4, '44', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4415', 'Fournisseurs d''immobilisations', 4, '44', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4418', 'Fournisseurs - Factures non parvenues', 4, '44', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4421', 'Clients créditeurs (avances et acomptes reçus)', 4, '44', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4432', 'Rémunérations dues au personnel', 4, '44', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4433', 'Dépôts du personnel créditeurs', 4, '44', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4434', 'Oppositions sur salaires', 4, '44', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4443', 'CNSS', 4, '44', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4445', 'Mutuelles', 4, '44', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4447', 'AMO', 4, '44', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4448', 'Autres organismes sociaux', 4, '44', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4452', 'Etat - Impôts sur les résultats', 4, '44', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4453', 'Etat - Impôts retenus à la source (IR)', 4, '44', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4457', 'Etat - Autres impôts et taxes', 4, '44', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4458', 'Etat - Comptes créditeurs', 4, '44', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4461', 'Associés - Comptes courants créditeurs', 4, '44', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4463', 'Comptes bloqués des associés', 4, '44', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4465', 'Associés - Dividendes à payer', 4, '44', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4483', 'Dettes sur acquisitions de titres et valeurs de placement', 4, '44', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4487', 'Créditeurs divers', 4, '44', 'TIERS', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('4491', 'Produits constatés d''avance', 4, '44', 'PASSIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('5111', 'Chèques à encaisser ou à l''encaissement', 5, '51', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('5113', 'Effets à encaisser ou à l''encaissement', 5, '51', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('5115', 'Virements à l''encaissement', 5, '51', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('5146', 'CCP (soldes débiteurs)', 5, '51', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('5541', 'Banques (soldes créditeurs)', 5, '55', 'PASSIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('5900', 'Virements internes', 5, '59', 'ACTIF', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6112', 'Achats de marchandises (groupe B)', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6114', 'Variations de stocks de marchandises', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6118', 'Achats de marchandises des exercices précédents', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6119', 'R.R.R obtenus sur achats de marchandises', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6122', 'Achats de matières et fournitures consommables', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6126', 'Achats de fournitures de bureau', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6128', 'Achats de matières et fournitures des exercices précédents', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6129', 'R.R.R obtenus sur achats de matières et fournitures', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6134', 'Primes d''assurances', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6136', 'Frais d''actes et de contentieux', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6149', 'R.R.R obtenus sur autres charges externes', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6151', 'Impôts et taxes directs', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6155', 'Taxes sur le chiffre d''affaires', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6167', 'Taxes sur les véhicules', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6176', 'Prévoyance sociale', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6177', 'Autres charges sociales', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6191', 'D.E.A des frais de constitution', 6, '61', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6311', 'Intérêts des emprunts et dettes', 6, '63', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6331', 'Pertes de change', 6, '63', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6385', 'Charges nettes sur cessions de titres', 6, '63', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6513', 'Valeurs nettes d''amortissements des immo corporelles cédées', 6, '65', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6581', 'Pénalités et amendes', 6, '65', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('6701', 'Impôts sur les résultats', 6, '67', 'CHARGE', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7113', 'Vente de marchandises à l''étranger', 7, '71', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7118', 'Ventes de marchandises des exercices précédents', 7, '71', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7119', 'R.R.R accordés par l''entreprise', 7, '71', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7125', 'Ventes de services produits à l''étranger', 7, '71', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7126', 'Redevances pour brevets, marques, droits et valeurs', 7, '71', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7127', 'Ventes de produits résiduels', 7, '71', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7128', 'Ventes de produits et services des exercices précédents', 7, '71', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7129', 'R.R.R accordés sur ventes de produits', 7, '71', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7131', 'Variations des stocks de produits en cours', 7, '71', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7132', 'Variations des stocks de produits finis', 7, '71', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7140', 'Immobilisations produites par l''entreprise pour elle-même', 7, '71', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7182', 'Revenus des immeubles non destinés à l''exploitation', 7, '71', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7191', 'Reprises sur amortissements de l''actif immobilisé', 7, '71', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7311', 'Produits des titres de participation', 7, '73', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7331', 'Gains de change', 7, '73', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7381', 'Intérêts et produits assimilés', 7, '73', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7510', 'Produits des cessions d''immobilisations', 7, '75', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7561', 'Libéralités reçues', 7, '75', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;
INSERT INTO "comptes_pcm" ("code", "label", "pcm_class", "group_code", "account_type", "is_tva_account", "tva_type") VALUES ('7581', 'Indemnités d''assurances reçues', 7, '75', 'PRODUIT', FALSE, NULL) ON CONFLICT DO NOTHING;

-- === journaux_comptables (depuis SQLite:journaux_comptables, 6 lignes) ===
DELETE FROM "journaux_comptables";
INSERT INTO "journaux_comptables" ("id", "societe_id", "code", "label", "type", "created_at", "updated_at") VALUES (1, 1, 'ACH', 'Journal des Achats', 'ACHAT', '2026-03-25 13:42:03', '2026-03-25 13:42:03') ON CONFLICT DO NOTHING;
INSERT INTO "journaux_comptables" ("id", "societe_id", "code", "label", "type", "created_at", "updated_at") VALUES (2, 1, 'VTE', 'Journal des Ventes', 'VENTE', '2026-03-25 13:42:03', '2026-03-25 13:42:03') ON CONFLICT DO NOTHING;
INSERT INTO "journaux_comptables" ("id", "societe_id", "code", "label", "type", "created_at", "updated_at") VALUES (3, 1, 'OD', 'Opérations Diverses', 'OD', '2026-03-25 13:42:03', '2026-03-25 13:42:03') ON CONFLICT DO NOTHING;
INSERT INTO "journaux_comptables" ("id", "societe_id", "code", "label", "type", "created_at", "updated_at") VALUES (4, 1, 'BQ', 'Banque Général', 'BANQUE', '2026-03-25 13:42:03', '2026-03-25 13:42:03') ON CONFLICT DO NOTHING;
INSERT INTO "journaux_comptables" ("id", "societe_id", "code", "label", "type", "created_at", "updated_at") VALUES (5, 1, 'IMMO', 'Journal des Immobilisations', 'OD', '2026-03-25 13:42:03', '2026-03-25 13:42:03') ON CONFLICT DO NOTHING;
INSERT INTO "journaux_comptables" ("id", "societe_id", "code", "label", "type", "created_at", "updated_at") VALUES (6, 1, 'PAYE', 'Journal de Paie', 'PAIE', '2026-03-25 13:42:03', '2026-03-25 13:42:03') ON CONFLICT DO NOTHING;

-- === compteurs_facturation (depuis SQLite:compteurs_facturation, 3 lignes) ===
DELETE FROM "compteurs_facturation";
INSERT INTO "compteurs_facturation" ("id", "societe_id", "annee", "dernier_numero", "created_at", "updated_at") VALUES (1, 2, 2026, 0, '2026-05-06 12:03:59', '2026-05-06 12:03:59') ON CONFLICT DO NOTHING;
INSERT INTO "compteurs_facturation" ("id", "societe_id", "annee", "dernier_numero", "created_at", "updated_at") VALUES (2, 3, 2026, 0, '2026-05-06 12:03:59', '2026-05-06 12:03:59') ON CONFLICT DO NOTHING;
INSERT INTO "compteurs_facturation" ("id", "societe_id", "annee", "dernier_numero", "created_at", "updated_at") VALUES (3, 4, 2026, 0, '2026-05-06 12:03:59', '2026-05-06 12:03:59') ON CONFLICT DO NOTHING;

-- === factures (depuis SQLite:factures, 3 lignes) ===
DELETE FROM "factures";
INSERT INTO "factures" ("id", "societe_id", "numero_facture", "date_facture", "due_date", "invoice_type", "supplier_name", "supplier_ice", "supplier_if", "supplier_rc", "supplier_address", "client_name", "client_ice", "client_if", "client_address", "montant_ht", "montant_tva", "montant_ttc", "taux_tva", "devise", "payment_mode", "payment_terms", "ocr_confidence", "extraction_source", "dgi_flags", "status", "validated_by", "validated_at", "reject_reason", "file_path", "file_hash", "fournisseur", "operation_type", "operation_confidence", "if_frs", "ice_frs", "designation", "id_paie", "date_paie", "created_at", "updated_at") VALUES (1, 1, 'FAC-001', '2026-02-24', NULL, NULL, 'Fournisseur Telecom', '999888777', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 120, NULL, 'MAD', NULL, NULL, NULL, NULL, NULL, 'VALIDATED', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2026-02-24 09:37:57', '2026-02-24 09:37:57') ON CONFLICT DO NOTHING;
INSERT INTO "factures" ("id", "societe_id", "numero_facture", "date_facture", "due_date", "invoice_type", "supplier_name", "supplier_ice", "supplier_if", "supplier_rc", "supplier_address", "client_name", "client_ice", "client_if", "client_address", "montant_ht", "montant_tva", "montant_ttc", "taux_tva", "devise", "payment_mode", "payment_terms", "ocr_confidence", "extraction_source", "dgi_flags", "status", "validated_by", "validated_at", "reject_reason", "file_path", "file_hash", "fournisseur", "operation_type", "operation_confidence", "if_frs", "ice_frs", "designation", "id_paie", "date_paie", "created_at", "updated_at") VALUES (2, 1, NULL, NULL, NULL, NULL, 'Fournisseur Telecom (Bis)', '999888777', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'MAD', NULL, NULL, NULL, NULL, NULL, 'EXTRACTED', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2026-02-24 09:37:57', NULL) ON CONFLICT DO NOTHING;
INSERT INTO "factures" ("id", "societe_id", "numero_facture", "date_facture", "due_date", "invoice_type", "supplier_name", "supplier_ice", "supplier_if", "supplier_rc", "supplier_address", "client_name", "client_ice", "client_if", "client_address", "montant_ht", "montant_tva", "montant_ttc", "taux_tva", "devise", "payment_mode", "payment_terms", "ocr_confidence", "extraction_source", "dgi_flags", "status", "validated_by", "validated_at", "reject_reason", "file_path", "file_hash", "fournisseur", "operation_type", "operation_confidence", "if_frs", "ice_frs", "designation", "id_paie", "date_paie", "created_at", "updated_at") VALUES (3, 1, NULL, '2026-01-01', NULL, NULL, NULL, '123456789012345', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1200.5, NULL, 'MAD', NULL, NULL, NULL, NULL, NULL, 'EXTRACTED', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2026-02-24 12:28:37', NULL) ON CONFLICT DO NOTHING;

-- === lignes_factures (depuis SQLite:invoice_lines, 2 lignes) ===
DELETE FROM "lignes_factures";
INSERT INTO "lignes_factures" ("id", "facture_id", "description", "quantity", "tva_rate", "created_at") VALUES (1, 1, 'Abonnement Internet', NULL, NULL, '2026-02-24 09:37:57') ON CONFLICT DO NOTHING;
INSERT INTO "lignes_factures" ("id", "facture_id", "description", "quantity", "tva_rate", "created_at") VALUES (2, 2, 'Consommation Mobile', NULL, NULL, '2026-02-24 09:37:57') ON CONFLICT DO NOTHING;

-- === ecritures_journal (depuis SQLite:ecritures_journal, 1 lignes) ===
DELETE FROM "ecritures_journal";
INSERT INTO "ecritures_journal" ("id", "societe_id", "facture_id", "journal_code", "entry_date", "reference", "description", "is_validated", "validated_by", "validated_at", "total_debit", "total_credit", "created_at") VALUES (1, 1, NULL, 'OD', '2024-03-28', 'PAIE-1-03/2024', 'Bulletin de paie 03/2024 — Driss EL OMARI', FALSE, NULL, NULL, 7654.35, 7654.35, '2026-03-03 12:44:43') ON CONFLICT DO NOTHING;

-- === lignes_ecritures (depuis SQLite:lignes_ecritures, 8 lignes) ===
DELETE FROM "lignes_ecritures";
INSERT INTO "lignes_ecritures" ("id", "ecriture_journal_id", "line_order", "account_code", "account_label", "debit", "credit", "tiers_name", "tiers_ice", "created_at") VALUES (1, 1, 1, '6171', 'Rémunérations du personnel', 6750, 0, NULL, NULL, '2026-03-03 12:44:43') ON CONFLICT DO NOTHING;
INSERT INTO "lignes_ecritures" ("id", "ecriture_journal_id", "line_order", "account_code", "account_label", "debit", "credit", "tiers_name", "tiers_ice", "created_at") VALUES (2, 1, 2, '6174', 'Charges sociales patronales (CNSS+AMO)', 904.35, 0, NULL, NULL, '2026-03-03 12:44:43') ON CONFLICT DO NOTHING;
INSERT INTO "lignes_ecritures" ("id", "ecriture_journal_id", "line_order", "account_code", "account_label", "debit", "credit", "tiers_name", "tiers_ice", "created_at") VALUES (3, 1, 3, '4441', 'Salaire net à payer — Driss EL OMARI', 0, 6059.59, 'Driss EL OMARI', NULL, '2026-03-03 12:44:43') ON CONFLICT DO NOTHING;
INSERT INTO "lignes_ecritures" ("id", "ecriture_journal_id", "line_order", "account_code", "account_label", "debit", "credit", "tiers_name", "tiers_ice", "created_at") VALUES (4, 1, 4, '4443', 'CNSS — part salarié', 0, 268.8, NULL, NULL, '2026-03-03 12:44:43') ON CONFLICT DO NOTHING;
INSERT INTO "lignes_ecritures" ("id", "ecriture_journal_id", "line_order", "account_code", "account_label", "debit", "credit", "tiers_name", "tiers_ice", "created_at") VALUES (5, 1, 5, '4443', 'CNSS — part patronale', 0, 638.4, NULL, NULL, '2026-03-03 12:44:43') ON CONFLICT DO NOTHING;
INSERT INTO "lignes_ecritures" ("id", "ecriture_journal_id", "line_order", "account_code", "account_label", "debit", "credit", "tiers_name", "tiers_ice", "created_at") VALUES (6, 1, 6, '4447', 'AMO — part salarié', 0, 152.55, NULL, NULL, '2026-03-03 12:44:43') ON CONFLICT DO NOTHING;
INSERT INTO "lignes_ecritures" ("id", "ecriture_journal_id", "line_order", "account_code", "account_label", "debit", "credit", "tiers_name", "tiers_ice", "created_at") VALUES (7, 1, 7, '4447', 'AMO — part patronale', 0, 265.95, NULL, NULL, '2026-03-03 12:44:43') ON CONFLICT DO NOTHING;
INSERT INTO "lignes_ecritures" ("id", "ecriture_journal_id", "line_order", "account_code", "account_label", "debit", "credit", "tiers_name", "tiers_ice", "created_at") VALUES (8, 1, 8, '4444', 'IR/IGR retenu à la source', 0, 269.06, NULL, NULL, '2026-03-03 12:44:43') ON CONFLICT DO NOTHING;

-- === employes (depuis SQLite:employes, 1 lignes) ===
DELETE FROM "employes";
INSERT INTO "employes" ("id", "societe_id", "nom", "prenom", "cin", "date_naissance", "poste", "date_embauche", "type_contrat", "salaire_base", "nb_enfants", "anciennete_pct", "numero_cnss", "affiliee_cnss", "statut", "created_at", "updated_at") VALUES (1, 1, 'EL OMARI', 'Driss', NULL, NULL, NULL, '2020-01-01', 'CDI', 5000, 2, 5, NULL, TRUE, 'ACTIF', '2026-03-03 12:33:57', '2026-03-03 12:33:57') ON CONFLICT DO NOTHING;

-- === bulletins_paie (depuis SQLite:bulletins_paie, 1 lignes) ===
DELETE FROM "bulletins_paie";
INSERT INTO "bulletins_paie" ("id", "employe_id", "mois", "annee", "salaire_base", "prime_anciennete", "autres_gains", "salaire_brut", "cnss_salarie", "amo_salarie", "ir_retenu", "total_retenues", "cnss_patronal", "amo_patronal", "total_patronal", "salaire_net", "cout_total_employeur", "journal_entry_id", "statut", "valide_par", "valide_at", "created_at") VALUES (1, 1, 3, 2024, 5000, 250, 1500, 6750, 268.8, 152.55, 269.06, 690.41, 638.4, 265.95, 904.35, 6059.59, 7654.35, 1, 'VALIDE', NULL, NULL, '2026-03-03 12:44:43') ON CONFLICT DO NOTHING;

-- === lignes_paie (depuis SQLite:lignes_paie, 7 lignes) ===
DELETE FROM "lignes_paie";
INSERT INTO "lignes_paie" ("id", "bulletin_id", "libelle", "type_ligne", "montant", "taux", "base_calcul", "ordre") VALUES (1, 1, 'Salaire de base', 'GAIN', 5000, NULL, NULL, 1) ON CONFLICT DO NOTHING;
INSERT INTO "lignes_paie" ("id", "bulletin_id", "libelle", "type_ligne", "montant", "taux", "base_calcul", "ordre") VALUES (2, 1, 'Prime d''ancienneté', 'GAIN', 250, 0.05, NULL, 2) ON CONFLICT DO NOTHING;
INSERT INTO "lignes_paie" ("id", "bulletin_id", "libelle", "type_ligne", "montant", "taux", "base_calcul", "ordre") VALUES (3, 1, 'Primes/Avantages', 'GAIN', 1000, NULL, NULL, 3) ON CONFLICT DO NOTHING;
INSERT INTO "lignes_paie" ("id", "bulletin_id", "libelle", "type_ligne", "montant", "taux", "base_calcul", "ordre") VALUES (4, 1, 'Heures supplémentaires', 'GAIN', 500, NULL, NULL, 4) ON CONFLICT DO NOTHING;
INSERT INTO "lignes_paie" ("id", "bulletin_id", "libelle", "type_ligne", "montant", "taux", "base_calcul", "ordre") VALUES (5, 1, 'CNSS salarié (4.48%)', 'RETENUE', 268.8, 0.0448, 6000, 10) ON CONFLICT DO NOTHING;
INSERT INTO "lignes_paie" ("id", "bulletin_id", "libelle", "type_ligne", "montant", "taux", "base_calcul", "ordre") VALUES (6, 1, 'AMO salarié (2.26%)', 'RETENUE', 152.55, 0.0226, 6750, 11) ON CONFLICT DO NOTHING;
INSERT INTO "lignes_paie" ("id", "bulletin_id", "libelle", "type_ligne", "montant", "taux", "base_calcul", "ordre") VALUES (7, 1, 'IR/IGR retenu', 'RETENUE', 269.06, NULL, NULL, 12) ON CONFLICT DO NOTHING;

-- === mappings_fournisseurs (depuis SQLite:supplier_mappings, 1 lignes) ===
DELETE FROM "mappings_fournisseurs";
INSERT INTO "mappings_fournisseurs" ("id", "cabinet_id", "supplier_ice", "pcm_account_code", "created_at", "updated_at") VALUES (1, 1, '999888777', '6144', '2026-02-24 09:37:57', '2026-02-24 09:37:57') ON CONFLICT DO NOTHING;

-- === Resynchronisation sequences ===
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'cabinets') THEN
    PERFORM setval(pg_get_serial_sequence('cabinets', 'id'),
      COALESCE((SELECT MAX(id) FROM "cabinets"), 1));
  END IF;
END $$;
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'agents') THEN
    PERFORM setval(pg_get_serial_sequence('agents', 'id'),
      COALESCE((SELECT MAX(id) FROM "agents"), 1));
  END IF;
END $$;
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'societes') THEN
    PERFORM setval(pg_get_serial_sequence('societes', 'id'),
      COALESCE((SELECT MAX(id) FROM "societes"), 1));
  END IF;
END $$;
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'factures') THEN
    PERFORM setval(pg_get_serial_sequence('factures', 'id'),
      COALESCE((SELECT MAX(id) FROM "factures"), 1));
  END IF;
END $$;
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'journaux_comptables') THEN
    PERFORM setval(pg_get_serial_sequence('journaux_comptables', 'id'),
      COALESCE((SELECT MAX(id) FROM "journaux_comptables"), 1));
  END IF;
END $$;
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'compteurs_facturation') THEN
    PERFORM setval(pg_get_serial_sequence('compteurs_facturation', 'id'),
      COALESCE((SELECT MAX(id) FROM "compteurs_facturation"), 1));
  END IF;
END $$;
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ecritures_journal') THEN
    PERFORM setval(pg_get_serial_sequence('ecritures_journal', 'id'),
      COALESCE((SELECT MAX(id) FROM "ecritures_journal"), 1));
  END IF;
END $$;
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'lignes_ecritures') THEN
    PERFORM setval(pg_get_serial_sequence('lignes_ecritures', 'id'),
      COALESCE((SELECT MAX(id) FROM "lignes_ecritures"), 1));
  END IF;
END $$;
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'employes') THEN
    PERFORM setval(pg_get_serial_sequence('employes', 'id'),
      COALESCE((SELECT MAX(id) FROM "employes"), 1));
  END IF;
END $$;
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'bulletins_paie') THEN
    PERFORM setval(pg_get_serial_sequence('bulletins_paie', 'id'),
      COALESCE((SELECT MAX(id) FROM "bulletins_paie"), 1));
  END IF;
END $$;
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'lignes_paie') THEN
    PERFORM setval(pg_get_serial_sequence('lignes_paie', 'id'),
      COALESCE((SELECT MAX(id) FROM "lignes_paie"), 1));
  END IF;
END $$;
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'supplier_mappings') THEN
    PERFORM setval(pg_get_serial_sequence('supplier_mappings', 'id'),
      COALESCE((SELECT MAX(id) FROM "supplier_mappings"), 1));
  END IF;
END $$;

SET session_replication_role = DEFAULT;
-- TOTAL: 242 lignes dans 15 tables
SELECT 'RESTAURATION TERMINEE' as statut;