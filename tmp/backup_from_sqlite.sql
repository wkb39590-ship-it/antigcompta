BEGIN TRANSACTION;
CREATE TABLE action_logs (
	id INTEGER NOT NULL, 
	cabinet_id INTEGER, 
	agent_id INTEGER, 
	action_type VARCHAR(50) NOT NULL, 
	entity_type VARCHAR(50) NOT NULL, 
	entity_id INTEGER, 
	details TEXT, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(cabinet_id) REFERENCES cabinets (id) ON DELETE CASCADE, 
	FOREIGN KEY(agent_id) REFERENCES agents (id) ON DELETE SET NULL
);
CREATE TABLE agent_societes (
	agent_id INTEGER NOT NULL, 
	societe_id INTEGER NOT NULL, 
	PRIMARY KEY (agent_id, societe_id), 
	FOREIGN KEY(agent_id) REFERENCES agents (id) ON DELETE CASCADE, 
	FOREIGN KEY(societe_id) REFERENCES societes (id) ON DELETE CASCADE
);
CREATE TABLE agents (
	id INTEGER NOT NULL, 
	cabinet_id INTEGER NOT NULL, 
	username VARCHAR(100) NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	password_hash VARCHAR(500) NOT NULL, 
	nom VARCHAR(255), 
	prenom VARCHAR(255), 
	is_active BOOLEAN, 
	is_admin BOOLEAN, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, is_super_admin BOOLEAN DEFAULT 0, 
	PRIMARY KEY (id), 
	FOREIGN KEY(cabinet_id) REFERENCES cabinets (id), 
	UNIQUE (username), 
	UNIQUE (email)
);
INSERT INTO "agents" VALUES(1,2,'wissal','wissal@expertise-cpt.ma','6e7dc04babbd98b9f4952084a4493ee2fc16d360df95c4594d91df694dc73a79$4f52f2448bb46593bf5fb62111fa7c07ccd9e62d7af6c0853c14800db9a88549','Bennani','Wissal',1,0,'2026-05-06 12:03:59','2026-05-06 12:03:59',1);
INSERT INTO "agents" VALUES(2,2,'fatima','fatima@expertise-cpt.ma','66c5ab48caf1bf7a1036e541046d4957c446ab28b7809a93448d726ac8677bc8$11e10d3fd1df2d37fce845dabc76aed0ec400057474dc643bfe5a7a220a5a8d8','El Oujdi','Fatima',1,0,'2026-05-06 12:03:59','2026-05-06 12:03:59',0);
INSERT INTO "agents" VALUES(3,3,'ahmed','ahmed@finances-audit.ma','5f1d9ec2c0e4e979d9186b5e8ee759cc3c9e4e4105ee50c2953c96351396e34e$0d64af04ca3d4a10b5ef55c4272447098099bd3d943432fa161db0ce9dd19eda','Ahmed','Kabil',1,1,'2026-05-06 12:03:59','2026-05-06 12:03:59',0);
INSERT INTO "agents" VALUES(4,2,'fati','fati@expertise-cpt.ma','e8914c9c05eba70a5e514b611f21a057c8b0e243123c1a3ed7e569fd64b56901$ba6e6c3b455811bedbdd915e790fa70ace0fd05bcef5efee6090306df9487d63','Utilisateur','Fati',1,1,'2026-05-06 12:09:30','2026-05-06 12:09:30',0);
CREATE TABLE agents_societes (
	agent_id INTEGER NOT NULL, 
	societe_id INTEGER NOT NULL, 
	PRIMARY KEY (agent_id, societe_id), 
	FOREIGN KEY(agent_id) REFERENCES agents (id) ON DELETE CASCADE, 
	FOREIGN KEY(societe_id) REFERENCES societes (id) ON DELETE CASCADE
);
INSERT INTO "agents_societes" VALUES(3,4);
INSERT INTO "agents_societes" VALUES(1,2);
INSERT INTO "agents_societes" VALUES(1,3);
INSERT INTO "agents_societes" VALUES(2,2);
INSERT INTO "agents_societes" VALUES(4,5);
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
INSERT INTO "alembic_version" VALUES('e913ba9622fc');
CREATE TABLE bulletins_paie (
	id INTEGER NOT NULL, 
	employe_id INTEGER NOT NULL, 
	mois INTEGER NOT NULL, 
	annee INTEGER NOT NULL, 
	salaire_base NUMERIC(12, 2) NOT NULL, 
	prime_anciennete NUMERIC(12, 2), 
	autres_gains NUMERIC(12, 2), 
	salaire_brut NUMERIC(12, 2) NOT NULL, 
	cnss_salarie NUMERIC(10, 2) NOT NULL, 
	amo_salarie NUMERIC(10, 2) NOT NULL, 
	ir_retenu NUMERIC(10, 2) NOT NULL, 
	total_retenues NUMERIC(10, 2) NOT NULL, 
	cnss_patronal NUMERIC(10, 2) NOT NULL, 
	amo_patronal NUMERIC(10, 2) NOT NULL, 
	total_patronal NUMERIC(10, 2) NOT NULL, 
	salaire_net NUMERIC(12, 2) NOT NULL, 
	cout_total_employeur NUMERIC(12, 2), 
	journal_entry_id INTEGER, 
	statut VARCHAR(20) DEFAULT 'BROUILLON' NOT NULL, 
	valide_par VARCHAR(100), 
	valide_at DATETIME, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(employe_id) REFERENCES employes (id) ON DELETE CASCADE, 
	FOREIGN KEY(journal_entry_id) REFERENCES ecritures_journal (id)
);
INSERT INTO "bulletins_paie" VALUES(1,1,3,2024,5000,250,1500,6750,268.8,152.55,269.06,690.41,638.4,265.95,904.35,6059.59,7654.35,1,'VALIDE',NULL,NULL,'2026-03-03 12:44:43');
CREATE TABLE cabinets (
	id INTEGER NOT NULL, 
	nom VARCHAR(255) NOT NULL, 
	email VARCHAR(255), 
	telephone VARCHAR(20), 
	adresse VARCHAR(500), 
	logo_path VARCHAR(500), 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (nom)
);
INSERT INTO "cabinets" VALUES(1,'Cabinet Test',NULL,NULL,NULL,NULL,'2026-02-24 09:37:57');
INSERT INTO "cabinets" VALUES(2,'Cabinet Expertise Comptable','contact@expertise-cpt.ma','+212 5 24 12 34 56','123 Avenue Hassan II, Casablanca',NULL,'2026-05-06 12:03:58');
INSERT INTO "cabinets" VALUES(3,'Finances & Audit Maroc','info@finances-audit.ma','+212 5 37 77 88 99','45 Rue de Fès, Rabat',NULL,'2026-05-06 12:03:58');
CREATE TABLE comptes_pcm (
	code VARCHAR(10) NOT NULL, 
	label VARCHAR(255) NOT NULL, 
	pcm_class INTEGER NOT NULL, 
	group_code VARCHAR(10), 
	account_type VARCHAR(20), 
	is_tva_account BOOLEAN DEFAULT 'false' NOT NULL, 
	tva_type VARCHAR(30), 
	PRIMARY KEY (code)
);
INSERT INTO "comptes_pcm" VALUES('1111','Capital social',1,'11','PASSIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('1181','Résultat net en instance d''affectation',1,'11','PASSIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('1411','Emprunts obligataires',1,'14','PASSIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('1481','Emprunts auprès des établissements de crédit',1,'14','PASSIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2210','Terrains nus',2,'22','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2321','Bâtiments',2,'23','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2340','Matériel de transport',2,'23','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2350','Matériel de bureau et mobilier',2,'23','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2351','Mobilier de bureau',2,'23','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2352','Matériel de bureau',2,'23','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2355','Matériel informatique',2,'23','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2360','Agencements et installations',2,'23','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2400','Immobilisations incorporelles',2,'24','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2823','Amortissements des bâtiments',2,'28','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2834','Amortissements du matériel de transport',2,'28','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2835','Amortissements du matériel de bureau, mobilier et améng',2,'28','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('28351','Amortissements du mobilier de bureau',2,'28','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('28352','Amortissements du matériel de bureau',2,'28','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('28355','Amortissements du matériel informatique',2,'28','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('3111','Marchandises',3,'31','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('3121','Matières premières',3,'31','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('3421','Clients',3,'34','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('3441','Personnel — débiteur',3,'34','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('3451','Subventions à recevoir',3,'34','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('34551','TVA récupérable sur charges',3,'345','TIERS',1,'RECUPERABLE');
INSERT INTO "comptes_pcm" VALUES('34552','TVA récupérable sur immobilisations',3,'345','TIERS',1,'IMMOBILISATION');
INSERT INTO "comptes_pcm" VALUES('3456','Etat - Crédit de TVA',3,'34','TIERS',1,'RECUPERABLE');
INSERT INTO "comptes_pcm" VALUES('4411','Fournisseurs',4,'44','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('4417','Fournisseurs - Retenues de garantie',4,'44','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('4441','Personnel - Oppositions',4,'44','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('4451','État — TVA facturée',4,'44','TIERS',1,'COLLECTEE');
INSERT INTO "comptes_pcm" VALUES('4455','TVA facturée',4,'44','TIERS',1,'COLLECTEE');
INSERT INTO "comptes_pcm" VALUES('4456','Etat - TVA due',4,'44','TIERS',1,'COLLECTEE');
INSERT INTO "comptes_pcm" VALUES('4481','Dettes sur acquisitions d''immobilisations',4,'44','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('5141','Banques (soldes débiteurs)',5,'51','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('5161','Caisse (solde débiteur)',5,'51','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6111','Achats de marchandises (groupe A)',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6121','Achats de matières premières',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6123','Achats d''emballages',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6124','Achats de fournitures non stockables (eau, électricité)',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6125','Achats de fournitures d''entretien',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6131','Locations et charges locatives',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6132','Redevances de crédit-bail (leasing)',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6133','Entretien et réparations',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6135','Rémunérations d''intermédiaires et honoraires',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6141','Etudes, recherches et documentation',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6142','Transports (personnel, marchandises)',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6143','Déplacements, missions et réceptions',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6144','Publicité, publications et relations publiques',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6145','Frais postaux et frais de télécommunications',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6146','Cotisations et dons',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6147','Services bancaires',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6148','Autres charges externes des exercices précédents',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6152','Honoraires',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6161','Impôts, taxes et droits d''enregistrement',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6171','Appointements et salaires',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6174','Charges sociales',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6181','Jetons de présence',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6193','D.E.A des immobilisations corporelles',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6300','Impôts sur les résultats',6,'63','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7111','Ventes de marchandises au Maroc',7,'71','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7121','Ventes de produits finis',7,'71','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7122','Ventes de produits intermédiaires',7,'71','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7124','Ventes de services produits au Maroc',7,'71','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7161','Subventions d''exploitation',7,'71','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7181','Jetons de présence reçus',7,'71','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7300','Produits financiers',7,'73','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7500','Produits non courants',7,'75','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('8100','Résultat d''exploitation',8,'81','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('8200','Résultat financier',8,'82','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('8800','Résultat net de l''exercice',8,'88','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('1117','Capital appelé non versé',1,'11','PASSIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('1119','Actionnaires capital souscrit - non appelé',1,'11','PASSIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('1121','Primes d''émission',1,'11','PASSIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('1131','Réserve légale',1,'11','PASSIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('1140','Réserves statutaires ou contractuelles',1,'11','PASSIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('1151','Réserves facultatives',1,'11','PASSIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('1161','Report à nouveau (solde créditeur)',1,'11','PASSIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('1169','Report à nouveau (solde débiteur)',1,'11','PASSIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('1191','Résultat net de l''exercice (créditeur)',1,'11','PASSIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('1199','Résultat net de l''exercice (débiteur)',1,'11','PASSIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('1311','Subventions d''investissement reçues',1,'13','PASSIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('1482','Avances de l''Etat',1,'14','PASSIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('1486','Fournisseurs d''immobilisations (comptes de financement)',1,'14','PASSIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('1511','Provisions pour litiges',1,'15','PASSIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('1512','Provisions pour garanties données aux clients',1,'15','PASSIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('1555','Provisions pour impôts',1,'15','PASSIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2111','Frais de constitution',2,'21','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2113','Frais d''augmentation de capital',2,'21','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2220','Terrains aménagés',2,'22','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2230','Terrains bâtis',2,'22','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2311','Terrains',2,'23','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2331','Installations techniques',2,'23','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2332','Matériel et outillage',2,'23','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2356','Agencements, installations et aménagements divers',2,'23','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2358','Autres matériels, mobiliers et agencements',2,'23','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2380','Immobilisations corporelles en cours',2,'23','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2411','Titres de participation',2,'24','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2481','Prêts au personnel',2,'24','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2483','Dépôts et cautionnements versés',2,'24','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2486','Créances immobilisées',2,'24','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2510','Titres de participation',2,'25','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2710','Frais d''acquisition des immobilisations',2,'27','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2811','Amortissements des frais de constitution',2,'28','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2832','Amortissements des bâtiments',2,'28','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('2833','Amortissements du matériel et outillage',2,'28','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('3122','Matières et fournitures consommables',3,'31','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('3123','Emballages',3,'31','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('3131','Produits en cours',3,'31','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('3151','Produits finis',3,'31','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('3411','Fournisseurs débiteurs (avances et acomptes)',3,'34','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('3424','Clients - Créances douteuses ou litigieuses',3,'34','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('3425','Clients - Effets à recevoir',3,'34','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('3427','Clients - Factures à établir',3,'34','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('3431','Avances et acomptes au personnel',3,'34','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('3453','Acomptes sur impôts sur les résultats',3,'34','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('3458','Etat - Autres comptes débiteurs',3,'34','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('3461','Associés - Comptes courants débiteurs',3,'34','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('3481','Créances sur cessions d''immobilisations',3,'34','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('3482','Créances sur cessions de titres et valeurs de placement',3,'34','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('3487','Débiteurs divers',3,'34','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('3491','Charges constatées d''avance',3,'34','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('3500','Titres et valeurs de placement',3,'35','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('4413','Fournisseurs - Effets à payer',4,'44','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('4415','Fournisseurs d''immobilisations',4,'44','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('4418','Fournisseurs - Factures non parvenues',4,'44','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('4421','Clients créditeurs (avances et acomptes reçus)',4,'44','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('4432','Rémunérations dues au personnel',4,'44','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('4433','Dépôts du personnel créditeurs',4,'44','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('4434','Oppositions sur salaires',4,'44','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('4443','CNSS',4,'44','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('4445','Mutuelles',4,'44','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('4447','AMO',4,'44','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('4448','Autres organismes sociaux',4,'44','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('4452','Etat - Impôts sur les résultats',4,'44','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('4453','Etat - Impôts retenus à la source (IR)',4,'44','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('4457','Etat - Autres impôts et taxes',4,'44','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('4458','Etat - Comptes créditeurs',4,'44','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('4461','Associés - Comptes courants créditeurs',4,'44','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('4463','Comptes bloqués des associés',4,'44','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('4465','Associés - Dividendes à payer',4,'44','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('4483','Dettes sur acquisitions de titres et valeurs de placement',4,'44','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('4487','Créditeurs divers',4,'44','TIERS',0,NULL);
INSERT INTO "comptes_pcm" VALUES('4491','Produits constatés d''avance',4,'44','PASSIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('5111','Chèques à encaisser ou à l''encaissement',5,'51','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('5113','Effets à encaisser ou à l''encaissement',5,'51','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('5115','Virements à l''encaissement',5,'51','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('5146','CCP (soldes débiteurs)',5,'51','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('5541','Banques (soldes créditeurs)',5,'55','PASSIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('5900','Virements internes',5,'59','ACTIF',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6112','Achats de marchandises (groupe B)',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6114','Variations de stocks de marchandises',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6118','Achats de marchandises des exercices précédents',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6119','R.R.R obtenus sur achats de marchandises',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6122','Achats de matières et fournitures consommables',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6126','Achats de fournitures de bureau',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6128','Achats de matières et fournitures des exercices précédents',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6129','R.R.R obtenus sur achats de matières et fournitures',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6134','Primes d''assurances',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6136','Frais d''actes et de contentieux',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6149','R.R.R obtenus sur autres charges externes',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6151','Impôts et taxes directs',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6155','Taxes sur le chiffre d''affaires',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6167','Taxes sur les véhicules',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6176','Prévoyance sociale',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6177','Autres charges sociales',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6191','D.E.A des frais de constitution',6,'61','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6311','Intérêts des emprunts et dettes',6,'63','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6331','Pertes de change',6,'63','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6385','Charges nettes sur cessions de titres',6,'63','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6513','Valeurs nettes d''amortissements des immo corporelles cédées',6,'65','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6581','Pénalités et amendes',6,'65','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('6701','Impôts sur les résultats',6,'67','CHARGE',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7113','Vente de marchandises à l''étranger',7,'71','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7118','Ventes de marchandises des exercices précédents',7,'71','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7119','R.R.R accordés par l''entreprise',7,'71','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7125','Ventes de services produits à l''étranger',7,'71','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7126','Redevances pour brevets, marques, droits et valeurs',7,'71','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7127','Ventes de produits résiduels',7,'71','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7128','Ventes de produits et services des exercices précédents',7,'71','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7129','R.R.R accordés sur ventes de produits',7,'71','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7131','Variations des stocks de produits en cours',7,'71','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7132','Variations des stocks de produits finis',7,'71','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7140','Immobilisations produites par l''entreprise pour elle-même',7,'71','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7182','Revenus des immeubles non destinés à l''exploitation',7,'71','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7191','Reprises sur amortissements de l''actif immobilisé',7,'71','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7311','Produits des titres de participation',7,'73','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7331','Gains de change',7,'73','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7381','Intérêts et produits assimilés',7,'73','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7510','Produits des cessions d''immobilisations',7,'75','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7561','Libéralités reçues',7,'75','PRODUIT',0,NULL);
INSERT INTO "comptes_pcm" VALUES('7581','Indemnités d''assurances reçues',7,'75','PRODUIT',0,NULL);
CREATE TABLE compteurs_facturation (
	id INTEGER NOT NULL, 
	societe_id INTEGER NOT NULL, 
	annee INTEGER NOT NULL, 
	dernier_numero INTEGER, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(societe_id) REFERENCES societes (id)
);
INSERT INTO "compteurs_facturation" VALUES(1,2,2026,0,'2026-05-06 12:03:59','2026-05-06 12:03:59');
INSERT INTO "compteurs_facturation" VALUES(2,3,2026,0,'2026-05-06 12:03:59','2026-05-06 12:03:59');
INSERT INTO "compteurs_facturation" VALUES(3,4,2026,0,'2026-05-06 12:03:59','2026-05-06 12:03:59');
CREATE TABLE demandes_acces (
	id INTEGER NOT NULL, 
	nom_complet VARCHAR(255) NOT NULL, 
	entreprise VARCHAR(255) NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	telephone VARCHAR(50), 
	message TEXT, 
	statut VARCHAR(50) NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, cabinet_id INTEGER, 
	PRIMARY KEY (id)
);
CREATE TABLE documents_transmis (
	id INTEGER NOT NULL, 
	societe_id INTEGER NOT NULL, 
	client_id INTEGER, 
	file_path VARCHAR(500) NOT NULL, 
	file_name VARCHAR(255) NOT NULL, 
	type_document VARCHAR(50) DEFAULT 'FACTURE' NOT NULL, 
	statut VARCHAR(30) DEFAULT 'A_TRAITER' NOT NULL, 
	notes_client TEXT, 
	date_upload DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	date_traitement DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(societe_id) REFERENCES societes (id) ON DELETE CASCADE, 
	FOREIGN KEY(client_id) REFERENCES utilisateurs_clients (id) ON DELETE SET NULL
);
CREATE TABLE ecritures_comptables (
	id INTEGER NOT NULL, 
	societe_id INTEGER NOT NULL, 
	facture_id INTEGER NOT NULL, 
	operation VARCHAR(50) NOT NULL, 
	numero_piece VARCHAR(50) NOT NULL, 
	date_operation DATE NOT NULL, 
	tiers_nom VARCHAR(255), 
	journal VARCHAR(10) DEFAULT 'OD' NOT NULL, 
	statut VARCHAR(50) DEFAULT 'brouillon' NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	validated_at DATETIME, 
	libelle VARCHAR(255), 
	total_debit FLOAT DEFAULT '0' NOT NULL, 
	total_credit FLOAT DEFAULT '0' NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(societe_id) REFERENCES societes (id), 
	FOREIGN KEY(facture_id) REFERENCES factures (id) ON DELETE CASCADE
);
CREATE TABLE ecritures_journal (
	id INTEGER NOT NULL, 
	facture_id INTEGER, 
	journal_code VARCHAR(10) NOT NULL, 
	entry_date DATE, 
	reference VARCHAR(100), 
	description TEXT, 
	is_validated BOOLEAN DEFAULT 'false' NOT NULL, 
	validated_by VARCHAR(255), 
	validated_at DATETIME, 
	total_debit NUMERIC(15, 2) DEFAULT '0', 
	total_credit NUMERIC(15, 2) DEFAULT '0', 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, societe_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(facture_id) REFERENCES factures (id) ON DELETE CASCADE
);
INSERT INTO "ecritures_journal" VALUES(1,NULL,'OD','2024-03-28','PAIE-1-03/2024','Bulletin de paie 03/2024 — Driss EL OMARI',0,NULL,NULL,7654.35,7654.35,'2026-03-03 12:44:43',1);
CREATE TABLE ecritures_lignes (
	id INTEGER NOT NULL, 
	ecriture_id INTEGER NOT NULL, 
	compte VARCHAR(20) NOT NULL, 
	libelle VARCHAR(255), 
	debit FLOAT DEFAULT '0' NOT NULL, 
	credit FLOAT DEFAULT '0' NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(ecriture_id) REFERENCES ecritures_comptables (id) ON DELETE CASCADE
);
CREATE TABLE employes (
	id INTEGER NOT NULL, 
	societe_id INTEGER NOT NULL, 
	nom VARCHAR(100) NOT NULL, 
	prenom VARCHAR(100), 
	cin VARCHAR(20), 
	date_naissance DATE, 
	poste VARCHAR(200), 
	date_embauche DATE NOT NULL, 
	type_contrat VARCHAR(20) DEFAULT 'CDI', 
	salaire_base NUMERIC(12, 2) NOT NULL, 
	nb_enfants INTEGER NOT NULL, 
	anciennete_pct NUMERIC(5, 2), 
	numero_cnss VARCHAR(30), 
	affiliee_cnss BOOLEAN, 
	statut VARCHAR(20) DEFAULT 'ACTIF' NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(societe_id) REFERENCES societes (id)
);
INSERT INTO "employes" VALUES(1,1,'EL OMARI','Driss',NULL,NULL,NULL,'2020-01-01','CDI',5000,2,5,NULL,1,'ACTIF','2026-03-03 12:33:57','2026-03-03 12:33:57');
CREATE TABLE entry_lines (
	id INTEGER NOT NULL, 
	journal_entry_id INTEGER NOT NULL, 
	invoice_line_id INTEGER, 
	line_order INTEGER, 
	account_code VARCHAR(10) NOT NULL, 
	account_label VARCHAR(255), 
	debit NUMERIC(15, 2) DEFAULT '0' NOT NULL, 
	credit NUMERIC(15, 2) DEFAULT '0' NOT NULL, 
	tiers_name VARCHAR(255), 
	tiers_ice VARCHAR(15), 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(journal_entry_id) REFERENCES journal_entries (id) ON DELETE CASCADE, 
	FOREIGN KEY(invoice_line_id) REFERENCES invoice_lines (id) ON DELETE SET NULL
);
CREATE TABLE factures (
	id INTEGER NOT NULL, 
	societe_id INTEGER NOT NULL, 
	numero_facture VARCHAR(100), 
	date_facture DATE, 
	due_date DATE, 
	invoice_type VARCHAR(30), 
	supplier_name VARCHAR(255), 
	supplier_ice VARCHAR(15), 
	supplier_if VARCHAR(50), 
	supplier_rc VARCHAR(50), 
	supplier_address TEXT, 
	client_name VARCHAR(255), 
	client_ice VARCHAR(15), 
	client_if VARCHAR(50), 
	client_address TEXT, 
	montant_ht NUMERIC(15, 2), 
	montant_tva NUMERIC(15, 2), 
	montant_ttc NUMERIC(15, 2), 
	taux_tva NUMERIC(5, 2), 
	devise VARCHAR(10) DEFAULT 'MAD', 
	payment_mode VARCHAR(50), 
	payment_terms VARCHAR(100), 
	ocr_confidence FLOAT, 
	extraction_source VARCHAR(20), 
	dgi_flags TEXT, 
	status VARCHAR(30) DEFAULT 'IMPORTED' NOT NULL, 
	validated_by VARCHAR(255), 
	validated_at DATETIME, 
	reject_reason TEXT, 
	file_path VARCHAR(500), 
	fournisseur VARCHAR, 
	operation_type VARCHAR(50), 
	operation_confidence FLOAT, 
	if_frs VARCHAR(50), 
	ice_frs VARCHAR(50), 
	designation VARCHAR(255), 
	id_paie VARCHAR(50), 
	date_paie DATE, 
	ded_file_path VARCHAR(255), 
	ded_pdf_path VARCHAR(255), 
	ded_xlsx_path VARCHAR(255), 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME, file_hash VARCHAR(64), 
	PRIMARY KEY (id), 
	FOREIGN KEY(societe_id) REFERENCES societes (id)
);
INSERT INTO "factures" VALUES(1,1,'FAC-001','2026-02-24',NULL,NULL,'Fournisseur Telecom','999888777',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,120,NULL,'MAD',NULL,NULL,NULL,NULL,NULL,'VALIDATED',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2026-02-24 09:37:57','2026-02-24 09:37:57',NULL);
INSERT INTO "factures" VALUES(2,1,NULL,NULL,NULL,NULL,'Fournisseur Telecom (Bis)','999888777',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'MAD',NULL,NULL,NULL,NULL,NULL,'EXTRACTED',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2026-02-24 09:37:57',NULL,NULL);
INSERT INTO "factures" VALUES(3,1,NULL,'2026-01-01',NULL,NULL,NULL,'123456789012345',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1200.5,NULL,'MAD',NULL,NULL,NULL,NULL,NULL,'EXTRACTED',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2026-02-24 12:28:37',NULL,NULL);
CREATE TABLE immobilisations (
	id INTEGER NOT NULL, 
	societe_id INTEGER NOT NULL, 
	facture_id INTEGER, 
	designation VARCHAR(500) NOT NULL, 
	categorie VARCHAR(30) DEFAULT 'CORPORELLE', 
	date_acquisition DATE NOT NULL, 
	valeur_acquisition NUMERIC(15, 2) NOT NULL, 
	tva_acquisition NUMERIC(15, 2), 
	duree_amortissement INTEGER NOT NULL, 
	taux_amortissement NUMERIC(6, 4), 
	methode VARCHAR(20) DEFAULT 'LINEAIRE' NOT NULL, 
	compte_actif_pcm VARCHAR(10), 
	compte_amort_pcm VARCHAR(10), 
	compte_dotation_pcm VARCHAR(10), 
	statut VARCHAR(20) DEFAULT 'ACTIF' NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(societe_id) REFERENCES societes (id), 
	FOREIGN KEY(facture_id) REFERENCES factures (id)
);
CREATE TABLE invoice_lines (
	id INTEGER NOT NULL, 
	facture_id INTEGER NOT NULL, 
	line_number INTEGER, 
	description TEXT, 
	quantity NUMERIC(10, 3), 
	unit VARCHAR(50), 
	unit_price_ht NUMERIC(15, 4), 
	line_amount_ht NUMERIC(15, 2), 
	tva_rate NUMERIC(5, 2), 
	tva_amount NUMERIC(15, 2), 
	line_amount_ttc NUMERIC(15, 2), 
	pcm_class INTEGER, 
	pcm_account_code VARCHAR(10), 
	pcm_account_label VARCHAR(255), 
	classification_confidence FLOAT, 
	classification_reason TEXT, 
	is_corrected BOOLEAN DEFAULT 'false' NOT NULL, 
	corrected_account_code VARCHAR(10), 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(facture_id) REFERENCES factures (id) ON DELETE CASCADE
);
INSERT INTO "invoice_lines" VALUES(1,1,NULL,'Abonnement Internet',NULL,NULL,NULL,100,NULL,NULL,NULL,NULL,'6111',NULL,NULL,NULL,'false','6144','2026-02-24 09:37:57');
INSERT INTO "invoice_lines" VALUES(2,2,NULL,'Consommation Mobile',NULL,NULL,NULL,50,NULL,NULL,NULL,6,'6144','Postes et télécommunications',1.0,'Appris via l''ICE fournisseur: 999888777','false',NULL,'2026-02-24 09:37:57');
CREATE TABLE journal_entries (
	id INTEGER NOT NULL, 
	facture_id INTEGER NOT NULL, 
	journal_code VARCHAR(10) NOT NULL, 
	entry_date DATE, 
	reference VARCHAR(100), 
	description TEXT, 
	is_validated BOOLEAN DEFAULT 'false' NOT NULL, 
	validated_by VARCHAR(255), 
	validated_at DATETIME, 
	total_debit NUMERIC(15, 2) DEFAULT '0', 
	total_credit NUMERIC(15, 2) DEFAULT '0', 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(facture_id) REFERENCES factures (id) ON DELETE CASCADE
);
CREATE TABLE journaux_comptables (
	id INTEGER NOT NULL, 
	societe_id INTEGER NOT NULL, 
	code VARCHAR(10) NOT NULL, 
	label VARCHAR(100) NOT NULL, 
	type VARCHAR(20) NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(societe_id) REFERENCES societes (id) ON DELETE CASCADE
);
INSERT INTO "journaux_comptables" VALUES(1,1,'ACH','Journal des Achats','ACHAT','2026-03-25 13:42:03','2026-03-25 13:42:03');
INSERT INTO "journaux_comptables" VALUES(2,1,'VTE','Journal des Ventes','VENTE','2026-03-25 13:42:03','2026-03-25 13:42:03');
INSERT INTO "journaux_comptables" VALUES(3,1,'OD','Opérations Diverses','OD','2026-03-25 13:42:03','2026-03-25 13:42:03');
INSERT INTO "journaux_comptables" VALUES(4,1,'BQ','Banque Général','BANQUE','2026-03-25 13:42:03','2026-03-25 13:42:03');
INSERT INTO "journaux_comptables" VALUES(5,1,'IMMO','Journal des Immobilisations','OD','2026-03-25 13:42:03','2026-03-25 13:42:03');
INSERT INTO "journaux_comptables" VALUES(6,1,'PAYE','Journal de Paie','PAIE','2026-03-25 13:42:03','2026-03-25 13:42:03');
CREATE TABLE lignes_amortissement (
	id INTEGER NOT NULL, 
	immobilisation_id INTEGER NOT NULL, 
	annee INTEGER NOT NULL, 
	dotation_annuelle NUMERIC(15, 2) NOT NULL, 
	amortissement_cumule NUMERIC(15, 2) NOT NULL, 
	valeur_nette_comptable NUMERIC(15, 2) NOT NULL, 
	ecriture_generee BOOLEAN, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(immobilisation_id) REFERENCES immobilisations (id) ON DELETE CASCADE
);
CREATE TABLE lignes_ecritures (
	id INTEGER NOT NULL, 
	ecriture_journal_id INTEGER NOT NULL, 
	line_order INTEGER, 
	account_code VARCHAR(10) NOT NULL, 
	account_label VARCHAR(255), 
	debit NUMERIC(15, 2) DEFAULT '0' NOT NULL, 
	credit NUMERIC(15, 2) DEFAULT '0' NOT NULL, 
	tiers_name VARCHAR(255), 
	tiers_ice VARCHAR(15), 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(ecriture_journal_id) REFERENCES ecritures_journal (id) ON DELETE CASCADE
);
INSERT INTO "lignes_ecritures" VALUES(1,1,1,'6171','Rémunérations du personnel',6750,0,NULL,NULL,'2026-03-03 12:44:43');
INSERT INTO "lignes_ecritures" VALUES(2,1,2,'6174','Charges sociales patronales (CNSS+AMO)',904.35,0,NULL,NULL,'2026-03-03 12:44:43');
INSERT INTO "lignes_ecritures" VALUES(3,1,3,'4441','Salaire net à payer — Driss EL OMARI',0,6059.59,'Driss EL OMARI',NULL,'2026-03-03 12:44:43');
INSERT INTO "lignes_ecritures" VALUES(4,1,4,'4443','CNSS — part salarié',0,268.8,NULL,NULL,'2026-03-03 12:44:43');
INSERT INTO "lignes_ecritures" VALUES(5,1,5,'4443','CNSS — part patronale',0,638.4,NULL,NULL,'2026-03-03 12:44:43');
INSERT INTO "lignes_ecritures" VALUES(6,1,6,'4447','AMO — part salarié',0,152.55,NULL,NULL,'2026-03-03 12:44:43');
INSERT INTO "lignes_ecritures" VALUES(7,1,7,'4447','AMO — part patronale',0,265.95,NULL,NULL,'2026-03-03 12:44:43');
INSERT INTO "lignes_ecritures" VALUES(8,1,8,'4444','IR/IGR retenu à la source',0,269.06,NULL,NULL,'2026-03-03 12:44:43');
CREATE TABLE lignes_factures (
	id INTEGER NOT NULL, 
	facture_id INTEGER NOT NULL, 
	line_number INTEGER, 
	description TEXT, 
	quantity NUMERIC(10, 3), 
	unit VARCHAR(50), 
	unit_price_ht NUMERIC(15, 4), 
	line_amount_ht NUMERIC(15, 2), 
	tva_rate NUMERIC(5, 2), 
	tva_amount NUMERIC(15, 2), 
	line_amount_ttc NUMERIC(15, 2), 
	pcm_class INTEGER, 
	pcm_account_code VARCHAR(10), 
	pcm_account_label VARCHAR(255), 
	classification_confidence FLOAT, 
	classification_reason TEXT, 
	is_corrected BOOLEAN DEFAULT 'false' NOT NULL, 
	corrected_account_code VARCHAR(10), 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(facture_id) REFERENCES factures (id) ON DELETE CASCADE
);
CREATE TABLE lignes_paie (
	id INTEGER NOT NULL, 
	bulletin_id INTEGER NOT NULL, 
	libelle VARCHAR(300) NOT NULL, 
	type_ligne VARCHAR(10) NOT NULL, 
	montant NUMERIC(12, 2) NOT NULL, 
	taux NUMERIC(6, 4), 
	base_calcul NUMERIC(12, 2), 
	ordre INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(bulletin_id) REFERENCES bulletins_paie (id) ON DELETE CASCADE
);
INSERT INTO "lignes_paie" VALUES(1,1,'Salaire de base','GAIN',5000,NULL,NULL,1);
INSERT INTO "lignes_paie" VALUES(2,1,'Prime d''ancienneté','GAIN',250,0.05,NULL,2);
INSERT INTO "lignes_paie" VALUES(3,1,'Primes/Avantages','GAIN',1000,NULL,NULL,3);
INSERT INTO "lignes_paie" VALUES(4,1,'Heures supplémentaires','GAIN',500,NULL,NULL,4);
INSERT INTO "lignes_paie" VALUES(5,1,'CNSS salarié (4.48%)','RETENUE',268.8,0.0448,6000,10);
INSERT INTO "lignes_paie" VALUES(6,1,'AMO salarié (2.26%)','RETENUE',152.55,0.0226,6750,11);
INSERT INTO "lignes_paie" VALUES(7,1,'IR/IGR retenu','RETENUE',269.06,NULL,NULL,12);
CREATE TABLE lignes_releves (
	id INTEGER NOT NULL, 
	releve_id INTEGER NOT NULL, 
	date_operation DATE NOT NULL, 
	date_valeur DATE, 
	description TEXT, 
	reference VARCHAR(100), 
	debit NUMERIC(15, 2) DEFAULT '0' NOT NULL, 
	credit NUMERIC(15, 2) DEFAULT '0' NOT NULL, 
	is_rapproche BOOLEAN DEFAULT 'false' NOT NULL, 
	rapprochement_type VARCHAR(20), 
	entry_line_id INTEGER, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(releve_id) REFERENCES releves_bancaires (id) ON DELETE CASCADE, 
	FOREIGN KEY(entry_line_id) REFERENCES lignes_ecritures (id) ON DELETE SET NULL
);
CREATE TABLE mappings_fournisseurs (
	id INTEGER NOT NULL, 
	cabinet_id INTEGER NOT NULL, 
	supplier_ice VARCHAR(15) NOT NULL, 
	pcm_account_code VARCHAR(10) NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(cabinet_id) REFERENCES cabinets (id)
);
CREATE TABLE pcm_accounts (
	code VARCHAR(10) NOT NULL, 
	label VARCHAR(255) NOT NULL, 
	pcm_class INTEGER NOT NULL, 
	group_code VARCHAR(10), 
	account_type VARCHAR(20), 
	is_tva_account BOOLEAN DEFAULT 'false' NOT NULL, 
	tva_type VARCHAR(30), 
	PRIMARY KEY (code)
);
INSERT INTO "pcm_accounts" VALUES('6144','Postes et télécommunications',6,NULL,NULL,'false',NULL);
CREATE TABLE releves_bancaires (
	id INTEGER NOT NULL, 
	societe_id INTEGER NOT NULL, 
	date_import DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	date_debut DATE, 
	date_fin DATE, 
	banque_nom VARCHAR(100), 
	compte_bancaire VARCHAR(50), 
	solde_initial NUMERIC(15, 2), 
	solde_final NUMERIC(15, 2), 
	file_path VARCHAR(500), 
	file_name VARCHAR(255), 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(societe_id) REFERENCES societes (id)
);
CREATE TABLE societes (
	id INTEGER NOT NULL, 
	cabinet_id INTEGER NOT NULL, 
	raison_sociale VARCHAR(255) NOT NULL, 
	ice VARCHAR(15), 
	if_fiscal VARCHAR(50), 
	rc VARCHAR(50), 
	patente VARCHAR(50), 
	adresse VARCHAR(500), 
	logo_path VARCHAR(500), 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, cnss VARCHAR(50), 
	PRIMARY KEY (id), 
	FOREIGN KEY(cabinet_id) REFERENCES cabinets (id)
);
INSERT INTO "societes" VALUES(1,1,'Ma Societe Test','123456789012345',NULL,NULL,NULL,NULL,NULL,'2026-02-24 09:37:57','2026-02-24 09:37:57',NULL);
INSERT INTO "societes" VALUES(2,2,'Ets. EL OUJDI & FILS','001234567890001','12345678','RC-12345','PAT-001','Quartier des Affaires, Casablanca',NULL,'2026-05-06 12:03:59','2026-05-06 12:03:59',NULL);
INSERT INTO "societes" VALUES(3,2,'COMPTOIRE ARRAHMA SARL','002234567890002','87654321','RC-54321','PAT-002','Zone Industrielle, Fès',NULL,'2026-05-06 12:03:59','2026-05-06 12:03:59',NULL);
INSERT INTO "societes" VALUES(4,3,'Entreprise Import-Export','003234567890003','11111111','RC-99999','PAT-003','Port de Casablanca',NULL,'2026-05-06 12:03:59','2026-05-06 12:03:59',NULL);
INSERT INTO "societes" VALUES(5,2,'Entreprise de Test SARL','001234567890001',NULL,NULL,NULL,NULL,NULL,'2026-05-06 12:09:30','2026-05-06 12:09:30',NULL);
CREATE TABLE supplier_mappings (
	id INTEGER NOT NULL, 
	cabinet_id INTEGER NOT NULL, 
	supplier_ice VARCHAR(15) NOT NULL, 
	pcm_account_code VARCHAR(10) NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(cabinet_id) REFERENCES cabinets (id)
);
INSERT INTO "supplier_mappings" VALUES(1,1,'999888777','6144','2026-02-24 09:37:57','2026-02-24 09:37:57');
CREATE TABLE utilisateurs_clients (
	id INTEGER NOT NULL, 
	societe_id INTEGER NOT NULL, 
	username VARCHAR(100) NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	password_hash VARCHAR(500) NOT NULL, 
	nom VARCHAR(255), 
	prenom VARCHAR(255), 
	is_active BOOLEAN, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(societe_id) REFERENCES societes (id) ON DELETE CASCADE, 
	UNIQUE (username), 
	UNIQUE (email)
);
CREATE INDEX ix_cabinets_id ON cabinets (id);
CREATE INDEX ix_agents_cabinet_id ON agents (cabinet_id);
CREATE INDEX ix_agents_id ON agents (id);
CREATE INDEX ix_societes_cabinet_id ON societes (cabinet_id);
CREATE INDEX ix_societes_ice ON societes (ice);
CREATE INDEX ix_societes_id ON societes (id);
CREATE INDEX ix_supplier_mappings_supplier_ice ON supplier_mappings (supplier_ice);
CREATE INDEX ix_supplier_mappings_cabinet_id ON supplier_mappings (cabinet_id);
CREATE INDEX ix_supplier_mappings_id ON supplier_mappings (id);
CREATE INDEX ix_compteurs_facturation_id ON compteurs_facturation (id);
CREATE INDEX ix_compteurs_facturation_societe_id ON compteurs_facturation (societe_id);
CREATE INDEX ix_factures_societe_id ON factures (societe_id);
CREATE INDEX ix_factures_id ON factures (id);
CREATE INDEX ix_invoice_lines_id ON invoice_lines (id);
CREATE INDEX ix_invoice_lines_facture_id ON invoice_lines (facture_id);
CREATE INDEX ix_journal_entries_id ON journal_entries (id);
CREATE INDEX ix_journal_entries_facture_id ON journal_entries (facture_id);
CREATE INDEX ix_ecritures_comptables_facture_id ON ecritures_comptables (facture_id);
CREATE INDEX ix_ecritures_comptables_journal ON ecritures_comptables (journal);
CREATE INDEX ix_ecritures_comptables_societe_id ON ecritures_comptables (societe_id);
CREATE INDEX ix_ecritures_comptables_date_operation ON ecritures_comptables (date_operation);
CREATE INDEX ix_ecritures_comptables_id ON ecritures_comptables (id);
CREATE INDEX ix_ecritures_comptables_numero_piece ON ecritures_comptables (numero_piece);
CREATE INDEX ix_entry_lines_id ON entry_lines (id);
CREATE INDEX ix_entry_lines_journal_entry_id ON entry_lines (journal_entry_id);
CREATE INDEX ix_ecritures_lignes_ecriture_id ON ecritures_lignes (ecriture_id);
CREATE INDEX ix_ecritures_lignes_id ON ecritures_lignes (id);
CREATE INDEX ix_lignes_factures_facture_id ON lignes_factures (facture_id);
CREATE INDEX ix_lignes_factures_id ON lignes_factures (id);
CREATE INDEX ix_mappings_fournisseurs_supplier_ice ON mappings_fournisseurs (supplier_ice);
CREATE INDEX ix_mappings_fournisseurs_cabinet_id ON mappings_fournisseurs (cabinet_id);
CREATE INDEX ix_mappings_fournisseurs_id ON mappings_fournisseurs (id);
CREATE INDEX ix_action_logs_id ON action_logs (id);
CREATE INDEX ix_action_logs_cabinet_id ON action_logs (cabinet_id);
CREATE INDEX ix_immobilisations_id ON immobilisations (id);
CREATE INDEX ix_immobilisations_facture_id ON immobilisations (facture_id);
CREATE INDEX ix_immobilisations_societe_id ON immobilisations (societe_id);
CREATE INDEX ix_employes_id ON employes (id);
CREATE INDEX ix_employes_societe_id ON employes (societe_id);
CREATE INDEX ix_lignes_amortissement_id ON lignes_amortissement (id);
CREATE INDEX ix_lignes_amortissement_immobilisation_id ON lignes_amortissement (immobilisation_id);
CREATE INDEX ix_ecritures_journal_id ON ecritures_journal (id);
CREATE INDEX ix_ecritures_journal_facture_id ON ecritures_journal (facture_id);
CREATE INDEX ix_lignes_ecritures_id ON lignes_ecritures (id);
CREATE INDEX ix_lignes_ecritures_ecriture_journal_id ON lignes_ecritures (ecriture_journal_id);
CREATE INDEX ix_bulletins_paie_id ON bulletins_paie (id);
CREATE INDEX ix_bulletins_paie_employe_id ON bulletins_paie (employe_id);
CREATE INDEX ix_lignes_paie_id ON lignes_paie (id);
CREATE INDEX ix_lignes_paie_bulletin_id ON lignes_paie (bulletin_id);
CREATE INDEX ix_factures_file_hash ON factures (file_hash);
CREATE INDEX ix_releves_bancaires_societe_id ON releves_bancaires (societe_id);
CREATE INDEX ix_releves_bancaires_id ON releves_bancaires (id);
CREATE INDEX ix_lignes_releves_releve_id ON lignes_releves (releve_id);
CREATE INDEX ix_lignes_releves_id ON lignes_releves (id);
CREATE INDEX ix_utilisateurs_clients_societe_id ON utilisateurs_clients (societe_id);
CREATE INDEX ix_utilisateurs_clients_id ON utilisateurs_clients (id);
CREATE INDEX ix_documents_transmis_societe_id ON documents_transmis (societe_id);
CREATE INDEX ix_documents_transmis_id ON documents_transmis (id);
CREATE INDEX ix_journaux_comptables_societe_id ON journaux_comptables (societe_id);
CREATE INDEX ix_journaux_comptables_id ON journaux_comptables (id);
CREATE INDEX ix_demandes_acces_id ON demandes_acces (id);
COMMIT;
