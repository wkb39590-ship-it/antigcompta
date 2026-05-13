--
-- PostgreSQL database dump
--

\restrict 0njt2Zz3tL4miRVVHxCvIFDxe065vm7d1QcJG8gmxjEfEdBx4agE7X6uR1QTeML

-- Dumped from database version 15.17 (Debian 15.17-1.pgdg13+1)
-- Dumped by pg_dump version 15.17 (Debian 15.17-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: action_logs; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.action_logs (
    id integer NOT NULL,
    cabinet_id integer,
    agent_id integer,
    action_type character varying(50) NOT NULL,
    entity_type character varying(50) NOT NULL,
    entity_id integer,
    details text,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.action_logs OWNER TO admin;

--
-- Name: action_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.action_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.action_logs_id_seq OWNER TO admin;

--
-- Name: action_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.action_logs_id_seq OWNED BY public.action_logs.id;


--
-- Name: agents; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.agents (
    id integer NOT NULL,
    cabinet_id integer NOT NULL,
    username character varying(100) NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(500) NOT NULL,
    nom character varying(255),
    prenom character varying(255),
    is_active boolean,
    is_admin boolean,
    is_super_admin boolean,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.agents OWNER TO admin;

--
-- Name: agents_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.agents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.agents_id_seq OWNER TO admin;

--
-- Name: agents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.agents_id_seq OWNED BY public.agents.id;


--
-- Name: agents_societes; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.agents_societes (
    agent_id integer NOT NULL,
    societe_id integer NOT NULL
);


ALTER TABLE public.agents_societes OWNER TO admin;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO admin;

--
-- Name: bulletins_paie; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.bulletins_paie (
    id integer NOT NULL,
    employe_id integer NOT NULL,
    mois integer NOT NULL,
    annee integer NOT NULL,
    salaire_base numeric(12,2) NOT NULL,
    prime_anciennete numeric(12,2),
    autres_gains numeric(12,2),
    salaire_brut numeric(12,2) NOT NULL,
    cnss_salarie numeric(10,2) NOT NULL,
    amo_salarie numeric(10,2) NOT NULL,
    ir_retenu numeric(10,2) NOT NULL,
    total_retenues numeric(10,2) NOT NULL,
    cnss_patronal numeric(10,2) NOT NULL,
    amo_patronal numeric(10,2) NOT NULL,
    total_patronal numeric(10,2) NOT NULL,
    salaire_net numeric(12,2) NOT NULL,
    cout_total_employeur numeric(12,2),
    journal_entry_id integer,
    statut character varying(20) DEFAULT 'BROUILLON'::character varying NOT NULL,
    valide_par character varying(100),
    valide_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.bulletins_paie OWNER TO admin;

--
-- Name: bulletins_paie_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.bulletins_paie_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bulletins_paie_id_seq OWNER TO admin;

--
-- Name: bulletins_paie_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.bulletins_paie_id_seq OWNED BY public.bulletins_paie.id;


--
-- Name: cabinets; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.cabinets (
    id integer NOT NULL,
    nom character varying(255) NOT NULL,
    email character varying(255),
    telephone character varying(20),
    adresse character varying(500),
    logo_path character varying(500),
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.cabinets OWNER TO admin;

--
-- Name: cabinets_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.cabinets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cabinets_id_seq OWNER TO admin;

--
-- Name: cabinets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.cabinets_id_seq OWNED BY public.cabinets.id;


--
-- Name: comptes_pcm; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.comptes_pcm (
    code character varying(10) NOT NULL,
    label character varying(255) NOT NULL,
    pcm_class integer NOT NULL,
    group_code character varying(10),
    account_type character varying(20),
    is_tva_account boolean DEFAULT false NOT NULL,
    tva_type character varying(30)
);


ALTER TABLE public.comptes_pcm OWNER TO admin;

--
-- Name: compteurs_facturation; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.compteurs_facturation (
    id integer NOT NULL,
    societe_id integer NOT NULL,
    annee integer NOT NULL,
    dernier_numero integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.compteurs_facturation OWNER TO admin;

--
-- Name: compteurs_facturation_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.compteurs_facturation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.compteurs_facturation_id_seq OWNER TO admin;

--
-- Name: compteurs_facturation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.compteurs_facturation_id_seq OWNED BY public.compteurs_facturation.id;


--
-- Name: demandes_acces; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.demandes_acces (
    id integer NOT NULL,
    cabinet_id integer,
    nom_complet character varying(255) NOT NULL,
    entreprise character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    telephone character varying(50),
    message text,
    statut character varying(50) NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.demandes_acces OWNER TO admin;

--
-- Name: demandes_acces_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.demandes_acces_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.demandes_acces_id_seq OWNER TO admin;

--
-- Name: demandes_acces_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.demandes_acces_id_seq OWNED BY public.demandes_acces.id;


--
-- Name: documents_transmis; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.documents_transmis (
    id integer NOT NULL,
    societe_id integer NOT NULL,
    client_id integer,
    file_path character varying(500) NOT NULL,
    file_name character varying(255) NOT NULL,
    type_document character varying(50) DEFAULT 'FACTURE'::character varying NOT NULL,
    statut character varying(30) DEFAULT 'A_TRAITER'::character varying NOT NULL,
    notes_client text,
    date_upload timestamp without time zone DEFAULT now() NOT NULL,
    date_traitement timestamp without time zone,
    facture_id integer
);


ALTER TABLE public.documents_transmis OWNER TO admin;

--
-- Name: documents_transmis_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.documents_transmis_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.documents_transmis_id_seq OWNER TO admin;

--
-- Name: documents_transmis_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.documents_transmis_id_seq OWNED BY public.documents_transmis.id;


--
-- Name: ecritures_journal; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.ecritures_journal (
    id integer NOT NULL,
    societe_id integer,
    facture_id integer,
    journal_code character varying(10) NOT NULL,
    entry_date date,
    reference character varying(100),
    description text,
    is_validated boolean DEFAULT false NOT NULL,
    validated_by character varying(255),
    validated_at timestamp without time zone,
    total_debit numeric(15,2) DEFAULT '0'::numeric,
    total_credit numeric(15,2) DEFAULT '0'::numeric,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.ecritures_journal OWNER TO admin;

--
-- Name: ecritures_journal_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.ecritures_journal_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ecritures_journal_id_seq OWNER TO admin;

--
-- Name: ecritures_journal_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.ecritures_journal_id_seq OWNED BY public.ecritures_journal.id;


--
-- Name: employes; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.employes (
    id integer NOT NULL,
    societe_id integer NOT NULL,
    nom character varying(100) NOT NULL,
    prenom character varying(100) NOT NULL,
    cin character varying(20),
    date_naissance date,
    poste character varying(200),
    date_embauche date NOT NULL,
    type_contrat character varying(20) DEFAULT 'CDI'::character varying,
    salaire_base numeric(12,2) NOT NULL,
    nb_enfants integer NOT NULL,
    anciennete_pct numeric(5,2),
    numero_cnss character varying(30),
    affiliee_cnss boolean,
    statut character varying(20) DEFAULT 'ACTIF'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    matricule character varying(20),
    situation_familiale character varying(50),
    adresse character varying(500),
    departement character varying(100),
    numero_mutuelle character varying(30),
    numero_retraite character varying(30)
);


ALTER TABLE public.employes OWNER TO admin;

--
-- Name: employes_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.employes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.employes_id_seq OWNER TO admin;

--
-- Name: employes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.employes_id_seq OWNED BY public.employes.id;


--
-- Name: factures; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.factures (
    id integer NOT NULL,
    societe_id integer NOT NULL,
    numero_facture character varying(100),
    date_facture date,
    due_date date,
    invoice_type character varying(30),
    supplier_name character varying(255),
    supplier_ice character varying(15),
    supplier_if character varying(50),
    supplier_rc character varying(50),
    supplier_address text,
    client_name character varying(255),
    client_ice character varying(15),
    client_if character varying(50),
    client_address text,
    montant_ht numeric(15,2),
    montant_tva numeric(15,2),
    montant_ttc numeric(15,2),
    taux_tva numeric(5,2),
    devise character varying(10) DEFAULT 'MAD'::character varying,
    payment_mode character varying(50),
    payment_terms character varying(100),
    ocr_confidence double precision,
    extraction_source character varying(20),
    dgi_flags text,
    status character varying(30) DEFAULT 'IMPORTED'::character varying NOT NULL,
    validated_by character varying(255),
    validated_at timestamp without time zone,
    reject_reason text,
    file_path character varying(500),
    file_hash character varying(64),
    fournisseur character varying,
    operation_type character varying(50),
    operation_confidence double precision,
    if_frs character varying(50),
    ice_frs character varying(50),
    designation character varying(255),
    id_paie character varying(50),
    date_paie date,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    ded_file_path character varying(255),
    ded_pdf_path character varying(255),
    ded_xlsx_path character varying(255)
);


ALTER TABLE public.factures OWNER TO admin;

--
-- Name: factures_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.factures_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.factures_id_seq OWNER TO admin;

--
-- Name: factures_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.factures_id_seq OWNED BY public.factures.id;


--
-- Name: immobilisations; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.immobilisations (
    id integer NOT NULL,
    societe_id integer NOT NULL,
    facture_id integer,
    designation character varying(500) NOT NULL,
    categorie character varying(30) DEFAULT 'CORPORELLE'::character varying,
    date_acquisition date NOT NULL,
    valeur_acquisition numeric(15,2) NOT NULL,
    tva_acquisition numeric(15,2),
    duree_amortissement integer NOT NULL,
    taux_amortissement numeric(6,4),
    methode character varying(20) DEFAULT 'LINEAIRE'::character varying NOT NULL,
    compte_actif_pcm character varying(10),
    compte_amort_pcm character varying(10),
    compte_dotation_pcm character varying(10),
    statut character varying(20) DEFAULT 'ACTIF'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.immobilisations OWNER TO admin;

--
-- Name: immobilisations_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.immobilisations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.immobilisations_id_seq OWNER TO admin;

--
-- Name: immobilisations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.immobilisations_id_seq OWNED BY public.immobilisations.id;


--
-- Name: journaux_comptables; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.journaux_comptables (
    id integer NOT NULL,
    societe_id integer NOT NULL,
    code character varying(10) NOT NULL,
    label character varying(100) NOT NULL,
    type character varying(20) NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.journaux_comptables OWNER TO admin;

--
-- Name: journaux_comptables_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.journaux_comptables_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.journaux_comptables_id_seq OWNER TO admin;

--
-- Name: journaux_comptables_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.journaux_comptables_id_seq OWNED BY public.journaux_comptables.id;


--
-- Name: lignes_amortissement; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.lignes_amortissement (
    id integer NOT NULL,
    immobilisation_id integer NOT NULL,
    annee integer NOT NULL,
    dotation_annuelle numeric(15,2) NOT NULL,
    amortissement_cumule numeric(15,2) NOT NULL,
    valeur_nette_comptable numeric(15,2) NOT NULL,
    ecriture_generee boolean,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.lignes_amortissement OWNER TO admin;

--
-- Name: lignes_amortissement_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.lignes_amortissement_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lignes_amortissement_id_seq OWNER TO admin;

--
-- Name: lignes_amortissement_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.lignes_amortissement_id_seq OWNED BY public.lignes_amortissement.id;


--
-- Name: lignes_ecritures; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.lignes_ecritures (
    id integer NOT NULL,
    ecriture_journal_id integer NOT NULL,
    line_order integer,
    account_code character varying(10) NOT NULL,
    account_label character varying(255),
    debit numeric(15,2) DEFAULT '0'::numeric NOT NULL,
    credit numeric(15,2) DEFAULT '0'::numeric NOT NULL,
    tiers_name character varying(255),
    tiers_ice character varying(15),
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.lignes_ecritures OWNER TO admin;

--
-- Name: lignes_ecritures_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.lignes_ecritures_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lignes_ecritures_id_seq OWNER TO admin;

--
-- Name: lignes_ecritures_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.lignes_ecritures_id_seq OWNED BY public.lignes_ecritures.id;


--
-- Name: lignes_factures; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.lignes_factures (
    id integer NOT NULL,
    facture_id integer NOT NULL,
    line_number integer,
    description text,
    quantity numeric(10,3),
    unit character varying(50),
    unit_price_ht numeric(15,4),
    line_amount_ht numeric(15,2),
    tva_rate numeric(5,2),
    tva_amount numeric(15,2),
    line_amount_ttc numeric(15,2),
    pcm_class integer,
    pcm_account_code character varying(10),
    pcm_account_label character varying(255),
    classification_confidence double precision,
    classification_reason text,
    is_corrected boolean DEFAULT false NOT NULL,
    corrected_account_code character varying(10),
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.lignes_factures OWNER TO admin;

--
-- Name: lignes_factures_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.lignes_factures_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lignes_factures_id_seq OWNER TO admin;

--
-- Name: lignes_factures_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.lignes_factures_id_seq OWNED BY public.lignes_factures.id;


--
-- Name: lignes_paie; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.lignes_paie (
    id integer NOT NULL,
    bulletin_id integer NOT NULL,
    libelle character varying(300) NOT NULL,
    type_ligne character varying(10) NOT NULL,
    montant numeric(12,2) NOT NULL,
    taux numeric(6,4),
    base_calcul numeric(12,2),
    ordre integer
);


ALTER TABLE public.lignes_paie OWNER TO admin;

--
-- Name: lignes_paie_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.lignes_paie_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lignes_paie_id_seq OWNER TO admin;

--
-- Name: lignes_paie_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.lignes_paie_id_seq OWNED BY public.lignes_paie.id;


--
-- Name: lignes_releves; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.lignes_releves (
    id integer NOT NULL,
    releve_id integer NOT NULL,
    date_operation date NOT NULL,
    date_valeur date,
    description text,
    reference character varying(100),
    debit numeric(15,2) DEFAULT '0'::numeric NOT NULL,
    credit numeric(15,2) DEFAULT '0'::numeric NOT NULL,
    is_rapproche boolean DEFAULT false NOT NULL,
    rapprochement_type character varying(20),
    entry_line_id integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.lignes_releves OWNER TO admin;

--
-- Name: lignes_releves_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.lignes_releves_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lignes_releves_id_seq OWNER TO admin;

--
-- Name: lignes_releves_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.lignes_releves_id_seq OWNED BY public.lignes_releves.id;


--
-- Name: mappings_fournisseurs; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.mappings_fournisseurs (
    id integer NOT NULL,
    cabinet_id integer NOT NULL,
    supplier_ice character varying(15) NOT NULL,
    pcm_account_code character varying(10) NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.mappings_fournisseurs OWNER TO admin;

--
-- Name: mappings_fournisseurs_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.mappings_fournisseurs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mappings_fournisseurs_id_seq OWNER TO admin;

--
-- Name: mappings_fournisseurs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.mappings_fournisseurs_id_seq OWNED BY public.mappings_fournisseurs.id;


--
-- Name: releves_bancaires; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.releves_bancaires (
    id integer NOT NULL,
    societe_id integer NOT NULL,
    date_import timestamp without time zone DEFAULT now() NOT NULL,
    date_debut date,
    date_fin date,
    banque_nom character varying(100),
    compte_bancaire character varying(50),
    solde_initial numeric(15,2),
    solde_final numeric(15,2),
    file_path character varying(500),
    file_name character varying(255),
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.releves_bancaires OWNER TO admin;

--
-- Name: releves_bancaires_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.releves_bancaires_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.releves_bancaires_id_seq OWNER TO admin;

--
-- Name: releves_bancaires_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.releves_bancaires_id_seq OWNED BY public.releves_bancaires.id;


--
-- Name: societes; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.societes (
    id integer NOT NULL,
    cabinet_id integer NOT NULL,
    raison_sociale character varying(255) NOT NULL,
    ice character varying(15),
    if_fiscal character varying(50),
    rc character varying(50),
    patente character varying(50),
    adresse character varying(500),
    cnss character varying(50),
    logo_path character varying(500),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.societes OWNER TO admin;

--
-- Name: societes_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.societes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.societes_id_seq OWNER TO admin;

--
-- Name: societes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.societes_id_seq OWNED BY public.societes.id;


--
-- Name: utilisateurs_clients; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.utilisateurs_clients (
    id integer NOT NULL,
    societe_id integer NOT NULL,
    username character varying(100) NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(500) NOT NULL,
    nom character varying(255),
    prenom character varying(255),
    is_active boolean,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.utilisateurs_clients OWNER TO admin;

--
-- Name: utilisateurs_clients_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.utilisateurs_clients_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.utilisateurs_clients_id_seq OWNER TO admin;

--
-- Name: utilisateurs_clients_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.utilisateurs_clients_id_seq OWNED BY public.utilisateurs_clients.id;


--
-- Name: action_logs id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.action_logs ALTER COLUMN id SET DEFAULT nextval('public.action_logs_id_seq'::regclass);


--
-- Name: agents id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.agents ALTER COLUMN id SET DEFAULT nextval('public.agents_id_seq'::regclass);


--
-- Name: bulletins_paie id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.bulletins_paie ALTER COLUMN id SET DEFAULT nextval('public.bulletins_paie_id_seq'::regclass);


--
-- Name: cabinets id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.cabinets ALTER COLUMN id SET DEFAULT nextval('public.cabinets_id_seq'::regclass);


--
-- Name: compteurs_facturation id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.compteurs_facturation ALTER COLUMN id SET DEFAULT nextval('public.compteurs_facturation_id_seq'::regclass);


--
-- Name: demandes_acces id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.demandes_acces ALTER COLUMN id SET DEFAULT nextval('public.demandes_acces_id_seq'::regclass);


--
-- Name: documents_transmis id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.documents_transmis ALTER COLUMN id SET DEFAULT nextval('public.documents_transmis_id_seq'::regclass);


--
-- Name: ecritures_journal id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.ecritures_journal ALTER COLUMN id SET DEFAULT nextval('public.ecritures_journal_id_seq'::regclass);


--
-- Name: employes id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.employes ALTER COLUMN id SET DEFAULT nextval('public.employes_id_seq'::regclass);


--
-- Name: factures id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.factures ALTER COLUMN id SET DEFAULT nextval('public.factures_id_seq'::regclass);


--
-- Name: immobilisations id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.immobilisations ALTER COLUMN id SET DEFAULT nextval('public.immobilisations_id_seq'::regclass);


--
-- Name: journaux_comptables id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.journaux_comptables ALTER COLUMN id SET DEFAULT nextval('public.journaux_comptables_id_seq'::regclass);


--
-- Name: lignes_amortissement id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lignes_amortissement ALTER COLUMN id SET DEFAULT nextval('public.lignes_amortissement_id_seq'::regclass);


--
-- Name: lignes_ecritures id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lignes_ecritures ALTER COLUMN id SET DEFAULT nextval('public.lignes_ecritures_id_seq'::regclass);


--
-- Name: lignes_factures id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lignes_factures ALTER COLUMN id SET DEFAULT nextval('public.lignes_factures_id_seq'::regclass);


--
-- Name: lignes_paie id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lignes_paie ALTER COLUMN id SET DEFAULT nextval('public.lignes_paie_id_seq'::regclass);


--
-- Name: lignes_releves id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lignes_releves ALTER COLUMN id SET DEFAULT nextval('public.lignes_releves_id_seq'::regclass);


--
-- Name: mappings_fournisseurs id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.mappings_fournisseurs ALTER COLUMN id SET DEFAULT nextval('public.mappings_fournisseurs_id_seq'::regclass);


--
-- Name: releves_bancaires id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.releves_bancaires ALTER COLUMN id SET DEFAULT nextval('public.releves_bancaires_id_seq'::regclass);


--
-- Name: societes id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.societes ALTER COLUMN id SET DEFAULT nextval('public.societes_id_seq'::regclass);


--
-- Name: utilisateurs_clients id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.utilisateurs_clients ALTER COLUMN id SET DEFAULT nextval('public.utilisateurs_clients_id_seq'::regclass);


--
-- Data for Name: action_logs; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.action_logs (id, cabinet_id, agent_id, action_type, entity_type, entity_id, details, created_at) FROM stdin;
1	3	3	UPLOAD	FACTURE	4	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-06 20:37:32.233007
2	3	3	DELETE	FACTURE	4	Suppression de la facture 4 et de ses fichiers	2026-05-06 20:38:54.419986
3	3	3	UPLOAD	FACTURE	5	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-06 20:39:04.923107
4	3	3	DELETE	FACTURE	5	Suppression de la facture 5 et de ses fichiers	2026-05-06 20:41:33.992881
5	3	3	UPLOAD	FACTURE	6	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-06 20:41:43.928486
6	3	3	DELETE	FACTURE	6	Suppression de la facture 6 et de ses fichiers	2026-05-06 20:44:51.260152
7	3	3	UPLOAD	FACTURE	101	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-06 20:44:58.810012
8	3	3	EXTRACTION	FACTURE	101	Extraction OCR/IA réussie (N° N/A)	2026-05-06 20:45:16.06196
9	3	3	CLASSIFICATION	FACTURE	101	Classification PCM des lignes terminée	2026-05-06 20:45:20.719814
10	3	3	GENERATION_BROUILLON	FACTURE	101	Génération du brouillon d'écriture comptable	2026-05-06 20:45:20.759242
11	3	3	DELETE	FACTURE	101	Suppression de la facture 101 et de ses fichiers	2026-05-06 20:47:38.697044
12	3	3	UPLOAD	FACTURE	102	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-06 20:47:48.948645
13	3	3	EXTRACTION	FACTURE	102	Extraction OCR/IA réussie (N° N/A)	2026-05-06 20:48:06.473618
14	3	3	CLASSIFICATION	FACTURE	102	Classification PCM des lignes terminée	2026-05-06 20:48:11.218612
15	3	3	GENERATION_BROUILLON	FACTURE	102	Génération du brouillon d'écriture comptable	2026-05-06 20:48:11.24261
16	3	3	DELETE	FACTURE	102	Suppression de la facture 102 et de ses fichiers	2026-05-06 20:57:11.647029
17	3	3	UPLOAD	FACTURE	103	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-06 20:57:20.690746
18	3	3	EXTRACTION	FACTURE	103	Extraction OCR/IA réussie (N° N/A)	2026-05-06 20:57:39.194899
19	3	3	CLASSIFICATION	FACTURE	103	Classification PCM des lignes terminée	2026-05-06 20:57:43.899904
20	3	3	GENERATION_BROUILLON	FACTURE	103	Génération du brouillon d'écriture comptable	2026-05-06 20:57:43.923272
21	3	3	DELETE	FACTURE	103	Suppression de la facture 103 et de ses fichiers	2026-05-06 21:00:52.937596
22	3	3	UPLOAD	FACTURE	104	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-06 21:01:12.002819
23	3	3	EXTRACTION	FACTURE	104	Extraction OCR/IA réussie (N° N/A)	2026-05-06 21:01:30.803235
24	3	3	CLASSIFICATION	FACTURE	104	Classification PCM des lignes terminée	2026-05-06 21:01:35.379517
25	3	3	GENERATION_BROUILLON	FACTURE	104	Génération du brouillon d'écriture comptable	2026-05-06 21:01:35.405265
26	3	3	DELETE	FACTURE	104	Suppression de la facture 104 et de ses fichiers	2026-05-06 21:08:33.261758
27	3	3	UPLOAD	FACTURE	105	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-06 21:08:44.683104
28	3	3	EXTRACTION	FACTURE	105	Extraction OCR/IA réussie (N° N/A)	2026-05-06 21:09:02.085264
29	3	3	CLASSIFICATION	FACTURE	105	Classification PCM des lignes terminée	2026-05-06 21:09:06.620124
30	3	3	GENERATION_BROUILLON	FACTURE	105	Génération du brouillon d'écriture comptable	2026-05-06 21:09:06.647856
31	3	3	DELETE	FACTURE	105	Suppression de la facture 105 et de ses fichiers	2026-05-06 21:12:25.317429
32	3	3	UPLOAD	FACTURE	106	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-06 21:12:34.909369
33	3	3	EXTRACTION	FACTURE	106	Extraction OCR/IA réussie (N° N/A)	2026-05-06 21:12:52.463551
34	3	3	CLASSIFICATION	FACTURE	106	Classification PCM des lignes terminée	2026-05-06 21:12:56.959072
35	3	3	GENERATION_BROUILLON	FACTURE	106	Génération du brouillon d'écriture comptable	2026-05-06 21:12:56.98485
36	3	3	DELETE	FACTURE	106	Suppression de la facture 106 et de ses fichiers	2026-05-06 21:16:14.264011
37	3	3	UPLOAD	FACTURE	107	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-06 21:16:25.560095
38	3	3	EXTRACTION	FACTURE	107	Extraction OCR/IA réussie (N° N/A)	2026-05-06 21:16:45.36077
39	3	3	CLASSIFICATION	FACTURE	107	Classification PCM des lignes terminée	2026-05-06 21:16:49.98647
40	3	3	GENERATION_BROUILLON	FACTURE	107	Génération du brouillon d'écriture comptable	2026-05-06 21:16:50.020143
41	3	3	DELETE	FACTURE	107	Suppression de la facture 107 et de ses fichiers	2026-05-06 21:18:54.407157
42	3	3	UPLOAD	FACTURE	108	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-06 21:19:04.526759
43	3	3	EXTRACTION	FACTURE	108	Extraction OCR/IA réussie (N° N/A)	2026-05-06 21:19:23.314673
44	3	3	CLASSIFICATION	FACTURE	108	Classification PCM des lignes terminée	2026-05-06 21:19:27.963233
45	3	3	GENERATION_BROUILLON	FACTURE	108	Génération du brouillon d'écriture comptable	2026-05-06 21:19:27.986873
46	3	3	DELETE	FACTURE	108	Suppression de la facture 108 et de ses fichiers	2026-05-06 21:21:59.983057
47	3	3	UPLOAD	FACTURE	109	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-06 21:22:08.349826
48	3	3	EXTRACTION	FACTURE	109	Extraction OCR/IA réussie (N° N/A)	2026-05-06 21:22:25.949973
49	3	3	CLASSIFICATION	FACTURE	109	Classification PCM des lignes terminée	2026-05-06 21:22:30.514882
50	3	3	GENERATION_BROUILLON	FACTURE	109	Génération du brouillon d'écriture comptable	2026-05-06 21:22:30.541014
51	3	3	DELETE	FACTURE	109	Suppression de la facture 109 et de ses fichiers	2026-05-06 21:26:46.82811
52	3	3	UPLOAD	FACTURE	110	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-06 21:27:16.637641
53	3	3	EXTRACTION	FACTURE	110	Extraction OCR/IA réussie (N° N/A)	2026-05-06 21:27:34.175941
54	3	3	CLASSIFICATION	FACTURE	110	Classification PCM des lignes terminée	2026-05-06 21:27:38.795299
55	3	3	GENERATION_BROUILLON	FACTURE	110	Génération du brouillon d'écriture comptable	2026-05-06 21:27:38.818367
56	3	3	DELETE	FACTURE	110	Suppression de la facture 110 et de ses fichiers	2026-05-06 21:29:13.600401
57	3	3	UPLOAD	FACTURE	111	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-06 21:29:25.379772
58	3	3	EXTRACTION	FACTURE	111	Extraction OCR/IA réussie (N° N/A)	2026-05-06 21:29:43.392416
59	3	3	CLASSIFICATION	FACTURE	111	Classification PCM des lignes terminée	2026-05-06 21:29:48.119213
60	3	3	GENERATION_BROUILLON	FACTURE	111	Génération du brouillon d'écriture comptable	2026-05-06 21:29:48.15684
61	3	3	DELETE	FACTURE	111	Suppression de la facture 111 et de ses fichiers	2026-05-06 21:35:06.703903
62	3	3	UPLOAD	FACTURE	112	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-06 21:35:15.855054
63	3	3	EXTRACTION	FACTURE	112	Extraction OCR/IA réussie (N° N/A)	2026-05-06 21:35:33.54517
64	3	3	CLASSIFICATION	FACTURE	112	Classification PCM des lignes terminée	2026-05-06 21:35:38.164458
65	3	3	GENERATION_BROUILLON	FACTURE	112	Génération du brouillon d'écriture comptable	2026-05-06 21:35:38.199953
66	3	3	DELETE	FACTURE	112	Suppression de la facture 112 et de ses fichiers	2026-05-06 21:37:28.495604
67	3	3	UPLOAD	FACTURE	113	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-06 21:37:39.674088
71	3	3	DELETE	FACTURE	113	Suppression de la facture 113 et de ses fichiers	2026-05-06 21:45:26.405798
68	3	3	EXTRACTION	FACTURE	113	Extraction OCR/IA réussie (N° N/A)	2026-05-06 21:37:58.532845
74	3	3	CLASSIFICATION	FACTURE	114	Classification PCM des lignes terminée	2026-05-06 21:46:11.898709
69	3	3	CLASSIFICATION	FACTURE	113	Classification PCM des lignes terminée	2026-05-06 21:38:03.15864
72	3	3	UPLOAD	FACTURE	114	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-06 21:45:47.75968
70	3	3	GENERATION_BROUILLON	FACTURE	113	Génération du brouillon d'écriture comptable	2026-05-06 21:38:03.192463
75	3	3	GENERATION_BROUILLON	FACTURE	114	Génération du brouillon d'écriture comptable	2026-05-06 21:46:11.933444
73	3	3	EXTRACTION	FACTURE	114	Extraction OCR/IA réussie (N° N/A)	2026-05-06 21:46:07.408974
76	3	3	DELETE	FACTURE	114	Suppression de la facture 114 et de ses fichiers	2026-05-06 21:48:45.880684
77	3	3	UPLOAD	FACTURE	115	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-06 21:48:53.785307
78	3	3	EXTRACTION	FACTURE	115	Extraction OCR/IA réussie (N° N/A)	2026-05-06 21:49:11.651454
79	3	3	CLASSIFICATION	FACTURE	115	Classification PCM des lignes terminée	2026-05-06 21:49:16.906298
80	3	3	GENERATION_BROUILLON	FACTURE	115	Génération du brouillon d'écriture comptable	2026-05-06 21:49:17.038243
81	3	3	DELETE	FACTURE	115	Suppression de la facture 115 et de ses fichiers	2026-05-06 23:07:04.564178
82	2	1	CREATE	AGENT	5	Agent mohammed créé	2026-05-06 23:29:06.680063
83	2	5	DELETE	SOCIETE	3	Société COMPTOIRE ARRAHMA SARL supprimée	2026-05-06 23:43:44.683939
84	2	5	CREATE	SOCIETE	6	Société STE Comptoire Arrahma S.A.R.L créée	2026-05-06 23:45:03.694466
85	2	5	CREATE	AGENT	6	Agent khadija créé	2026-05-06 23:48:54.662255
86	2	5	ASSOCIATION	AGENT_SOCIETE	6	Agent khadija associé à STE Comptoire Arrahma S.A.R.L	2026-05-06 23:48:54.70216
87	2	5	ASSOCIATION	AGENT_SOCIETE	6	Agent khadija associé à Ets. EL OUJDI & FILS	2026-05-06 23:49:46.030682
88	2	6	UPLOAD	FACTURE	116	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-06 23:52:52.348066
89	2	6	EXTRACTION	FACTURE	116	Extraction OCR/IA réussie (N° N/A)	2026-05-06 23:55:56.190419
90	2	6	CLASSIFICATION	FACTURE	116	Classification PCM des lignes terminée	2026-05-06 23:56:57.185868
91	2	6	GENERATION_BROUILLON	FACTURE	116	Génération du brouillon d'écriture comptable	2026-05-06 23:56:57.242819
92	2	6	DELETE	FACTURE	116	Suppression de la facture 116 et de ses fichiers	2026-05-07 00:03:31.569033
93	2	6	UPLOAD	FACTURE	117	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-07 00:03:40.713171
94	2	6	EXTRACTION	FACTURE	117	Extraction OCR/IA réussie (N° N/A)	2026-05-07 00:06:44.434536
95	2	6	CLASSIFICATION	FACTURE	117	Classification PCM des lignes terminée	2026-05-07 00:07:45.506496
96	2	6	GENERATION_BROUILLON	FACTURE	117	Génération du brouillon d'écriture comptable	2026-05-07 00:07:45.541751
97	2	6	DELETE	FACTURE	117	Suppression de la facture 117 et de ses fichiers	2026-05-07 00:18:32.518604
98	2	6	UPLOAD	FACTURE	118	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-07 00:18:40.407546
99	2	6	EXTRACTION	FACTURE	118	Extraction OCR/IA réussie (N° N/A)	2026-05-07 00:19:18.184335
100	2	6	CLASSIFICATION	FACTURE	118	Classification PCM des lignes terminée	2026-05-07 00:19:23.748284
101	2	6	GENERATION_BROUILLON	FACTURE	118	Génération du brouillon d'écriture comptable	2026-05-07 00:19:23.786789
102	2	6	DELETE	FACTURE	118	Suppression de la facture 118 et de ses fichiers	2026-05-07 00:21:51.374016
103	2	6	UPLOAD	FACTURE	119	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-07 00:22:01.047785
104	2	6	EXTRACTION	FACTURE	119	Extraction OCR/IA réussie (N° N/A)	2026-05-07 00:22:31.86846
105	2	6	CLASSIFICATION	FACTURE	119	Classification PCM des lignes terminée	2026-05-07 00:22:37.197257
106	2	6	GENERATION_BROUILLON	FACTURE	119	Génération du brouillon d'écriture comptable	2026-05-07 00:22:37.331206
107	2	6	DELETE	FACTURE	119	Suppression de la facture 119 et de ses fichiers	2026-05-07 00:24:19.628965
108	2	6	UPLOAD	FACTURE	120	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-07 00:24:31.002912
109	2	6	EXTRACTION	FACTURE	120	Extraction OCR/IA réussie (N° N/A)	2026-05-07 00:24:58.056959
110	2	6	CLASSIFICATION	FACTURE	120	Classification PCM des lignes terminée	2026-05-07 00:25:03.559574
111	2	6	GENERATION_BROUILLON	FACTURE	120	Génération du brouillon d'écriture comptable	2026-05-07 00:25:03.598572
112	2	6	DELETE	FACTURE	120	Suppression de la facture 120 et de ses fichiers	2026-05-07 00:29:44.017102
113	2	6	UPLOAD	FACTURE	121	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-07 00:29:59.192866
114	2	6	EXTRACTION	FACTURE	121	Extraction OCR/IA réussie (N° N/A)	2026-05-07 00:30:29.968223
115	2	6	CLASSIFICATION	FACTURE	121	Classification PCM des lignes terminée	2026-05-07 00:30:35.365378
116	2	6	GENERATION_BROUILLON	FACTURE	121	Génération du brouillon d'écriture comptable	2026-05-07 00:30:35.512323
117	2	6	DELETE	FACTURE	121	Suppression de la facture 121 et de ses fichiers	2026-05-07 00:32:27.567668
118	2	6	UPLOAD	FACTURE	122	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-07 00:32:40.041561
119	2	6	EXTRACTION	FACTURE	122	Extraction OCR/IA réussie (N° struction)	2026-05-07 00:33:08.041179
120	2	6	CLASSIFICATION	FACTURE	122	Classification PCM des lignes terminée	2026-05-07 00:33:11.672234
121	2	6	GENERATION_BROUILLON	FACTURE	122	Génération du brouillon d'écriture comptable	2026-05-07 00:33:11.801624
122	2	6	DELETE	FACTURE	122	Suppression de la facture 122 et de ses fichiers	2026-05-07 00:35:23.186103
123	2	6	UPLOAD	FACTURE	123	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-07 00:35:33.117955
124	2	6	EXTRACTION	FACTURE	123	Extraction OCR/IA réussie (N° N/A)	2026-05-07 00:35:53.622032
125	2	6	CLASSIFICATION	FACTURE	123	Classification PCM des lignes terminée	2026-05-07 00:35:56.313439
126	2	6	GENERATION_BROUILLON	FACTURE	123	Génération du brouillon d'écriture comptable	2026-05-07 00:35:56.469174
127	2	6	DELETE	FACTURE	123	Suppression de la facture 123 et de ses fichiers	2026-05-07 00:39:05.05832
128	2	6	UPLOAD	FACTURE	124	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-07 00:39:14.522741
129	2	6	EXTRACTION	FACTURE	124	Extraction OCR/IA réussie (N° 2025-40708/12/2025146)	2026-05-07 00:39:35.050434
130	2	6	CLASSIFICATION	FACTURE	124	Classification PCM des lignes terminée	2026-05-07 00:39:37.903817
131	2	6	GENERATION_BROUILLON	FACTURE	124	Génération du brouillon d'écriture comptable	2026-05-07 00:39:38.032822
132	2	6	DELETE	FACTURE	124	Suppression de la facture 124 et de ses fichiers	2026-05-07 00:48:15.838043
133	2	6	UPLOAD	FACTURE	125	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-07 00:48:26.328518
134	2	6	EXTRACTION	FACTURE	125	Extraction OCR/IA réussie (N° 2025-40708/12/2025146)	2026-05-07 00:48:55.078907
135	2	6	CLASSIFICATION	FACTURE	125	Classification PCM des lignes terminée	2026-05-07 00:49:00.671924
136	2	6	GENERATION_BROUILLON	FACTURE	125	Génération du brouillon d'écriture comptable	2026-05-07 00:49:00.822167
137	2	6	DELETE	FACTURE	125	Suppression de la facture 125 et de ses fichiers	2026-05-07 00:55:35.215117
138	2	6	UPLOAD	FACTURE	126	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-07 00:55:44.29294
139	2	6	EXTRACTION	FACTURE	126	Extraction OCR/IA réussie (N° 2025-40708/12/2025146)	2026-05-07 00:56:12.93376
140	2	6	CLASSIFICATION	FACTURE	126	Classification PCM des lignes terminée	2026-05-07 00:56:18.321876
141	2	6	GENERATION_BROUILLON	FACTURE	126	Génération du brouillon d'écriture comptable	2026-05-07 00:56:18.45742
142	2	6	DELETE	FACTURE	126	Suppression de la facture 126 et de ses fichiers	2026-05-07 00:58:31.819982
143	2	6	UPLOAD	FACTURE	127	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-07 00:58:41.42342
144	2	6	EXTRACTION	FACTURE	127	Extraction OCR/IA réussie (N° 2025-407)	2026-05-07 00:58:54.408363
145	2	6	CLASSIFICATION	FACTURE	127	Classification PCM des lignes terminée	2026-05-07 00:59:15.644623
146	2	6	GENERATION_BROUILLON	FACTURE	127	Génération du brouillon d'écriture comptable	2026-05-07 00:59:15.697162
147	2	6	DELETE	FACTURE	127	Suppression de la facture 127 et de ses fichiers	2026-05-07 01:06:00.438297
148	2	6	UPLOAD	FACTURE	128	Import de la facture (Fichier: Facture 2025-407.pdf)	2026-05-07 01:06:09.026759
149	2	6	EXTRACTION	FACTURE	128	Extraction OCR/IA réussie (N° 2025-407)	2026-05-07 01:06:23.800112
150	2	6	CLASSIFICATION	FACTURE	128	Classification PCM des lignes terminée	2026-05-07 01:06:43.434103
151	2	6	GENERATION_BROUILLON	FACTURE	128	Génération du brouillon d'écriture comptable	2026-05-07 01:06:43.494223
152	2	6	VALIDATION	FACTURE	128	Validation finale de la facture 2025-407	2026-05-07 01:10:50.298577
153	2	6	UPLOAD	FACTURE	129	Import de la facture (Fichier: Facture 2025-411.pdf)	2026-05-07 01:17:35.494432
154	2	6	EXTRACTION	FACTURE	129	Extraction OCR/IA réussie (N° 2025-411)	2026-05-07 01:17:55.238226
155	2	6	CLASSIFICATION	FACTURE	129	Classification PCM des lignes terminée	2026-05-07 01:17:55.290398
156	2	6	GENERATION_BROUILLON	FACTURE	129	Génération du brouillon d'écriture comptable	2026-05-07 01:17:55.340149
157	2	6	VALIDATION	FACTURE	129	Validation finale de la facture 2025-411	2026-05-07 01:18:27.834702
158	2	6	UPLOAD	FACTURE	130	Import de la facture (Fichier: OPTIMA CHIMIE.pdf)	2026-05-07 01:21:12.58552
159	2	6	EXTRACTION	FACTURE	130	Extraction OCR/IA réussie (N° FA2501536)	2026-05-07 01:23:16.215756
160	2	6	CLASSIFICATION	FACTURE	130	Classification PCM des lignes terminée	2026-05-07 01:23:30.068226
161	2	6	GENERATION_BROUILLON	FACTURE	130	Génération du brouillon d'écriture comptable	2026-05-07 01:23:30.113936
162	2	6	VALIDATION	FACTURE	130	Validation finale de la facture FA2501536	2026-05-07 01:25:58.028352
163	2	6	UPLOAD	FACTURE	131	Import de la facture (Fichier: CamScanner.pdf)	2026-05-07 01:26:35.895136
164	2	6	EXTRACTION	FACTURE	131	Extraction OCR/IA réussie (N° 00005112/25)	2026-05-07 01:27:11.521673
165	2	6	CLASSIFICATION	FACTURE	131	Classification PCM des lignes terminée	2026-05-07 01:27:25.73228
166	2	6	GENERATION_BROUILLON	FACTURE	131	Génération du brouillon d'écriture comptable	2026-05-07 01:27:25.787719
167	2	6	VALIDATION	FACTURE	131	Validation finale de la facture 00005112/25	2026-05-07 01:28:12.497698
168	2	6	UPLOAD	FACTURE	132	Import de la facture (Fichier: factura.png)	2026-05-07 01:36:21.353725
169	2	6	EXTRACTION	FACTURE	132	Extraction OCR/IA réussie (N° 0042225)	2026-05-07 01:36:55.890298
170	2	6	CLASSIFICATION	FACTURE	132	Classification PCM des lignes terminée	2026-05-07 01:37:02.282286
171	2	6	GENERATION_BROUILLON	FACTURE	132	Génération du brouillon d'écriture comptable	2026-05-07 01:37:02.338542
172	2	6	UPLOAD	FACTURE	133	Import de la facture (Fichier: CamScanner 02-04-2026 08.57_14.jpg)	2026-05-07 11:40:43.142445
173	2	6	EXTRACTION	FACTURE	133	Extraction OCR/IA réussie (N° FA2026/00893)	2026-05-07 11:40:56.37781
174	2	6	CLASSIFICATION	FACTURE	133	Classification PCM des lignes terminée	2026-05-07 11:41:24.652188
175	2	6	GENERATION_BROUILLON	FACTURE	133	Génération du brouillon d'écriture comptable	2026-05-07 11:41:24.681394
176	2	6	VALIDATION	FACTURE	133	Validation finale de la facture FA2026/00893	2026-05-07 11:43:11.538654
177	2	6	UPLOAD	FACTURE	134	Import de la facture (Fichier: CamScanner 02-04-2026 08.57_19.jpg)	2026-05-07 11:43:40.348013
178	2	6	EXTRACTION	FACTURE	134	Extraction OCR/IA réussie (N° 17344)	2026-05-07 11:48:30.384285
179	2	6	CLASSIFICATION	FACTURE	134	Classification PCM des lignes terminée	2026-05-07 11:50:06.170986
180	2	6	GENERATION_BROUILLON	FACTURE	134	Génération du brouillon d'écriture comptable	2026-05-07 11:50:06.205528
181	2	6	VALIDATION	FACTURE	134	Validation finale de la facture 17344	2026-05-07 11:51:12.795241
182	2	6	UPLOAD	FACTURE	135	Import de la facture (Fichier: CamScanner 02-04-2026 08.57_20.jpg)	2026-05-07 11:52:12.302669
183	2	6	EXTRACTION	FACTURE	135	Extraction OCR/IA réussie (N° N/A)	2026-05-07 11:52:51.599064
184	2	6	CLASSIFICATION	FACTURE	135	Classification PCM des lignes terminée	2026-05-07 11:52:56.381821
185	2	6	GENERATION_BROUILLON	FACTURE	135	Génération du brouillon d'écriture comptable	2026-05-07 11:52:56.404732
186	2	6	DELETE	FACTURE	132	Suppression de la facture 132 et de ses fichiers	2026-05-07 11:56:56.499507
187	2	6	DELETE	FACTURE	135	Suppression de la facture 135 et de ses fichiers	2026-05-07 11:56:59.323516
188	2	6	UPLOAD	FACTURE	136	Import de la facture (Fichier: CamScanner 02-04-2026 08.57_20.jpg)	2026-05-07 12:06:39.155699
189	2	6	EXTRACTION	FACTURE	136	Extraction OCR/IA réussie (N° N/A)	2026-05-07 12:07:22.03933
190	2	6	CLASSIFICATION	FACTURE	136	Classification PCM des lignes terminée	2026-05-07 12:07:27.171256
191	2	6	GENERATION_BROUILLON	FACTURE	136	Génération du brouillon d'écriture comptable	2026-05-07 12:07:27.195611
192	2	6	DELETE	FACTURE	136	Suppression de la facture 136 et de ses fichiers	2026-05-07 12:11:49.497373
193	2	6	UPLOAD	FACTURE	137	Import de la facture (Fichier: CamScanner 02-04-2026 08.57_20.jpg)	2026-05-07 13:01:06.806478
194	2	6	EXTRACTION	FACTURE	137	Extraction OCR/IA réussie (N° 00000644/26)	2026-05-07 13:01:30.668918
195	2	6	CLASSIFICATION	FACTURE	137	Classification PCM des lignes terminée	2026-05-07 13:01:30.713845
196	2	6	GENERATION_BROUILLON	FACTURE	137	Génération du brouillon d'écriture comptable	2026-05-07 13:01:30.75498
197	2	6	VALIDATION	FACTURE	137	Validation finale de la facture 00000644/26	2026-05-07 13:02:12.046338
198	2	6	UPLOAD	FACTURE	138	Import de la facture (Fichier: Facture_Avoir.pdf)	2026-05-07 13:37:03.693774
199	2	6	EXTRACTION	FACTURE	138	Extraction OCR/IA réussie (N° AV2025-407-P)	2026-05-07 13:37:18.965656
200	2	6	CLASSIFICATION	FACTURE	138	Classification PCM des lignes terminée	2026-05-07 13:37:25.498474
201	2	6	GENERATION_BROUILLON	FACTURE	138	Génération du brouillon d'écriture comptable	2026-05-07 13:37:25.578596
202	2	6	DELETE	FACTURE	138	Suppression de la facture 138 et de ses fichiers	2026-05-07 13:50:53.448269
203	2	6	UPLOAD	FACTURE	139	Import de la facture (Fichier: Facture_Avoir.pdf)	2026-05-07 13:51:05.726201
204	2	6	EXTRACTION	FACTURE	139	Extraction OCR/IA réussie (N° 2025-407)	2026-05-07 13:53:35.094803
205	2	6	CLASSIFICATION	FACTURE	139	Classification PCM des lignes terminée	2026-05-07 13:53:35.124142
206	2	6	GENERATION_BROUILLON	FACTURE	139	Génération du brouillon d'écriture comptable	2026-05-07 13:53:35.152295
207	2	6	DELETE	FACTURE	139	Suppression de la facture 139 et de ses fichiers	2026-05-07 14:03:56.075232
208	2	6	UPLOAD	FACTURE	140	Import de la facture (Fichier: Facture_Avoir.pdf)	2026-05-07 14:04:02.464254
209	2	6	EXTRACTION	FACTURE	140	Extraction OCR/IA réussie (N° 2025-407)	2026-05-07 14:04:31.854665
210	2	6	CLASSIFICATION	FACTURE	140	Classification PCM des lignes terminée	2026-05-07 14:04:31.884475
211	2	6	GENERATION_BROUILLON	FACTURE	140	Génération du brouillon d'écriture comptable	2026-05-07 14:04:31.912923
212	2	6	DELETE	FACTURE	140	Suppression de la facture 140 et de ses fichiers	2026-05-07 14:09:44.404643
213	2	6	UPLOAD	FACTURE	141	Import de la facture (Fichier: Facture_Avoir.pdf)	2026-05-07 14:09:52.036533
214	2	6	EXTRACTION	FACTURE	141	Extraction OCR/IA réussie (N° 2025-407)	2026-05-07 14:13:14.453632
215	2	6	CLASSIFICATION	FACTURE	141	Classification PCM des lignes terminée	2026-05-07 14:13:14.493257
216	2	6	GENERATION_BROUILLON	FACTURE	141	Génération du brouillon d'écriture comptable	2026-05-07 14:13:14.52675
217	2	6	DELETE	FACTURE	141	Suppression de la facture 141 et de ses fichiers	2026-05-07 14:22:14.334261
218	2	6	CREATE	IMMOBILISATION	1	Création de l'immobilisation 'Bureau de direction en bois chêne'	2026-05-07 14:40:03.821365
219	2	6	GENERATION_DOTATION	IMMOBILISATION	1	Génération de la dotation aux amortissements pour l'année 2024 (Asset: Bureau de direction en bois chêne)	2026-05-07 14:40:42.422032
220	2	6	GENERATION_DOTATION	IMMOBILISATION	1	Génération de la dotation aux amortissements pour l'année 2025 (Asset: Bureau de direction en bois chêne)	2026-05-07 14:40:45.108037
221	2	6	GENERATION_DOTATION	IMMOBILISATION	1	Génération de la dotation aux amortissements pour l'année 2026 (Asset: Bureau de direction en bois chêne)	2026-05-07 14:40:48.656987
222	2	6	DELETE	ECRITURE	144	Suppression de l'écriture 144	2026-05-07 14:54:34.862536
223	2	6	DELETE	ECRITURE	143	Suppression de l'écriture 143	2026-05-07 14:54:37.844153
224	2	6	DELETE	ECRITURE	142	Suppression de l'écriture 142	2026-05-07 14:54:35.763489
225	2	6	CREATE	IMMOBILISATION	2	Création de l'immobilisation 'Bureau de direction en bois chêne'	2026-05-07 15:05:20.76072
226	2	6	GENERATION_DOTATION	IMMOBILISATION	2	Génération de la dotation aux amortissements pour l'année 2024 (Asset: Bureau de direction en bois chêne)	2026-05-07 15:05:27.334058
227	2	6	GENERATION_DOTATION	IMMOBILISATION	2	Génération de la dotation aux amortissements pour l'année 2025 (Asset: Bureau de direction en bois chêne)	2026-05-07 15:05:44.024835
228	2	6	GENERATION_DOTATION	IMMOBILISATION	2	Génération de la dotation aux amortissements pour l'année 2026 (Asset: Bureau de direction en bois chêne)	2026-05-07 15:05:45.924606
229	2	6	UPDATE_MANUAL	ECRITURE	148	Modification de l'écriture manuelle (Ref: IMMO-2)	2026-05-07 15:16:55.539818
230	2	6	UPDATE_MANUAL	ECRITURE	148	Modification de l'écriture manuelle (Ref: IMMO-2)	2026-05-07 15:40:27.03497
231	2	6	UPDATE_MANUAL	ECRITURE	148	Modification de l'écriture manuelle (Ref: IMMO-2)	2026-05-07 15:46:40.726661
232	2	6	UPDATE_MANUAL	ECRITURE	148	Modification de l'écriture manuelle (Ref: IMMO-2)	2026-05-07 15:46:59.182313
233	2	6	UPDATE_MANUAL	ECRITURE	148	Modification de l'écriture manuelle (Ref: IMMO-2)	2026-05-07 15:47:44.050229
234	2	6	UPDATE_MANUAL	ECRITURE	148	Modification de l'écriture manuelle (Ref: IMMO-2)	2026-05-07 15:58:56.687634
235	2	6	UPLOAD	FACTURE	142	Import de la facture (Fichier: Facture_Avoir.pdf)	2026-05-07 16:21:42.444412
236	2	6	EXTRACTION	FACTURE	142	Extraction OCR/IA réussie (N° AV2025-407-P)	2026-05-07 16:21:59.930719
237	2	6	CLASSIFICATION	FACTURE	142	Classification PCM des lignes terminée	2026-05-07 16:22:00.00136
238	2	6	GENERATION_BROUILLON	FACTURE	142	Génération du brouillon d'écriture comptable	2026-05-07 16:22:00.046961
239	2	6	VALIDATION	FACTURE	142	Validation finale de la facture AV2025-407-P	2026-05-07 16:23:25.413434
240	2	6	CREATE	IMMOBILISATION	3	Création de l'immobilisation 'PC Portable HP'	2026-05-07 16:31:05.189279
241	2	6	GENERATION_DOTATION	IMMOBILISATION	3	Génération de la dotation aux amortissements pour l'année 2024 (Asset: PC Portable HP)	2026-05-07 16:31:30.000522
242	2	6	GENERATION_DOTATION	IMMOBILISATION	3	Génération de la dotation aux amortissements pour l'année 2025 (Asset: PC Portable HP)	2026-05-07 16:31:31.958286
243	2	6	GENERATION_DOTATION	IMMOBILISATION	3	Génération de la dotation aux amortissements pour l'année 2026 (Asset: PC Portable HP)	2026-05-07 16:31:33.51593
244	2	6	UPDATE_MANUAL	ECRITURE	150	Modification de l'écriture manuelle (Ref: IMMO-3)	2026-05-07 16:37:34.594373
245	2	6	GENERATION_ACQUISITION	IMMOBILISATION	3	Génération/Récupération de l'écriture d'acquisition pour 'PC Portable HP'	2026-05-07 16:41:06.700647
246	2	6	GENERATION_ACQUISITION	IMMOBILISATION	3	Génération/Récupération de l'écriture d'acquisition pour 'PC Portable HP'	2026-05-07 16:41:52.011682
247	2	6	CREATE_MANUAL	ECRITURE	154	Saisie manuelle d'une écriture (Ref: PAIE/05-26/OM)	2026-05-07 19:03:33.322608
248	2	6	CREATE_MANUAL	ECRITURE	155	Saisie manuelle d'une écriture (Ref:  PAIE/04-26/AM)	2026-05-07 19:11:21.302633
249	2	6	UPLOAD	RELEVE	1	Import du relevé CamScanner 02-04-2026 08.57_11.jpg	2026-05-07 19:59:48.915549
250	2	6	GENERATION	ECRITURE_BQ	156	Génération d'écriture bancaire pour la ligne 'TAXE SUR VALEUR AJOUTEE' (Compte: 34552000)	2026-05-07 20:02:11.022461
251	2	6	GENERATION	ECRITURE_BQ	157	Génération d'écriture bancaire pour la ligne 'VIR. INSTANTANE EN FAVEUR DE OULMEKKI MO HAMED REF 260206248575 DU 20260206' (Compte: 4411)	2026-05-07 20:07:41.045134
252	2	6	GENERATION	ECRITURE_BQ	158	Génération d'écriture bancaire pour la ligne 'VERSEMENT EFFECTUE PAR ABDELKEBIR ATIFI V62229' (Compte: 3421)	2026-05-07 20:09:22.663226
253	2	6	GENERATION	ECRITURE_BQ	159	Génération d'écriture bancaire pour la ligne 'DROIT DE TIMBRE SUR VERSEMENT' (Compte: 61671)	2026-05-07 20:10:57.272098
254	2	6	GENERATION	ECRITURE_BQ	161	Génération d'écriture bancaire pour la ligne 'VERSEMENT EFFECTUE PAR ABDELKEBIR ATIFI V62229' (Compte: 3421)	2026-05-07 20:14:11.123302
255	2	6	GENERATION	ECRITURE_BQ	162	Génération d'écriture bancaire pour la ligne 'COTISATIONS CNSS' (Compte: 4443)	2026-05-07 20:14:35.796252
256	2	6	GENERATION	ECRITURE_BQ	163	Génération d'écriture bancaire pour la ligne 'DROIT DE TIMBRE SUR VERSEMENT' (Compte: 61671)	2026-05-07 20:18:09.829342
257	2	6	GENERATION	ECRITURE_BQ	164	Génération d'écriture bancaire pour la ligne 'DROIT DE TIMBRE SUR VERSEMENT' (Compte: 61671)	2026-05-07 20:18:58.492965
258	2	6	GENERATION	ECRITURE_BQ	167	Génération d'écriture bancaire pour la ligne 'EFFET N 3100642 REMIS PAR ATW EN FAVEUR DE BHF ATLAS PEINTURES' (Compte: 4411)	2026-05-07 20:19:51.428274
259	2	6	GENERATION	ECRITURE_BQ	168	Génération d'écriture bancaire pour la ligne 'VERSEMENT EFFECTUE PAR ABDELKEBIR ATIFI V62229' (Compte: 3421)	2026-05-07 20:21:28.985063
260	2	\N	CREATE	DEMANDE_ACCES	1	Nouvelle demande d'accès : abdullah fathi (STE COMPTOIRE ARRAHMA S.A.R.L)	2026-05-07 20:46:07.113757
261	2	5	UPDATE	DEMANDE_ACCES	1	Demande d'accès de abdullah fathi marquée comme traitee — Compte créé: abdullah@gmail.com	2026-05-07 20:47:12.699625
\.


--
-- Data for Name: agents; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.agents (id, cabinet_id, username, email, password_hash, nom, prenom, is_active, is_admin, is_super_admin, created_at, updated_at) FROM stdin;
1	2	wissal	wissal@expertise-cpt.ma	6e7dc04babbd98b9f4952084a4493ee2fc16d360df95c4594d91df694dc73a79$4f52f2448bb46593bf5fb62111fa7c07ccd9e62d7af6c0853c14800db9a88549	Bennani	Wissal	t	f	t	2026-05-06 12:03:59	2026-05-06 12:03:59
2	2	fatima	fatima@expertise-cpt.ma	66c5ab48caf1bf7a1036e541046d4957c446ab28b7809a93448d726ac8677bc8$11e10d3fd1df2d37fce845dabc76aed0ec400057474dc643bfe5a7a220a5a8d8	El Oujdi	Fatima	t	f	f	2026-05-06 12:03:59	2026-05-06 12:03:59
3	3	ahmed	ahmed@finances-audit.ma	5f1d9ec2c0e4e979d9186b5e8ee759cc3c9e4e4105ee50c2953c96351396e34e$0d64af04ca3d4a10b5ef55c4272447098099bd3d943432fa161db0ce9dd19eda	Ahmed	Kabil	t	t	f	2026-05-06 12:03:59	2026-05-06 12:03:59
4	2	fati	fati@expertise-cpt.ma	5c00f447519008986d98d33ef67c953382f7b45c8525ba5246ff24035c9e84e7$33e59b668892d9de5c2504b17a23d423ec90c53785ed315c796d76ec741c675f	Utilisateur	Fati	t	t	f	2026-05-06 12:09:30	2026-05-07 20:29:56.744288
5	2	mohammed	mohamed@gmail.com	133e35eb478d9690910ebf8904a5d79e5ddeb79d239df8622ba64a1922012575$4955404d1786191e0b66be74e2d9a7e02baa8e8116b4db5af1e057c6df6c0485	mohammed	mohammed	t	t	f	2026-05-06 23:29:06.641738	2026-05-06 23:29:06.641738
6	2	khadija	khadija@gmail.com	8fd63b4061a5437b553240cfbea7e6cd4c0b766035a94bb58e8357c2360c7a8d$1f504e6288ca8bd7b1a2d57f654369500d6cc990363e7d3812249c83235352a1	motawakil	khadija	t	f	f	2026-05-06 23:48:54.635699	2026-05-06 23:48:54.635699
\.


--
-- Data for Name: agents_societes; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.agents_societes (agent_id, societe_id) FROM stdin;
3	4
1	2
2	2
4	5
6	6
6	2
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.alembic_version (version_num) FROM stdin;
e913ba9622fc
\.


--
-- Data for Name: bulletins_paie; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.bulletins_paie (id, employe_id, mois, annee, salaire_base, prime_anciennete, autres_gains, salaire_brut, cnss_salarie, amo_salarie, ir_retenu, total_retenues, cnss_patronal, amo_patronal, total_patronal, salaire_net, cout_total_employeur, journal_entry_id, statut, valide_par, valide_at, created_at) FROM stdin;
1	1	3	2024	5000.00	250.00	1500.00	6750.00	268.80	152.55	269.06	690.41	638.40	265.95	904.35	6059.59	7654.35	1	VALIDE	\N	\N	2026-03-03 12:44:43
\.


--
-- Data for Name: cabinets; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.cabinets (id, nom, email, telephone, adresse, logo_path, created_at) FROM stdin;
1	Cabinet Test	\N	\N	\N	\N	2026-02-24 09:37:57
2	Cabinet Expertise Comptable	contact@expertise-cpt.ma	+212 5 24 12 34 56	123 Avenue Hassan II, Casablanca	\N	2026-05-06 12:03:58
3	Finances & Audit Maroc	info@finances-audit.ma	+212 5 37 77 88 99	45 Rue de Fès, Rabat	\N	2026-05-06 12:03:58
4	Cabinet par Défaut	admin@cabinet.ma	+212 5 24 12 34 56	Casablanca	\N	2026-05-06 23:12:08.986664
\.


--
-- Data for Name: comptes_pcm; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.comptes_pcm (code, label, pcm_class, group_code, account_type, is_tva_account, tva_type) FROM stdin;
1411	Emprunts obligataires	1	14	PASSIF	f	\N
2321	Bâtiments	2	23	ACTIF	f	\N
2340	Matériel de transport	2	23	ACTIF	f	\N
2350	Matériel de bureau et mobilier	2	23	ACTIF	f	\N
2351	Mobilier de bureau	2	23	ACTIF	f	\N
2352	Matériel de bureau	2	23	ACTIF	f	\N
2355	Matériel informatique	2	23	ACTIF	f	\N
2360	Agencements et installations	2	23	ACTIF	f	\N
2400	Immobilisations incorporelles	2	24	ACTIF	f	\N
2834	Amortissements du matériel de transport	2	28	ACTIF	f	\N
28351	Amortissements du mobilier de bureau	2	28	ACTIF	f	\N
28352	Amortissements du matériel de bureau	2	28	ACTIF	f	\N
28355	Amortissements du matériel informatique	2	28	ACTIF	f	\N
3111	Marchandises	3	31	ACTIF	f	\N
3121	Matières premières	3	31	ACTIF	f	\N
3421	Clients	3	34	TIERS	f	\N
3441	Personnel — débiteur	3	34	TIERS	f	\N
4411	Fournisseurs	4	44	TIERS	f	\N
4451	État — TVA facturée	4	44	TIERS	t	COLLECTEE
6121	Achats de matières premières	6	61	CHARGE	f	\N
6131	Locations et charges locatives	6	61	CHARGE	f	\N
6133	Entretien et réparations	6	61	CHARGE	f	\N
6143	Déplacements, missions et réceptions	6	61	CHARGE	f	\N
6144	Publicité, publications et relations publiques	6	61	CHARGE	f	\N
6145	Frais postaux et frais de télécommunications	6	61	CHARGE	f	\N
6146	Cotisations et dons	6	61	CHARGE	f	\N
6147	Services bancaires	6	61	CHARGE	f	\N
6152	Honoraires	6	61	CHARGE	f	\N
6174	Charges sociales	6	61	CHARGE	f	\N
6300	Impôts sur les résultats	6	63	CHARGE	f	\N
7121	Ventes de produits finis	7	71	PRODUIT	f	\N
7122	Ventes de produits intermédiaires	7	71	PRODUIT	f	\N
7300	Produits financiers	7	73	PRODUIT	f	\N
7500	Produits non courants	7	75	PRODUIT	f	\N
8100	Résultat d'exploitation	8	81	PRODUIT	f	\N
8200	Résultat financier	8	82	PRODUIT	f	\N
1111	Capital social	1	11	PASSIF	f	\N
1181	Résultats nets en instance d'affectation	1	11	PASSIF	f	\N
1481	Autres dettes de financement	1	14	PASSIF	f	\N
2210	Terrains	2	22	ACTIF	f	\N
2823	Amortissements des bâtiments	2	28	ACTIF	f	\N
4443	Caisses de retraite	4	44	TIERS	f	\N
2835	Amortissements du matériel de bureau et mobilier	2	28	ACTIF	f	\N
3451	État — débiteur	3	34	TIERS	f	\N
34551	TVA récupérable sur charges	3	345	TIERS	t	RECUPERABLE
6123	Achats de fournitures de bureau	6	61	CHARGE	f	\N
34552	TVA récupérable sur immobilisations	3	345	TIERS	t	IMMOBILISATION
6132	Redevances de crédit-bail	6	61	CHARGE	f	\N
6142	Transports	6	61	CHARGE	f	\N
6148	Autres charges externes	6	61	CHARGE	f	\N
6171	Rémunérations du personnel	6	61	CHARGE	f	\N
3456	Créances sur cessions d'immobilisations	3	34	TIERS	f	\N
6193	Dotations d'exploitation aux amortissements des immobilisations corporelles	6	61	CHARGE	f	\N
7161	Ventes de services	7	71	PRODUIT	f	\N
7181	Produits accessoires	7	71	PRODUIT	f	\N
4417	Fournisseurs — retenues de garantie	4	44	TIERS	f	\N
4481	Dettes sociales	4	44	TIERS	f	\N
5161	Caisse	5	51	ACTIF	f	\N
6111	Achats de marchandises revendues	6	61	CHARGE	f	\N
7127	Ventes de produits résiduels	7	71	PRODUIT	f	\N
6125	Achats de fournitures informatiques	6	61	CHARGE	f	\N
6135	Primes d'assurance	6	61	CHARGE	f	\N
6141	Études et recherches	6	61	CHARGE	f	\N
3455	Etat - TVA récupérable	3	\N	TIERS	f	\N
6134	Primes d'assurance	6	61	CHARGE	f	\N
6191	Dotations d'exploitation aux amortissements de l'immobilisation incorporelle	6	61	CHARGE	f	\N
7131	Variation des stocks de produits	7	71	PRODUIT	f	\N
3911	Provisions pour dépréciation des marchandises	3	\N	BILAN	f	\N
3461	Associés - comptes d'apport en société	3	34	TIERS	f	\N
4421	Clients - avances et acomptes reçus sur commandes en cours	4	44	TIERS	f	\N
4432	Rémunérations dues au personnel	4	44	TIERS	f	\N
6161	Impôts et taxes directs	6	61	CHARGE	f	\N
7111	Ventes de marchandises	7	71	PRODUIT	f	\N
7124	Ventes de déchets	7	71	PRODUIT	f	\N
4444	État - Impôt sur le revenu retenu à la source	4	\N	BILAN	f	\N
151	Provisions pour risques	1	\N	BILAN	f	\N
1513	Provisions pour propre assureur	1	\N	BILAN	f	\N
1514	Provision pour pertes sur marchés à terme	1	\N	BILAN	f	\N
1515	Provisions pour amendes, double droits, pénalités	1	\N	BILAN	f	\N
1516	Provisions pour pertes de change	1	\N	BILAN	f	\N
1518	Autres provisions pour risques	1	\N	BILAN	f	\N
155	Provisions pour charges	1	\N	BILAN	f	\N
1551	Provisions pour impôts	1	\N	BILAN	f	\N
1552	Provisions pour pensions de retraite et obligations similaires	1	\N	BILAN	f	\N
1558	Autres provisions pour charges	1	\N	BILAN	f	\N
160	Comptes de liaison des établissements et succursales	1	\N	BILAN	f	\N
1601	Comptes de liaison du siège	1	\N	BILAN	f	\N
1605	Comptes de liaison des établissements	1	\N	BILAN	f	\N
171	Augmentation des créances immobilisées	1	\N	BILAN	f	\N
1710	Augmentation des créances immobilisées	1	\N	BILAN	f	\N
172	Diminution des dettes de financement	1	\N	BILAN	f	\N
1720	Diminution des dettes de financement	1	\N	BILAN	f	\N
211	Frais préliminaires	2	\N	BILAN	f	\N
2112	Frais préalables au démarrage	2	\N	BILAN	f	\N
2114	Frais sur opérations de fusions, scissions et transformations	2	\N	BILAN	f	\N
2116	Frais de prospection	2	\N	BILAN	f	\N
2117	Frais de publicité	2	\N	BILAN	f	\N
2118	Autres frais préliminaires	2	\N	BILAN	f	\N
212	Charges à répartir sur plusieurs exercices	2	\N	BILAN	f	\N
2121	Frais d'acquisitition des immobilisations	2	\N	BILAN	f	\N
2125	Frais d'émission des emprunts	2	\N	BILAN	f	\N
2128	Autres charges à répartir	2	\N	BILAN	f	\N
213	Primes de remboursement des obligations	2	\N	BILAN	f	\N
2130	Primes de remboursement des obligations	2	\N	BILAN	f	\N
221	Immobilisation en recherche et développement	2	\N	BILAN	f	\N
222	Brevets, marques, droits et valeurs similaires	2	\N	BILAN	f	\N
223	Fonds commercial	2	\N	BILAN	f	\N
228	Autres immobilisations incorporelles	2	\N	BILAN	f	\N
2285	Autres immobilisations incorporelles	2	\N	BILAN	f	\N
231	Terrains	2	\N	BILAN	f	\N
2312	Terrains aménagés	2	\N	BILAN	f	\N
2313	Terrains bâtis	2	\N	BILAN	f	\N
2314	Terrains de gisement	2	\N	BILAN	f	\N
2316	Agencements et aménagements de terrains	2	\N	BILAN	f	\N
2318	Autres terrains	2	\N	BILAN	f	\N
232	Constructions	2	\N	BILAN	f	\N
23211	Bâtiments industriels	2	\N	BILAN	f	\N
23214	Bâtiments administratifs et commerciaux	2	\N	BILAN	f	\N
23218	Autres bâtiments	2	\N	BILAN	f	\N
2323	Constructions sur terrains d'autrui	2	\N	BILAN	f	\N
2325	Ouvrages d'infrastructure	2	\N	BILAN	f	\N
2327	Agencements et aménagements des constructions	2	\N	BILAN	f	\N
2328	Autres constructions	2	\N	BILAN	f	\N
233	Installations techniques, matériel et outillage	2	\N	BILAN	f	\N
23321	Matériel	2	\N	BILAN	f	\N
23324	Outillage	2	\N	BILAN	f	\N
2333	Emballages récupérables identifiables	2	\N	BILAN	f	\N
2338	Autres installations techniques, matériel et outillage	2	\N	BILAN	f	\N
234	Matériel de transport	2	\N	BILAN	f	\N
235	Mobilier, matériel de bureau et aménagements divers	2	\N	BILAN	f	\N
238	Autres immobilisations corporelles	2	\N	BILAN	f	\N
239	Immobilisations corporelles en cours	2	\N	BILAN	f	\N
2392	Immobilisations corporelles en cours des terrains et constructions	2	\N	BILAN	f	\N
2393	Immobilisations corporelles en cours des installations techniques, matériel et outillage	2	\N	BILAN	f	\N
2394	Immobilisations corporelles en cours de matériel de transport	2	\N	BILAN	f	\N
2395	Immobilisations corporelles en cours de mobilier, matériel de bureau et aménagements divers	2	\N	BILAN	f	\N
2397	Avances et acomptes versés sur commandes d'immobilisations corporelles	2	\N	BILAN	f	\N
2398	Autres immobilisations corporelles en cours	2	\N	BILAN	f	\N
241	Prêts immobilsés	2	\N	BILAN	f	\N
2441	Prêts au personnel	2	\N	BILAN	f	\N
2415	Prêts aux associés	2	\N	BILAN	f	\N
2416	Billets de fonds	2	\N	BILAN	f	\N
2418	Autres prêts	2	\N	BILAN	f	\N
248	Autres créances financières	2	\N	BILAN	f	\N
24811	Obligations	2	\N	BILAN	f	\N
24813	Bons d'équipement	2	\N	BILAN	f	\N
24818	Bons divers	2	\N	BILAN	f	\N
24861	Dépôts	2	\N	BILAN	f	\N
24864	Cautionnements	2	\N	BILAN	f	\N
2487	Créances immobilisées	2	\N	BILAN	f	\N
2488	Créances financères diverses	2	\N	BILAN	f	\N
251	Titres de participation	2	\N	BILAN	f	\N
258	Autres titres immobilisés	2	\N	BILAN	f	\N
2581	Actions	2	\N	BILAN	f	\N
2588	Titres divers	2	\N	BILAN	f	\N
271	Diminution des créances immobilisées	2	\N	BILAN	f	\N
272	Augmentation des dettes de financement	2	\N	BILAN	f	\N
2720	Augmentation des dettes de financement	2	\N	BILAN	f	\N
281	Amortissements des non-valeurs	2	\N	BILAN	f	\N
28111	Amortissements des frais de constitution	2	\N	BILAN	f	\N
28112	Amortissements des frais préliminaires au démarrage	2	\N	BILAN	f	\N
28113	Amortissements des frais d'augmentation du capital	2	\N	BILAN	f	\N
28114	Amortissements des frais sur opérations de fusions, scissions, et transformations	2	\N	BILAN	f	\N
28116	Amortissements des frais de prospection	2	\N	BILAN	f	\N
28117	Amortissements des frais de publicité	2	\N	BILAN	f	\N
28118	Amortissements des autres frais préliminaires	2	\N	BILAN	f	\N
2812	Amortissements des charges à répartir	2	\N	BILAN	f	\N
28121	Amortissements des frais d'acquisition des immobilisations	2	\N	BILAN	f	\N
28125	Amortissements des frais d'émission des emprunts	2	\N	BILAN	f	\N
28128	Amortissements des autres charges à répartir	2	\N	BILAN	f	\N
2813	Amortissements des primes de remboursement des obligations	2	\N	BILAN	f	\N
4441	Associés — dividendes à payer	4	44	TIERS	f	\N
4455	TVA facturée	4	44	TIERS	t	COLLECTEE
2220	Brevets, marques, droits et valeurs similaires	2	22	ACTIF	f	\N
4456	État — autres impôts et taxes	4	44	TIERS	f	\N
5141	Banques — soldes débiteurs	5	51	ACTIF	f	\N
2111	Frais de constitution	2	21	ACTIF	f	\N
6124	Achats de fournitures d'atelier	6	61	CHARGE	f	\N
1117	Capital personnel	1	11	BILAN	f	\N
1119	Actionnaires, capital souscrit-non appelé	1	11	BILAN	f	\N
1140	Réserve légale	1	11	BILAN	f	\N
1151	Réserves statutaires ou contractuelles	1	11	BILAN	f	\N
1191	Résultat net de l'exercice (solde créditeur)	1	11	BILAN	f	\N
1199	Résultat net de l'exercice (solde débiteur)	1	11	BILAN	f	\N
1486	Fournisseurs d'immobilisation	1	14	BILAN	f	\N
1555	Provisions pour charges à répartir sur plusieurs exercices	1	15	BILAN	f	\N
2113	Frais d'augmentation du capital	2	21	BILAN	f	\N
2230	Fonds commercial	2	22	BILAN	f	\N
2311	Terrains nus	2	23	BILAN	f	\N
2358	Autres mobilier, matériel de bureau et aménagements divers	2	23	BILAN	f	\N
2380	Autres immobilisations corporelles	2	23	BILAN	f	\N
2481	Titres immobilisés (droits de créance)	2	24	BILAN	f	\N
4413	Fournisseurs - retenues de garantie	4	44	TIERS	f	\N
4415	Fournisseurs - effets à payer	4	44	TIERS	f	\N
4452	Etat - Impôts, taxes et assimilés	4	44	TIERS	f	\N
4463	Comptes courants des associés créditeurs	4	44	TIERS	f	\N
5541	Banques (solde créditeur)	5	55	BILAN	f	\N
6114	Variation de stocks de marchandises	6	61	CHARGE	f	\N
6119	Rabais, remises et ristournes obtenus sur achats de marchandises	6	61	CHARGE	f	\N
7113	Ventes de marchandises à l’étranger	7	71	PRODUIT	f	\N
111	Capital social ou personnel	1	\N	BILAN	f	\N
1112	Fonds de dotation	1	\N	BILAN	f	\N
11171	Capital individuel	1	\N	BILAN	f	\N
11175	Compte de l'exploitant	1	\N	BILAN	f	\N
112	Primes d'émission, de fusion et d'apport	1	\N	BILAN	f	\N
1122	Primes de fusion	1	\N	BILAN	f	\N
1123	Primes d'apport	1	\N	BILAN	f	\N
113	Ecarts de réévaluation	1	\N	BILAN	f	\N
1130	Ecarts de réévaluation	1	\N	BILAN	f	\N
114	Réserve légale	1	\N	BILAN	f	\N
115	Autres réserves	1	\N	BILAN	f	\N
1152	Réserves facultatives	1	\N	BILAN	f	\N
1155	Réserves réglementées	1	\N	BILAN	f	\N
116	Report à nouveau	1	\N	BILAN	f	\N
118	Résultats nets en instance d'affectation	1	\N	BILAN	f	\N
1189	Résultats nets en instance d'affectation (solde débiteur)	1	\N	BILAN	f	\N
119	Résultat net de l'exercice	1	\N	BILAN	f	\N
131	Subventions d'investissement	1	\N	BILAN	f	\N
1319	Subventions d'investissement inscrites au CPC	1	\N	BILAN	f	\N
135	Provisions réglementées	1	\N	BILAN	f	\N
1351	Provisions pour amortissements dérogatoires	1	\N	BILAN	f	\N
1352	Provisions pour plus-values en instance d'imposition	1	\N	BILAN	f	\N
1354	Provisions pour investissements	1	\N	BILAN	f	\N
1355	Provisions pour reconstitution des gisements	1	\N	BILAN	f	\N
1356	Provisions pour acquisition et construction de logements	1	\N	BILAN	f	\N
1358	Autres provisions réglementées	1	\N	BILAN	f	\N
141	Emprunts obligataires	1	\N	BILAN	f	\N
1410	Emprunts obligataires	1	\N	BILAN	f	\N
148	Autres dettes de financement	1	\N	BILAN	f	\N
1483	Dettes rattachées à des participations	1	\N	BILAN	f	\N
1484	Billets de fonds	1	\N	BILAN	f	\N
8800	Résultat net de l'exercice	8	88	PRODUIT	f	\N
1121	Primes d'émission	1	11	PASSIF	f	\N
1131	Réserve légale	1	11	PASSIF	f	\N
1161	Report à nouveau (solde créditeur)	1	11	PASSIF	f	\N
1169	Report à nouveau (solde débiteur)	1	11	PASSIF	f	\N
1311	Subventions d'investissement reçues	1	13	PASSIF	f	\N
1482	Avances de l'Etat	1	14	PASSIF	f	\N
1511	Provisions pour litiges	1	15	PASSIF	f	\N
1512	Provisions pour garanties données aux clients	1	15	PASSIF	f	\N
2331	Installations techniques	2	23	ACTIF	f	\N
2332	Matériel et outillage	2	23	ACTIF	f	\N
2356	Agencements, installations et aménagements divers	2	23	ACTIF	f	\N
2411	Titres de participation	2	24	ACTIF	f	\N
1485	Avances reçues et comptes courants bloqués	1	\N	BILAN	f	\N
1487	Dépôts et cautionnements reçues	1	\N	BILAN	f	\N
1488	Dettes de financement diverses	1	\N	BILAN	f	\N
6181	Dotations d'exploitation aux amortissements des immobilisations incorporelles	6	61	CHARGE	f	\N
2510	Titres de participation	2	25	ACTIF	f	\N
3122	Matières et fournitures consommables	3	31	ACTIF	f	\N
3123	Emballages	3	31	ACTIF	f	\N
3131	Produits en cours	3	31	ACTIF	f	\N
3151	Produits finis	3	31	ACTIF	f	\N
3424	Clients - Créances douteuses ou litigieuses	3	34	TIERS	f	\N
3427	Clients - Factures à établir	3	34	TIERS	f	\N
3431	Avances et acomptes au personnel	3	34	TIERS	f	\N
3453	Acomptes sur impôts sur les résultats	3	34	TIERS	f	\N
3458	Etat - Autres comptes débiteurs	3	34	TIERS	f	\N
3481	Créances sur cessions d'immobilisations	3	34	TIERS	f	\N
3482	Créances sur cessions de titres et valeurs de placement	3	34	TIERS	f	\N
3487	Débiteurs divers	3	34	TIERS	f	\N
3491	Charges constatées d'avance	3	34	ACTIF	f	\N
3500	Titres et valeurs de placement	3	35	ACTIF	f	\N
4433	Dépôts du personnel créditeurs	4	44	TIERS	f	\N
4434	Oppositions sur salaires	4	44	TIERS	f	\N
4445	Mutuelles	4	44	TIERS	f	\N
4448	Autres organismes sociaux	4	44	TIERS	f	\N
4458	Etat - Comptes créditeurs	4	44	TIERS	f	\N
4461	Associés - Comptes courants créditeurs	4	44	TIERS	f	\N
4465	Associés - Dividendes à payer	4	44	TIERS	f	\N
4483	Dettes sur acquisitions de titres et valeurs de placement	4	44	TIERS	f	\N
4487	Créditeurs divers	4	44	TIERS	f	\N
4491	Produits constatés d'avance	4	44	PASSIF	f	\N
5111	Chèques à encaisser ou à l'encaissement	5	51	ACTIF	f	\N
5113	Effets à encaisser ou à l'encaissement	5	51	ACTIF	f	\N
5115	Virements à l'encaissement	5	51	ACTIF	f	\N
5146	CCP (soldes débiteurs)	5	51	ACTIF	f	\N
5900	Virements internes	5	59	ACTIF	f	\N
6112	Achats de marchandises (groupe B)	6	61	CHARGE	f	\N
6118	Achats de marchandises des exercices précédents	6	61	CHARGE	f	\N
6122	Achats de matières et fournitures consommables	6	61	CHARGE	f	\N
6126	Achats de fournitures de bureau	6	61	CHARGE	f	\N
6128	Achats de matières et fournitures des exercices précédents	6	61	CHARGE	f	\N
6129	R.R.R obtenus sur achats de matières et fournitures	6	61	CHARGE	f	\N
6136	Frais d'actes et de contentieux	6	61	CHARGE	f	\N
6149	R.R.R obtenus sur autres charges externes	6	61	CHARGE	f	\N
6151	Impôts et taxes directs	6	61	CHARGE	f	\N
6155	Taxes sur le chiffre d'affaires	6	61	CHARGE	f	\N
6167	Taxes sur les véhicules	6	61	CHARGE	f	\N
6176	Prévoyance sociale	6	61	CHARGE	f	\N
6177	Autres charges sociales	6	61	CHARGE	f	\N
6311	Intérêts des emprunts et dettes	6	63	CHARGE	f	\N
6331	Pertes de change	6	63	CHARGE	f	\N
6385	Charges nettes sur cessions de titres	6	63	CHARGE	f	\N
6513	Valeurs nettes d'amortissements des immo corporelles cédées	6	65	CHARGE	f	\N
6581	Pénalités et amendes	6	65	CHARGE	f	\N
6701	Impôts sur les résultats	6	67	CHARGE	f	\N
7118	Ventes de marchandises des exercices précédents	7	71	PRODUIT	f	\N
7119	R.R.R accordés par l'entreprise	7	71	PRODUIT	f	\N
7125	Ventes de services produits à l'étranger	7	71	PRODUIT	f	\N
7126	Redevances pour brevets, marques, droits et valeurs	7	71	PRODUIT	f	\N
7128	Ventes de produits et services des exercices précédents	7	71	PRODUIT	f	\N
7129	R.R.R accordés sur ventes de produits	7	71	PRODUIT	f	\N
7132	Variations des stocks de produits finis	7	71	PRODUIT	f	\N
7140	Immobilisations produites par l'entreprise pour elle-même	7	71	PRODUIT	f	\N
7182	Revenus des immeubles non destinés à l'exploitation	7	71	PRODUIT	f	\N
7191	Reprises sur amortissements de l'actif immobilisé	7	71	PRODUIT	f	\N
7311	Produits des titres de participation	7	73	PRODUIT	f	\N
7331	Gains de change	7	73	PRODUIT	f	\N
7381	Intérêts et produits assimilés	7	73	PRODUIT	f	\N
7510	Produits des cessions d'immobilisations	7	75	PRODUIT	f	\N
7561	Libéralités reçues	7	75	PRODUIT	f	\N
7581	Indemnités d'assurances reçues	7	75	PRODUIT	f	\N
2483	Créances rattachées à des participations	2	24	BILAN	f	\N
4447	Charges sociales à payer	4	44	TIERS	f	\N
4457	État - autres impôts, taxes et versements assimilés	4	44	TIERS	f	\N
3425	Clients - effets à recevoir	3	34	TIERS	f	\N
4418	Fournisseurs - factures non parvenues	4	44	TIERS	f	\N
4453	État - impôt sur le revenu (retenu à la source)	4	44	TIERS	f	\N
2486	Dépôts et cautionnements versés	2	24	BILAN	f	\N
2710	Diminution des créances immobilisées	2	27	BILAN	f	\N
2811	Amortissements des frais préliminaires	2	28	BILAN	f	\N
2832	Amortissements des constructions	2	28	BILAN	f	\N
2833	Amortissements des installations techniques, matériel et outillage	2	28	BILAN	f	\N
3411	Fournisseurs - avances et acomptes versés sur commandes d'exploitation	3	34	TIERS	f	\N
2821	Amortissements de l'immobilisation en recherche et développement	2	\N	BILAN	f	\N
2822	Amortissements des brevets, marques, droits et valeurs similaires	2	\N	BILAN	f	\N
2828	Amortissements des autres immobilisations incorporelles	2	\N	BILAN	f	\N
2831	Amortissements des terrains	2	\N	BILAN	f	\N
28311	Amortissements des terrains nus	2	\N	BILAN	f	\N
28312	Amortissements des terrains aménagés	2	\N	BILAN	f	\N
28313	Amortissements des terrains bâtis	2	\N	BILAN	f	\N
28314	Amortissements des terrains de gisement	2	\N	BILAN	f	\N
28316	Amortissements des agencements et aménagements de terrains	2	\N	BILAN	f	\N
28318	Amortissements des autres terrains	2	\N	BILAN	f	\N
28321	Amortissements des bâtiments	2	\N	BILAN	f	\N
28323	Amortissements des constructions sur terrains d'autrui	2	\N	BILAN	f	\N
28325	Amortissements des ouvrages d'infrastructure	2	\N	BILAN	f	\N
28327	Amortissements des installations, agencements et aménagements des constructions	2	\N	BILAN	f	\N
28328	Amortissements des autres constructions	2	\N	BILAN	f	\N
28331	Amortissements des installations techniques	2	\N	BILAN	f	\N
28332	Amortissements du matériel et outillage	2	\N	BILAN	f	\N
28333	Amortissements des emballages récupérables identifiables	2	\N	BILAN	f	\N
28338	Amortissements des autres installations techniques, matériel et outillage	2	\N	BILAN	f	\N
28356	Amortissements des agencements, installations et aménagements divers	2	\N	BILAN	f	\N
28358	Amortissements des autres mobilier, matériel de bureau et aménagements divers	2	\N	BILAN	f	\N
2838	Amortissements des autres immobilisations corporelles	2	\N	BILAN	f	\N
2920	Provisions pour dépréciation des immobilisations incorporelles	2	\N	BILAN	f	\N
2930	Provisions pour dépréciation des immobilisations corporelles	2	\N	BILAN	f	\N
2941	Provisions pour dépréciation des prêts immobilisés	2	\N	BILAN	f	\N
2948	Provisions pour dépréciation des autres créances financières	2	\N	BILAN	f	\N
2951	Provisions pour dépréciation des titres de participation	2	\N	BILAN	f	\N
2958	Provisions pour dépréciation des autres titres immobilisés	2	\N	BILAN	f	\N
31227	Fournitures de bureau	3	\N	TIERS	f	\N
3463	Comptes courants des associés débiteurs	3	\N	TIERS	f	\N
3501	Actions, partie libérée	3	\N	TIERS	f	\N
3504	Obligations	3	\N	TIERS	f	\N
44525	Etat - IGR	4	\N	TIERS	f	\N
61251	Achats de fournitures non stockables (eau, électricité)	6	\N	CHARGE	f	\N
61252	Achats de fournitures d'entretien	6	\N	CHARGE	f	\N
61254	Achats de fournitures de bureau	6	\N	CHARGE	f	\N
61311	Locations de terrains	6	\N	CHARGE	f	\N
61312	Locations de constructions	6	\N	CHARGE	f	\N
61313	Locations de matériel et d'outillage	6	\N	CHARGE	f	\N
61331	Entretien et réparations des biens immobiliers	6	\N	CHARGE	f	\N
61341	Assurances multirisque	6	\N	CHARGE	f	\N
61361	Commissions et courtages	6	\N	CHARGE	f	\N
61365	Honoraires	6	\N	CHARGE	f	\N
61411	Etudes générales	6	\N	CHARGE	f	\N
61421	Transports du personnel	6	\N	CHARGE	f	\N
61431	Voyages et déplacements	6	\N	CHARGE	f	\N
61441	Annonces et insertions	6	\N	CHARGE	f	\N
61455	Frais de téléphone	6	\N	CHARGE	f	\N
61473	Frais et commisions sur services bancaires	6	\N	CHARGE	f	\N
61612	Patente	6	\N	CHARGE	f	\N
61671	Droits d’enregistrement et de timbre	6	\N	CHARGE	f	\N
61711	Appointements et salaires	6	\N	CHARGE	f	\N
61741	Cotisations de sécurité sociale	6	\N	CHARGE	f	\N
61742	Cotisations aux caisses de retraite	6	\N	CHARGE	f	\N
61743	Cotisations aux mutuelles	6	\N	CHARGE	f	\N
61933	D.E.A. des installations techniques, matériel et outillage	6	\N	CHARGE	f	\N
61934	D.E.A. du matériel de transport	6	\N	CHARGE	f	\N
61935	D.E.A. des mobiliers, matériels de bureau et aménagements divers	6	\N	CHARGE	f	\N
71211	Ventes de produits finis	7	\N	PRODUIT	f	\N
71243	Prestations de services	7	\N	PRODUIT	f	\N
\.


--
-- Data for Name: compteurs_facturation; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.compteurs_facturation (id, societe_id, annee, dernier_numero, created_at, updated_at) FROM stdin;
1	2	2026	0	2026-05-06 12:03:59	2026-05-06 12:03:59
3	4	2026	0	2026-05-06 12:03:59	2026-05-06 12:03:59
4	6	2026	0	2026-05-06 23:45:03.688116	2026-05-06 23:45:03.688116
\.


--
-- Data for Name: demandes_acces; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.demandes_acces (id, cabinet_id, nom_complet, entreprise, email, telephone, message, statut, created_at, updated_at) FROM stdin;
1	2	abdullah fathi	STE COMPTOIRE ARRAHMA S.A.R.L	abdullah@gmail.com	0693000000	je veux l'accès	traitee	2026-05-07 20:46:07.098289	2026-05-07 20:47:12.658082
\.


--
-- Data for Name: documents_transmis; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.documents_transmis (id, societe_id, client_id, file_path, file_name, type_document, statut, notes_client, date_upload, date_traitement, facture_id) FROM stdin;
1	6	1	uploads/transmission/doc_3a10c460.pdf	OPTIMA CHIMIE.pdf	FACTURE_ACHAT	A_TRAITER	\N	2026-05-07 20:50:28.563507	\N	\N
\.


--
-- Data for Name: ecritures_journal; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.ecritures_journal (id, societe_id, facture_id, journal_code, entry_date, reference, description, is_validated, validated_by, validated_at, total_debit, total_credit, created_at) FROM stdin;
149	6	142	VTE	2026-05-07	AV2025-407-P	Facture AV2025-407-P — STE SHEMADRI	t	khadija	2026-05-07 16:23:25.404238	960.00	960.00	2026-05-07 16:22:00.025402
128	6	128	VTE	2025-12-08	2025-407	Facture 2025-407 — STE SHEMADRI	t	khadija	2026-05-07 01:10:50.252782	4848.00	4848.00	2026-05-07 01:06:43.467928
129	6	129	VTE	2025-12-10	2025-411	Facture 2025-411 — STE SHEMADRI	t	khadija	2026-05-07 01:18:27.80071	4955.40	4955.40	2026-05-07 01:17:55.309479
130	6	130	ACH	2025-05-21	FA2501536	Facture FA2501536 — OPTIMA CHIMIE	t	khadija	2026-05-07 01:25:57.989432	9500.00	9500.00	2026-05-07 01:23:30.094712
131	6	131	ACH	2025-11-17	00005112/25	Facture 00005112/25 — Ets. EL OUJDI & FILS	t	khadija	2026-05-07 01:28:12.46104	6000.00	6000.00	2026-05-07 01:27:25.757085
151	6	\N	IMMO	2024-12-31	DOT-3-2024	Dotation amortissement 2024 — PC Portable HP	t	\N	\N	1700.00	1700.00	2026-05-07 16:31:29.985447
133	6	133	ACH	2026-02-12	FA2026/00893	Facture FA2026/00893 — SEMACDO	t	khadija	2026-05-07 11:43:11.528892	5600.00	5600.00	2026-05-07 11:41:24.66424
152	6	\N	IMMO	2025-12-31	DOT-3-2025	Dotation amortissement 2025 — PC Portable HP	t	\N	\N	1700.00	1700.00	2026-05-07 16:31:31.925173
134	6	134	ACH	2026-02-13	17344	Facture 17344 — STE LABSELEC s.a.r.l	t	khadija	2026-05-07 11:51:12.789364	8900.00	8900.00	2026-05-07 11:50:06.185508
137	6	137	ACH	2026-02-13	00000644/26	Facture 00000644/26 — Ets. EL OUJDI & FILS	t	khadija	2026-05-07 13:02:12.026375	4300.00	4300.00	2026-05-07 13:01:30.726551
153	6	\N	IMMO	2026-12-31	DOT-3-2026	Dotation amortissement 2026 — PC Portable HP	t	\N	\N	1700.00	1700.00	2026-05-07 16:31:33.483259
1	1	\N	PAYE	2024-03-28	PAIE-1-03/2024	Bulletin de paie 03/2024 — Driss EL OMARI	f	\N	\N	7654.35	7654.35	2026-03-03 12:44:43
150	6	\N	IMMO	2024-05-15	IMMO-3	Acquisition immobilisation : PC Portable HP	t	\N	\N	10200.00	10200.00	2026-05-07 16:31:05.172215
154	6	\N	PAYE	2026-05-07	PAIE/05-26/OM	Salaire Avril 2026 — Oumayma Merzak	t	\N	\N	8500.00	8500.00	2026-05-07 19:03:33.26001
155	6	\N	PAYE	2026-05-07	 PAIE/04-26/AM	Salaire Avril 2026 — Moujahid Abbes	t	\N	\N	6700.00	6700.00	2026-05-07 19:11:21.288782
145	6	\N	IMMO	2024-12-31	DOT-2-2024	Dotation amortissement 2024 — Bureau de direction en bois chêne	t	\N	\N	450.00	450.00	2026-05-07 15:05:27.314699
146	6	\N	IMMO	2025-12-31	DOT-2-2025	Dotation amortissement 2025 — Bureau de direction en bois chêne	t	\N	\N	450.00	450.00	2026-05-07 15:05:44.013793
147	6	\N	IMMO	2026-12-31	DOT-2-2026	Dotation amortissement 2026 — Bureau de direction en bois chêne	t	\N	\N	450.00	450.00	2026-05-07 15:05:45.886844
148	6	\N	IMMO	2024-06-01	IMMO-2	Acquisition immobilisation : Bureau de direction en bois chêne	t	\N	\N	5400.00	5400.00	2026-05-07 15:11:30.846215
156	6	\N	BQ1	2026-02-06	248575	Rapprochement : TAXE SUR VALEUR AJOUTEE - RELEVÉ N°1 02/2026	t	\N	\N	3.50	3.50	2026-05-07 20:02:11.008301
157	6	\N	BQ1	2026-02-06	248575	Rapprochement : VIR. INSTANTANE EN FAVEUR DE OULMEKKI MO HAMED REF 260206248575 DU 20260206 - RELEVÉ N°1 02/2026	t	\N	\N	6000.00	6000.00	2026-05-07 20:07:41.026803
158	6	\N	BQ1	2026-02-06	7XG2P1	Rapprochement : VERSEMENT EFFECTUE PAR ABDELKEBIR ATIFI V62229 - RELEVÉ N°1 02/2026	t	\N	\N	16500.00	16500.00	2026-05-07 20:09:22.650011
159	6	\N	BQ1	2026-02-10	10P6VN	Rapprochement : DROIT DE TIMBRE SUR VERSEMENT - RELEVÉ N°1 02/2026	t	\N	\N	1.00	1.00	2026-05-07 20:10:57.255626
160	6	\N	BQ1	2026-02-10	100627	Rapprochement : EFFET N 3100627 REMIS PAR ATW EN FAVEUR DE SEMACDO SARL - RELEVÉ N°1 02/2026	t	\N	\N	5600.00	5600.00	2026-05-07 20:11:15.714988
161	6	\N	BQ1	2026-02-10	10P6VN	Rapprochement : VERSEMENT EFFECTUE PAR ABDELKEBIR ATIFI V62229 - RELEVÉ N°1 02/2026	t	\N	\N	7400.00	7400.00	2026-05-07 20:14:11.105126
162	6	\N	BQ1	2026-02-11	260211	Rapprochement : COTISATIONS CNSS - RELEVÉ N°1 02/2026	t	\N	\N	1910.24	1910.24	2026-05-07 20:14:35.784403
163	6	\N	BQ1	2026-02-12	3T5R1R	Rapprochement : DROIT DE TIMBRE SUR VERSEMENT - RELEVÉ N°1 02/2026	t	\N	\N	1.00	1.00	2026-05-07 20:18:09.815161
164	6	\N	BQ1	2026-02-16	7F07ZB	Rapprochement : DROIT DE TIMBRE SUR VERSEMENT - RELEVÉ N°1 02/2026	t	\N	\N	1.00	1.00	2026-05-07 20:18:58.475834
165	6	\N	BQ1	2026-02-16	100651	Rapprochement : PAIEMENT EFFET N 3100651 EN FAVEUR DE ME BANQUE POPULAIRE - RELEVÉ N°1 02/2026	t	\N	\N	4300.00	4300.00	2026-05-07 20:19:09.665011
166	6	\N	BQ1	2026-02-16	600247	Rapprochement : EFFET N 2600247 REMIS PAR ATW EN FAVEUR DE LAB SELEC SARL - RELEVÉ N°1 02/2026	t	\N	\N	8900.00	8900.00	2026-05-07 20:19:13.382796
167	6	\N	BQ1	2026-02-12	100642	Rapprochement : EFFET N 3100642 REMIS PAR ATW EN FAVEUR DE BHF ATLAS PEINTURES - RELEVÉ N°1 02/2026	t	\N	\N	16500.00	16500.00	2026-05-07 20:19:51.41208
168	6	\N	BQ1	2026-02-12	3T5R1R	Rapprochement : VERSEMENT EFFECTUE PAR ABDELKEBIR ATIFI V62229 - RELEVÉ N°1 02/2026	t	\N	\N	16500.00	16500.00	2026-05-07 20:21:28.968418
\.


--
-- Data for Name: employes; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.employes (id, societe_id, nom, prenom, cin, date_naissance, poste, date_embauche, type_contrat, salaire_base, nb_enfants, anciennete_pct, numero_cnss, affiliee_cnss, statut, created_at, updated_at, matricule, situation_familiale, adresse, departement, numero_mutuelle, numero_retraite) FROM stdin;
1	1	EL OMARI	Driss	\N	\N	\N	2020-01-01	CDI	5000.00	2	5.00	\N	t	ACTIF	2026-03-03 12:33:57	2026-03-03 12:33:57	\N	\N	\N	\N	\N	\N
2	6	kibali	sohayb	v370012	2000-02-01	`Comptable	2020-09-05	CDI	4300.00	0	0.00	12345678	t	ACTIF	2026-05-07 17:49:11.725014	2026-05-07 17:49:11.725014	\N	\N	\N	\N	\N	\N
3	6	moujahid	Abbes	v734756	1990-03-11	Chef de projet	2019-01-15	CDI	6700.00	0	0.00	56473829	t	ACTIF	2026-05-07 17:52:32.944955	2026-05-07 17:52:32.944955	\N	\N	\N	\N	\N	\N
4	6	merzak	oumayma	V169567	1996-09-01	Développeuse informatique 	2025-09-06	CDI	8500.00	0	0.00	67098634	t	ACTIF	2026-05-07 18:07:17.836544	2026-05-07 18:07:17.836544	\N	\N	\N	\N	\N	\N
\.


--
-- Data for Name: factures; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.factures (id, societe_id, numero_facture, date_facture, due_date, invoice_type, supplier_name, supplier_ice, supplier_if, supplier_rc, supplier_address, client_name, client_ice, client_if, client_address, montant_ht, montant_tva, montant_ttc, taux_tva, devise, payment_mode, payment_terms, ocr_confidence, extraction_source, dgi_flags, status, validated_by, validated_at, reject_reason, file_path, file_hash, fournisseur, operation_type, operation_confidence, if_frs, ice_frs, designation, id_paie, date_paie, created_at, updated_at, ded_file_path, ded_pdf_path, ded_xlsx_path) FROM stdin;
1	1	FAC-001	2026-02-24	\N	\N	Fournisseur Telecom	999888777	\N	\N	\N	\N	\N	\N	\N	\N	\N	120.00	\N	MAD	\N	\N	\N	\N	\N	VALIDATED	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-02-24 09:37:57	2026-02-24 09:37:57	\N	\N	\N
2	1	\N	\N	\N	\N	Fournisseur Telecom (Bis)	999888777	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	MAD	\N	\N	\N	\N	\N	EXTRACTED	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-02-24 09:37:57	\N	\N	\N	\N
3	1	\N	2026-01-01	\N	\N	\N	123456789012345	\N	\N	\N	\N	\N	\N	\N	\N	\N	1200.50	\N	MAD	\N	\N	\N	\N	\N	EXTRACTED	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-02-24 12:28:37	\N	\N	\N	\N
142	6	AV2025-407-P	2026-05-07	\N	AVOIR_VENTE	STE Comptoire Arrahma S.A.R.L	002012861000010	25005226	2613	Tamoument 2 N° 17 Avenue La marche Verte - KHENIFRA	STE SHEMADRI	003272689000032	\N	\N	-800.00	-160.00	-960.00	20.00	MAD	\N	\N	\N	GEMINI	[]	VALIDATED	khadija	2026-05-07 16:23:25.404238	\N	/app/uploads/efea47d8-1e9c-4d72-a9ba-59a2368c562a.pdf	d20f53122e23ff7303d4ba421ae664dd9d1273ab187ed07af86341db944036b5	STE Comptoire Arrahma S.A.R.L	avoir_vente	0.9	25005226	002012861000010	\N	\N	\N	2026-05-07 16:21:42.424824	2026-05-07 16:23:25.400475	\N	\N	\N
131	6	00005112/25	2025-11-17	\N	ACHAT	Ets. EL OUJDI & FILS	000086358000020	04100551	18581	Route de Fès 50080 Meknès	STE COMPTOIRE ARRAHMA	002012861000010	\N	\N	5000.00	1000.00	6000.00	20.00	MAD	CHEQUE	\N	\N	GEMINI	[]	VALIDATED	khadija	2026-05-07 01:28:12.46104	\N	/app/uploads/c06460f1-f214-46fe-a729-399941dfc57f.pdf	bcaf23e8009605eebc3b2b3c5fa59258ec380bfc89544c092330ed0cdeef8288	Ets. EL OUJDI & FILS	achat	0.9	04100551	000086358000020	\N	\N	\N	2026-05-07 01:26:35.861043	2026-05-07 01:28:12.458176	\N	\N	\N
133	6	FA2026/00893	2026-02-12	\N	ACHAT	SEMACDO	001535246000047	04501311	18777	N°23, Av Abdel Aziz Boutaleb - Fes	STE COMPTOIRE ARRAHMA SARL	002012861000010	\N	N 17 BD LA MARCHE VERTE KHENIFRA	4666.67	933.33	5600.00	20.00	MAD	EFFET	\N	\N	GEMINI	[]	VALIDATED	khadija	2026-05-07 11:43:11.528892	\N	/app/uploads/a96939c0-8159-45d8-8a64-478e73d76607.jpg	a84a6d8490d42c08131ea199d299b10885db57b72f861a53ef22bb514f98f3b2	SEMACDO	achat	0.9	04501311	001535246000047	\N	\N	\N	2026-05-07 11:40:43.112661	2026-05-07 11:43:11.522938	\N	\N	\N
129	6	2025-411	2025-12-10	\N	VENTE	STE Comptoire Arrahma S.A.R.L	002012861000010	25005226	2613	Tamoument 2 N° 17 Avenue La marche Verte - KHENIFRA	STE SHEMADRI	003272689000032	\N	\N	4129.50	825.90	4955.40	20.00	MAD	\N	\N	\N	GEMINI	[]	VALIDATED	khadija	2026-05-07 01:18:27.80071	\N	/app/uploads/26ee449f-a498-43ae-8cda-fca938852a6b.pdf	7324450c352d3a2e15ff35e551fbe8dc6a0dc473fae3a48474081e81906428cf	STE Comptoire Arrahma S.A.R.L	vente	0.9	25005226	002012861000010	\N	\N	\N	2026-05-07 01:17:35.469938	2026-05-07 01:18:27.794009	\N	\N	\N
137	6	00000644/26	2026-02-13	2026-02-16	ACHAT	Ets. EL OUJDI & FILS	000086358000020	04100551	18581	Route de Fès 50080 Meknès	STE COMPTOIRE ARRAHMA	002012861000010	\N	\N	3583.33	716.67	4300.00	20.00	MAD	CHEQUE	\N	\N	GEMINI	[]	VALIDATED	khadija	2026-05-07 13:02:12.026375	\N	/app/uploads/624ce247-0fe0-4b4a-adaa-fdd546f490c1.jpg	6f5f147306f9f26de2290e406f61474238781f09c40df3b1376b2477b398a1ea	Ets. EL OUJDI & FILS	achat	0.9	04100551	000086358000020	\N	\N	\N	2026-05-07 13:01:06.757113	2026-05-07 13:02:12.012843	\N	\N	\N
130	6	FA2501536	2025-05-21	\N	ACHAT	OPTIMA CHIMIE	000204969000075	01085612	37789	117 Bd Brahim Roudani, Casablanca, Maroc	COMPTOIR ARRAHMA	002012861000010	\N	FES, MAROC	7916.67	1583.33	9500.00	20.00	MAD	EFFET	\N	\N	GEMINI	[]	VALIDATED	khadija	2026-05-07 01:25:57.989432	\N	/app/uploads/f1da36f7-a306-40c7-bbc5-e523ac7b52f8.pdf	00cba37b629fcf5f36e0b795c9f8f05343f08bd5eed6f9310cdcf0e18081dbc9	OPTIMA CHIMIE	achat	0.9	01085612	000204969000075	\N	\N	\N	2026-05-07 01:21:12.306999	2026-05-07 01:25:57.983739	\N	\N	\N
128	6	2025-407	2025-12-08	\N	VENTE	STE Comptoire Arrahma S.A.R.L	002012861000010	25005226	2613	Tamoument 2 N° 17 Avenue La marche Verte - KHENIFRA	STE SHEMADRI	003272689000032	\N	\N	4040.00	808.00	4848.00	20.00	MAD	\N	\N	\N	GEMINI	[]	VALIDATED	khadija	2026-05-07 01:10:50.252782	\N	/app/uploads/8fe23504-4d85-4659-a1c2-6ec650be57d9.pdf	05f5b9944ac052a425199e22af41a274b86498a00504d0d2af213bbe97180905	STE Comptoire Arrahma S.A.R.L	vente	0.9	25005226	002012861000010	\N	\N	\N	2026-05-07 01:06:09.006563	2026-05-07 01:10:50.247007	\N	\N	\N
134	6	17344	2026-02-13	\N	ACHAT	STE LABSELEC s.a.r.l	001534521000028	04540172	359	Lot P3 Kandoul, Ouled Ali C/R Aghbalou Akorar, Sidi Khyar - SEFROU	STE COMPTOIRE ARRAHMA	002012861000010	\N	KHENIFRA	7416.67	1483.33	8900.00	20.00	MAD	EFFET	\N	\N	GEMINI	[]	VALIDATED	khadija	2026-05-07 11:51:12.789364	\N	/app/uploads/090ce7e3-7abd-4e60-a9d0-b23eca4b09cb.jpg	191733b0cdb2178ceee8903f91c29a6f488ab946c37f4e6d2f325a5827cb10ee	STE LABSELEC s.a.r.l	achat	0.9	04540172	001534521000028	\N	\N	\N	2026-05-07 11:43:40.337183	2026-05-07 11:51:12.786948	\N	\N	\N
\.


--
-- Data for Name: immobilisations; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.immobilisations (id, societe_id, facture_id, designation, categorie, date_acquisition, valeur_acquisition, tva_acquisition, duree_amortissement, taux_amortissement, methode, compte_actif_pcm, compte_amort_pcm, compte_dotation_pcm, statut, created_at, updated_at) FROM stdin;
2	6	\N	Bureau de direction en bois chêne	CORPORELLE	2024-06-01	4500.00	900.00	10	0.1000	LINEAIRE	2351	2835	6193	ACTIF	2026-05-07 15:05:20.750171	2026-05-07 15:05:20.750171
3	6	\N	PC Portable HP	CORPORELLE	2024-05-15	8500.00	1700.00	5	0.2000	LINEAIRE	2355	2835	6193	ACTIF	2026-05-07 16:31:05.172215	2026-05-07 16:31:05.172215
\.


--
-- Data for Name: journaux_comptables; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.journaux_comptables (id, societe_id, code, label, type, created_at, updated_at) FROM stdin;
1	1	ACH	Journal des Achats	ACHAT	2026-03-25 13:42:03	2026-03-25 13:42:03
2	1	VTE	Journal des Ventes	VENTE	2026-03-25 13:42:03	2026-03-25 13:42:03
3	1	OD	Opérations Diverses	OD	2026-03-25 13:42:03	2026-03-25 13:42:03
4	1	BQ	Banque Général	BANQUE	2026-03-25 13:42:03	2026-03-25 13:42:03
5	1	IMMO	Journal des Immobilisations	OD	2026-03-25 13:42:03	2026-03-25 13:42:03
6	1	PAYE	Journal de Paie	PAIE	2026-03-25 13:42:03	2026-03-25 13:42:03
7	2	ACH	Journal des Achats	ACHAT	2026-05-06 23:12:11.858922	2026-05-06 23:12:11.858922
8	2	VTE	Journal des Ventes	VENTE	2026-05-06 23:12:11.858922	2026-05-06 23:12:11.858922
9	2	OD	Opérations Diverses	OD	2026-05-06 23:12:11.858922	2026-05-06 23:12:11.858922
10	2	BQ	Banque Général	BANQUE	2026-05-06 23:12:11.858922	2026-05-06 23:12:11.858922
11	2	IMMO	Journal des Immobilisations	OD	2026-05-06 23:12:11.858922	2026-05-06 23:12:11.858922
12	2	PAYE	Journal de Paie	PAIE	2026-05-06 23:12:11.858922	2026-05-06 23:12:11.858922
19	4	ACH	Journal des Achats	ACHAT	2026-05-06 23:12:11.858922	2026-05-06 23:12:11.858922
20	4	VTE	Journal des Ventes	VENTE	2026-05-06 23:12:11.858922	2026-05-06 23:12:11.858922
21	4	OD	Opérations Diverses	OD	2026-05-06 23:12:11.858922	2026-05-06 23:12:11.858922
22	4	BQ	Banque Général	BANQUE	2026-05-06 23:12:11.858922	2026-05-06 23:12:11.858922
23	4	IMMO	Journal des Immobilisations	OD	2026-05-06 23:12:11.858922	2026-05-06 23:12:11.858922
24	4	PAYE	Journal de Paie	PAIE	2026-05-06 23:12:11.858922	2026-05-06 23:12:11.858922
25	5	ACH	Journal des Achats	ACHAT	2026-05-06 23:12:11.858922	2026-05-06 23:12:11.858922
26	5	VTE	Journal des Ventes	VENTE	2026-05-06 23:12:11.858922	2026-05-06 23:12:11.858922
27	5	OD	Opérations Diverses	OD	2026-05-06 23:12:11.858922	2026-05-06 23:12:11.858922
28	5	BQ	Banque Général	BANQUE	2026-05-06 23:12:11.858922	2026-05-06 23:12:11.858922
29	5	IMMO	Journal des Immobilisations	OD	2026-05-06 23:12:11.858922	2026-05-06 23:12:11.858922
30	5	PAYE	Journal de Paie	PAIE	2026-05-06 23:12:11.858922	2026-05-06 23:12:11.858922
31	1	BQ1	Banque Populaire	BANQUE	2026-05-07 01:15:13.902113	2026-05-07 01:15:13.902113
32	1	BQ2	CIH	BANQUE	2026-05-07 01:15:13.902113	2026-05-07 01:15:13.902113
33	2	BQ1	Banque Populaire	BANQUE	2026-05-07 01:15:13.902113	2026-05-07 01:15:13.902113
34	2	BQ2	CIH	BANQUE	2026-05-07 01:15:13.902113	2026-05-07 01:15:13.902113
35	4	BQ1	Banque Populaire	BANQUE	2026-05-07 01:15:13.902113	2026-05-07 01:15:13.902113
36	4	BQ2	CIH	BANQUE	2026-05-07 01:15:13.902113	2026-05-07 01:15:13.902113
37	5	BQ1	Banque Populaire	BANQUE	2026-05-07 01:15:13.902113	2026-05-07 01:15:13.902113
38	5	BQ2	CIH	BANQUE	2026-05-07 01:15:13.902113	2026-05-07 01:15:13.902113
39	6	ACH	Journal des Achats	ACHAT	2026-05-07 01:15:13.902113	2026-05-07 01:15:13.902113
40	6	VTE	Journal des Ventes	VENTE	2026-05-07 01:15:13.902113	2026-05-07 01:15:13.902113
41	6	IMMO	Journal d'Immobilisations	IMMOBILISATION	2026-05-07 01:15:13.902113	2026-05-07 01:15:13.902113
42	6	OD	Opérations Diverses	OD	2026-05-07 01:15:13.902113	2026-05-07 01:15:13.902113
43	6	PAYE	Journal de Paie	PAIE	2026-05-07 01:15:13.902113	2026-05-07 01:15:13.902113
44	6	BQ1	Banque Populaire	BANQUE	2026-05-07 01:15:13.902113	2026-05-07 01:15:13.902113
45	6	BQ2	CIH	BANQUE	2026-05-07 01:15:13.902113	2026-05-07 01:15:13.902113
\.


--
-- Data for Name: lignes_amortissement; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.lignes_amortissement (id, immobilisation_id, annee, dotation_annuelle, amortissement_cumule, valeur_nette_comptable, ecriture_generee, created_at) FROM stdin;
14	2	2027	450.00	1800.00	2700.00	f	2026-05-07 15:05:20.750171
15	2	2028	450.00	2250.00	2250.00	f	2026-05-07 15:05:20.750171
16	2	2029	450.00	2700.00	1800.00	f	2026-05-07 15:05:20.750171
17	2	2030	450.00	3150.00	1350.00	f	2026-05-07 15:05:20.750171
18	2	2031	450.00	3600.00	900.00	f	2026-05-07 15:05:20.750171
19	2	2032	450.00	4050.00	450.00	f	2026-05-07 15:05:20.750171
20	2	2033	450.00	4500.00	0.00	f	2026-05-07 15:05:20.750171
11	2	2024	450.00	450.00	4050.00	t	2026-05-07 15:05:20.750171
12	2	2025	450.00	900.00	3600.00	t	2026-05-07 15:05:20.750171
13	2	2026	450.00	1350.00	3150.00	t	2026-05-07 15:05:20.750171
24	3	2027	1700.00	6800.00	1700.00	f	2026-05-07 16:31:05.172215
25	3	2028	1700.00	8500.00	0.00	f	2026-05-07 16:31:05.172215
21	3	2024	1700.00	1700.00	6800.00	t	2026-05-07 16:31:05.172215
22	3	2025	1700.00	3400.00	5100.00	t	2026-05-07 16:31:05.172215
23	3	2026	1700.00	5100.00	3400.00	t	2026-05-07 16:31:05.172215
\.


--
-- Data for Name: lignes_ecritures; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.lignes_ecritures (id, ecriture_journal_id, line_order, account_code, account_label, debit, credit, tiers_name, tiers_ice, created_at) FROM stdin;
1	1	1	6171	Rémunérations du personnel	6750.00	0.00	\N	\N	2026-03-03 12:44:43
2	1	2	6174	Charges sociales patronales (CNSS+AMO)	904.35	0.00	\N	\N	2026-03-03 12:44:43
3	1	3	4441	Salaire net à payer — Driss EL OMARI	0.00	6059.59	Driss EL OMARI	\N	2026-03-03 12:44:43
4	1	4	4443	CNSS — part salarié	0.00	268.80	\N	\N	2026-03-03 12:44:43
5	1	5	4443	CNSS — part patronale	0.00	638.40	\N	\N	2026-03-03 12:44:43
6	1	6	4447	AMO — part salarié	0.00	152.55	\N	\N	2026-03-03 12:44:43
7	1	7	4447	AMO — part patronale	0.00	265.95	\N	\N	2026-03-03 12:44:43
8	1	8	4444	IR/IGR retenu à la source	0.00	269.06	\N	\N	2026-03-03 12:44:43
346	153	1	6193	Dotations aux amortissements	1700.00	0.00	\N	\N	2026-05-07 16:31:33.483259
347	153	2	2835	Amortissements cumulés	0.00	1700.00	\N	\N	2026-05-07 16:31:33.483259
356	155	1	6171	Rémunérations du personnel	6700.00	0.00	moujahid Abbes	\N	2026-05-07 19:11:21.288782
357	155	2	4432	Rémunérations dues au personnel	0.00	5958.49	moujahid Abbes	\N	2026-05-07 19:11:21.288782
358	155	3	4441	Caisse Nationale de la Sécurité Sociale	0.00	268.80	moujahid Abbes	\N	2026-05-07 19:11:21.288782
359	155	4	4447	Charges sociales à payer	0.00	151.42	moujahid Abbes	\N	2026-05-07 19:11:21.288782
360	155	5	4453	État - impôt sur le revenu (retenu à la source)	0.00	321.29	moujahid Abbes	\N	2026-05-07 19:11:21.288782
369	160	\N	51410000	BANQUE	0.00	5600.00	\N	\N	2026-05-07 20:11:15.714988
370	160	\N	4411	\N	5600.00	0.00	\N	\N	2026-05-07 20:11:15.714988
377	164	\N	51410000	BANQUE	0.00	1.00	\N	\N	2026-05-07 20:18:58.475834
378	164	\N	61671	\N	1.00	0.00	\N	\N	2026-05-07 20:18:58.475834
190	128	1	3421	Clients	4848.00	0.00	STE SHEMADRI	003272689000032	2026-05-07 01:06:43.467928
191	128	2	7111	PROJECTEURE 50W LED TOPAGE	0.00	1200.00	STE SHEMADRI	003272689000032	2026-05-07 01:06:43.467928
192	128	3	4455	TVA facturée	0.00	240.00	STE SHEMADRI	003272689000032	2026-05-07 01:06:43.467928
193	128	4	7111	APPLIQUE SAFI EN ALIMINIUME A POSER	0.00	1200.00	STE SHEMADRI	003272689000032	2026-05-07 01:06:43.467928
194	128	5	4455	TVA facturée	0.00	240.00	STE SHEMADRI	003272689000032	2026-05-07 01:06:43.467928
195	128	6	7111	TRINGLE POPULAIRE 3MAB	0.00	480.00	STE SHEMADRI	003272689000032	2026-05-07 01:06:43.467928
196	128	7	4455	TVA facturée	0.00	96.00	STE SHEMADRI	003272689000032	2026-05-07 01:06:43.467928
197	128	8	7111	ROBINET D ARRET 3/4 VILDA	0.00	360.00	STE SHEMADRI	003272689000032	2026-05-07 01:06:43.467928
198	128	9	4455	TVA facturée	0.00	72.00	STE SHEMADRI	003272689000032	2026-05-07 01:06:43.467928
199	128	10	7111	VINYL ROSE MAMOUNIA 30 KG	0.00	800.00	STE SHEMADRI	003272689000032	2026-05-07 01:06:43.467928
200	128	11	4455	TVA facturée	0.00	160.00	STE SHEMADRI	003272689000032	2026-05-07 01:06:43.467928
201	129	1	3421	Clients	4955.40	0.00	STE SHEMADRI	003272689000032	2026-05-07 01:17:55.309479
202	129	2	7111	LUMINAIRE 125W SAFILUM	0.00	300.00	STE SHEMADRI	003272689000032	2026-05-07 01:17:55.309479
203	129	3	4455	TVA facturée	0.00	60.00	STE SHEMADRI	003272689000032	2026-05-07 01:17:55.309479
204	129	4	7111	CABLE SOUPLE 2*1.5 TUMAG	0.00	3.50	STE SHEMADRI	003272689000032	2026-05-07 01:17:55.309479
205	129	5	4455	TVA facturée	0.00	0.70	STE SHEMADRI	003272689000032	2026-05-07 01:17:55.309479
206	129	6	7111	DISJONCTEUR SECURIS TRIPOLAIRE 40A ING	0.00	180.00	STE SHEMADRI	003272689000032	2026-05-07 01:17:55.309479
207	129	7	4455	TVA facturée	0.00	36.00	STE SHEMADRI	003272689000032	2026-05-07 01:17:55.309479
208	129	8	7111	ATLAS TOP L0.5	0.00	960.00	STE SHEMADRI	003272689000032	2026-05-07 01:17:55.309479
209	129	9	4455	TVA facturée	0.00	192.00	STE SHEMADRI	003272689000032	2026-05-07 01:17:55.309479
210	129	10	7111	LAQUE CELL REF 90006 1/2 NOIR	0.00	336.00	STE SHEMADRI	003272689000032	2026-05-07 01:17:55.309479
211	129	11	4455	TVA facturée	0.00	67.20	STE SHEMADRI	003272689000032	2026-05-07 01:17:55.309479
212	129	12	7111	ITRY LAC W001 K20 BLANC	0.00	1950.00	STE SHEMADRI	003272689000032	2026-05-07 01:17:55.309479
213	129	13	4455	TVA facturée	0.00	390.00	STE SHEMADRI	003272689000032	2026-05-07 01:17:55.309479
214	129	14	7111	ATLAS WOOD W800 ANTI UV L0.850	0.00	400.00	STE SHEMADRI	003272689000032	2026-05-07 01:17:55.309479
215	129	15	4455	TVA facturée	0.00	80.00	STE SHEMADRI	003272689000032	2026-05-07 01:17:55.309479
216	130	1	6121	JET LAC GRIS FONCE / 4.6 KG	1916.67	0.00	OPTIMA CHIMIE	000204969000075	2026-05-07 01:23:30.094712
217	130	2	34551	TVA récupérable	383.33	0.00	OPTIMA CHIMIE	000204969000075	2026-05-07 01:23:30.094712
218	130	3	6121	JET LAC MARRON FONCE / 0.860 KG	5750.00	0.00	OPTIMA CHIMIE	000204969000075	2026-05-07 01:23:30.094712
219	130	4	34551	TVA récupérable	1150.00	0.00	OPTIMA CHIMIE	000204969000075	2026-05-07 01:23:30.094712
220	130	5	6121	CAFLEX BLANCHE / 5 KG	250.00	0.00	OPTIMA CHIMIE	000204969000075	2026-05-07 01:23:30.094712
221	130	6	34551	TVA récupérable	50.00	0.00	OPTIMA CHIMIE	000204969000075	2026-05-07 01:23:30.094712
222	130	7	4411	Fournisseurs	0.00	9500.00	OPTIMA CHIMIE	000204969000075	2026-05-07 01:23:30.094712
223	131	1	6121	SABBIA SILVER 700 20KG	3700.00	0.00	Ets. EL OUJDI & FILS	000086358000020	2026-05-07 01:27:25.757085
224	131	2	34551	TVA récupérable	740.00	0.00	Ets. EL OUJDI & FILS	000086358000020	2026-05-07 01:27:25.757085
225	131	3	6121	AFRIVINYL V2 30KG	1260.00	0.00	Ets. EL OUJDI & FILS	000086358000020	2026-05-07 01:27:25.757085
226	131	4	34551	TVA récupérable	252.00	0.00	Ets. EL OUJDI & FILS	000086358000020	2026-05-07 01:27:25.757085
227	131	5	6121	SARAMAT 01KG	40.00	0.00	Ets. EL OUJDI & FILS	000086358000020	2026-05-07 01:27:25.757085
228	131	6	34551	TVA récupérable	8.00	0.00	Ets. EL OUJDI & FILS	000086358000020	2026-05-07 01:27:25.757085
229	131	7	4411	Fournisseurs	0.00	6000.00	Ets. EL OUJDI & FILS	000086358000020	2026-05-07 01:27:25.757085
342	151	1	6193	Dotations aux amortissements	1700.00	0.00	\N	\N	2026-05-07 16:31:29.985447
233	133	1	6122	DISJONCTEUR SECURIS UNIPOLAIRE 16A INGELEC	1245.33	0.00	SEMACDO	001535246000047	2026-05-07 11:41:24.66424
234	133	2	34551	TVA récupérable	249.07	0.00	SEMACDO	001535246000047	2026-05-07 11:41:24.66424
235	133	3	6122	BLOC DE SECOURS LED FLASH 2W 6500K 150LM	1792.26	0.00	SEMACDO	001535246000047	2026-05-07 11:41:24.66424
236	133	4	34551	TVA récupérable	358.45	0.00	SEMACDO	001535246000047	2026-05-07 11:41:24.66424
237	133	5	6122	POMPE CENTRIFUGE A EAU 0,5 HP / 370W AL 50 FERRI	1357.63	0.00	SEMACDO	001535246000047	2026-05-07 11:41:24.66424
238	133	6	34551	TVA récupérable	271.53	0.00	SEMACDO	001535246000047	2026-05-07 11:41:24.66424
239	133	7	6121	SADER BOIS 4 KG	202.31	0.00	SEMACDO	001535246000047	2026-05-07 11:41:24.66424
240	133	8	34551	TVA récupérable	40.46	0.00	SEMACDO	001535246000047	2026-05-07 11:41:24.66424
241	133	9	6122	POUSSOIR ROND LUMINEUX NOIR SAFIR	69.13	0.00	SEMACDO	001535246000047	2026-05-07 11:41:24.66424
242	133	10	34551	TVA récupérable	13.83	0.00	SEMACDO	001535246000047	2026-05-07 11:41:24.66424
243	133	11	4411	Fournisseurs	0.00	5600.00	SEMACDO	001535246000047	2026-05-07 11:41:24.66424
244	134	1	6122	BOITE D'ENCASTREMENT CARREE VE	262.50	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
245	134	2	34551	TVA récupérable	52.50	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
246	134	3	6122	MINUTERIE D'ESCAL 230V EMN001	475.00	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
247	134	4	34551	TVA récupérable	95.00	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
248	134	5	6122	DISJONCTEUR SECURIS UNIPOLAIRE 16A ING	800.00	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
249	134	6	34551	TVA récupérable	160.00	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
250	134	7	6122	KREPP MIARCO 24mm x 45M	332.50	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
251	134	8	34551	TVA récupérable	66.50	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
252	134	9	6122	LAMPE LED 36W NN	258.33	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
253	134	10	34551	TVA récupérable	51.67	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
254	134	11	6122	PRISE 2P+T GALAXY MARRON	442.50	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
255	134	12	34551	TVA récupérable	88.50	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
256	134	13	6122	INTERRUPTEUR SA GALAXY MARRON	227.50	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
257	134	14	34551	TVA récupérable	45.50	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
258	134	15	6122	POUSSOIR ROND LUM GALAXY MARRON	414.17	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
259	134	16	34551	TVA récupérable	82.83	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
260	134	17	6111	FICHE 2P+T MALE COUDEE	91.67	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
261	134	18	34551	TVA récupérable	18.33	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
262	134	19	6111	SOUPLE SM 2X0,75 GRIS CLAIR	566.67	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
263	134	20	34551	TVA récupérable	113.33	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
264	134	21	6111	SOUPLE SM 2X1 GRIS CLAIR	341.67	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
265	134	22	34551	TVA récupérable	68.33	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
266	134	23	6122	PRISE 2P GALAXY MARRON	455.00	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
267	134	24	34551	TVA récupérable	91.00	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
268	134	25	6122	ITL 16A 1P 230/240V A9C30811	525.00	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
269	134	26	34551	TVA récupérable	105.00	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
270	134	27	6122	SOUPLE SM 2X1,5 GRIS CLAIR	420.83	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
271	134	28	34551	TVA récupérable	84.17	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
272	134	29	6122	CABLE TORSADE ALUM 2 X 16 CORN	1075.00	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
273	134	30	34551	TVA récupérable	215.00	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
274	134	31	6122	HUBLOT ROND EN VERRE B22 2006V	320.00	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
275	134	32	34551	TVA récupérable	64.00	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
276	134	33	6122	EXTRACTEUR Q98/100M3/H 220V VF-B4	408.33	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
277	134	34	34551	TVA récupérable	81.67	0.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
278	134	35	4411	Fournisseurs	0.00	8900.00	STE LABSELEC s.a.r.l	001534521000028	2026-05-07 11:50:06.185508
283	137	1	6121	KONOUZ SILVER 01 20KG + GLITER	2233.33	0.00	Ets. EL OUJDI & FILS	000086358000020	2026-05-07 13:01:30.726551
284	137	2	34551	TVA récupérable	446.67	0.00	Ets. EL OUJDI & FILS	000086358000020	2026-05-07 13:01:30.726551
285	137	3	6121	SUPERSARAVINYL V10+ 30KG	1187.50	0.00	Ets. EL OUJDI & FILS	000086358000020	2026-05-07 13:01:30.726551
286	137	4	34551	TVA récupérable	237.50	0.00	Ets. EL OUJDI & FILS	000086358000020	2026-05-07 13:01:30.726551
287	137	5	6121	ENDUIT PATE SARA 2000 25KG	108.33	0.00	Ets. EL OUJDI & FILS	000086358000020	2026-05-07 13:01:30.726551
288	137	6	34551	TVA récupérable	21.67	0.00	Ets. EL OUJDI & FILS	000086358000020	2026-05-07 13:01:30.726551
289	137	7	6121	VERNIS DIVA NACRE SILVER 100	54.17	0.00	Ets. EL OUJDI & FILS	000086358000020	2026-05-07 13:01:30.726551
290	137	8	34551	TVA récupérable	10.83	0.00	Ets. EL OUJDI & FILS	000086358000020	2026-05-07 13:01:30.726551
291	137	9	4411	Fournisseurs	0.00	4300.00	Ets. EL OUJDI & FILS	000086358000020	2026-05-07 13:01:30.726551
333	148	1	2351	Immobilisation — Bureau de direction en bois chêne	4500.00	0.00		\N	2026-05-07 15:58:56.641427
334	148	2	34552	TVA récupérable sur immobilisations	900.00	0.00		\N	2026-05-07 15:58:56.641427
335	148	3	4411	Fournisseurs	0.00	5400.00		\N	2026-05-07 15:58:56.641427
343	151	2	2835	Amortissements cumulés	0.00	1700.00	\N	\N	2026-05-07 16:31:29.985447
348	150	1	2355	Immobilisation — PC Portable HP	8500.00	0.00		\N	2026-05-07 16:37:34.577943
349	150	2	34552	TVA récupérable sur immobilisations	1700.00	0.00		\N	2026-05-07 16:37:34.577943
350	150	3	4411	Fournisseurs	0.00	10200.00		\N	2026-05-07 16:37:34.577943
361	156	\N	51410000	BANQUE	0.00	3.50	\N	\N	2026-05-07 20:02:11.008301
362	156	\N	34552000	\N	3.50	0.00	\N	\N	2026-05-07 20:02:11.008301
379	165	\N	51410000	BANQUE	0.00	4300.00	\N	\N	2026-05-07 20:19:09.665011
380	165	\N	4411	\N	4300.00	0.00	\N	\N	2026-05-07 20:19:09.665011
385	168	\N	51410000	BANQUE	16500.00	0.00	\N	\N	2026-05-07 20:21:28.968418
386	168	\N	3421	\N	0.00	16500.00	\N	\N	2026-05-07 20:21:28.968418
336	149	1	7111	VINYL ROSE MAMOUNIA 30 KG	800.00	0.00	STE SHEMADRI	003272689000032	2026-05-07 16:22:00.025402
337	149	2	4455	TVA facturée (Avoir)	160.00	0.00	STE SHEMADRI	003272689000032	2026-05-07 16:22:00.025402
338	149	3	3421	Clients (Avoir)	0.00	960.00	STE SHEMADRI	003272689000032	2026-05-07 16:22:00.025402
344	152	1	6193	Dotations aux amortissements	1700.00	0.00	\N	\N	2026-05-07 16:31:31.925173
345	152	2	2835	Amortissements cumulés	0.00	1700.00	\N	\N	2026-05-07 16:31:31.925173
351	154	1	6171	Rémunérations du personnel	8500.00	0.00	merzak oumayma	\N	2026-05-07 19:03:33.26001
352	154	2	4432	Rémunérations dues au personnel	0.00	7304.04	merzak oumayma	\N	2026-05-07 19:03:33.26001
353	154	3	4441	Caisse Nationale de la Sécurité Sociale	0.00	268.80	merzak oumayma	\N	2026-05-07 19:03:33.26001
354	154	4	4447	Charges sociales à payer	0.00	192.10	merzak oumayma	\N	2026-05-07 19:03:33.26001
355	154	5	4453	État - impôt sur le revenu (retenu à la source)	0.00	735.06	merzak oumayma	\N	2026-05-07 19:03:33.26001
363	157	\N	51410000	BANQUE	0.00	6000.00	\N	\N	2026-05-07 20:07:41.026803
309	145	1	6193	Dotations aux amortissements	450.00	0.00	\N	\N	2026-05-07 15:05:27.314699
310	145	2	2835	Amortissements cumulés	0.00	450.00	\N	\N	2026-05-07 15:05:27.314699
311	146	1	6193	Dotations aux amortissements	450.00	0.00	\N	\N	2026-05-07 15:05:44.013793
312	146	2	2835	Amortissements cumulés	0.00	450.00	\N	\N	2026-05-07 15:05:44.013793
313	147	1	6193	Dotations aux amortissements	450.00	0.00	\N	\N	2026-05-07 15:05:45.886844
314	147	2	2835	Amortissements cumulés	0.00	450.00	\N	\N	2026-05-07 15:05:45.886844
364	157	\N	4411	\N	6000.00	0.00	\N	\N	2026-05-07 20:07:41.026803
365	158	\N	51410000	BANQUE	16500.00	0.00	\N	\N	2026-05-07 20:09:22.650011
366	158	\N	3421	\N	0.00	16500.00	\N	\N	2026-05-07 20:09:22.650011
367	159	\N	51410000	BANQUE	0.00	1.00	\N	\N	2026-05-07 20:10:57.255626
368	159	\N	61671	\N	1.00	0.00	\N	\N	2026-05-07 20:10:57.255626
371	161	\N	51410000	BANQUE	7400.00	0.00	\N	\N	2026-05-07 20:14:11.105126
372	161	\N	3421	\N	0.00	7400.00	\N	\N	2026-05-07 20:14:11.105126
373	162	\N	51410000	BANQUE	0.00	1910.24	\N	\N	2026-05-07 20:14:35.784403
374	162	\N	4443	\N	1910.24	0.00	\N	\N	2026-05-07 20:14:35.784403
375	163	\N	51410000	BANQUE	0.00	1.00	\N	\N	2026-05-07 20:18:09.815161
376	163	\N	61671	\N	1.00	0.00	\N	\N	2026-05-07 20:18:09.815161
381	166	\N	51410000	BANQUE	0.00	8900.00	\N	\N	2026-05-07 20:19:13.382796
382	166	\N	4411	\N	8900.00	0.00	\N	\N	2026-05-07 20:19:13.382796
383	167	\N	51410000	BANQUE	0.00	16500.00	\N	\N	2026-05-07 20:19:51.41208
384	167	\N	4411	\N	16500.00	0.00	\N	\N	2026-05-07 20:19:51.41208
\.


--
-- Data for Name: lignes_factures; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.lignes_factures (id, facture_id, line_number, description, quantity, unit, unit_price_ht, line_amount_ht, tva_rate, tva_amount, line_amount_ttc, pcm_class, pcm_account_code, pcm_account_label, classification_confidence, classification_reason, is_corrected, corrected_account_code, created_at) FROM stdin;
1	1	\N	Abonnement Internet	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	2026-02-24 09:37:57
2	2	\N	Consommation Mobile	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	2026-02-24 09:37:57
183	142	1	VINYL ROSE MAMOUNIA 30 KG	-2.000	\N	400.0000	-800.00	20.00	-160.00	-960.00	7	7111	Ventes de marchandises	1	Appris via l'ICE fournisseur: 002012861000010	f	\N	2026-05-07 16:21:42.52297
133	128	2	PROJECTEURE 50W LED TOPAGE	6.000	\N	200.0000	1200.00	20.00	240.00	1440.00	7	7111	Ventes de marchandises au Maroc	0.95	La facture est de type VENTE et concerne un produit physique (projecteur LED), ce qui correspond à une vente de marchandises au Maroc selon le PCM.	f	\N	2026-05-07 01:06:09.052974
134	128	3	APPLIQUE SAFI EN ALIMINIUME A POSER	12.000	\N	100.0000	1200.00	20.00	240.00	1440.00	7	7111	Ventes de marchandises au Maroc	0.95	La description indique la vente d'un luminaire (applique). Puisqu'il s'agit d'une facture de type VENTE, le produit doit être classé en classe 7. Le compte 7111 est utilisé pour les ventes de marchandises au Maroc.	f	\N	2026-05-07 01:06:09.052974
135	128	4	TRINGLE POPULAIRE 3MAB	12.000	\N	40.0000	480.00	20.00	96.00	576.00	7	7111	Ventes de marchandises au Maroc	0.95	La description correspond à un article de quincaillerie (tringle) et le type de facture est une vente, ce qui oriente vers le compte de vente de marchandises au Maroc.	f	\N	2026-05-07 01:06:09.052974
136	128	5	ROBINET D ARRET 3/4 VILDA	8.000	\N	45.0000	360.00	20.00	72.00	432.00	7	7111	Ventes de marchandises au Maroc	0.95	La description correspond à un article de quincaillerie et le type de facture est une vente, ce qui oriente vers le compte de vente de marchandises au Maroc.	f	\N	2026-05-07 01:06:09.052974
132	128	1	VINYL ROSE MAMOUNIA 30 KG	2.000	\N	400.0000	800.00	20.00	160.00	960.00	7	7111	Vente de marchandises au Maroc	0.95	La description correspond à un produit de peinture (Vinyl) et le type de facture est une vente, ce qui oriente vers le compte 7111 pour la vente de marchandises au Maroc.	f	\N	2026-05-07 01:06:09.052974
137	129	1	LUMINAIRE 125W SAFILUM	1.000	\N	300.0000	300.00	20.00	60.00	360.00	7	7111	Ventes de marchandises	1	Appris via l'ICE fournisseur: 002012861000010	f	\N	2026-05-07 01:17:35.523978
138	129	2	CABLE SOUPLE 2*1.5 TUMAG	1.000	\N	3.5000	3.50	20.00	0.70	4.20	7	7111	Ventes de marchandises	1	Appris via l'ICE fournisseur: 002012861000010	f	\N	2026-05-07 01:17:35.523978
139	129	3	DISJONCTEUR SECURIS TRIPOLAIRE 40A ING	2.000	\N	90.0000	180.00	20.00	36.00	216.00	7	7111	Ventes de marchandises	1	Appris via l'ICE fournisseur: 002012861000010	f	\N	2026-05-07 01:17:35.523978
140	129	4	ATLAS TOP L0.5	12.000	\N	80.0000	960.00	20.00	192.00	1152.00	7	7111	Ventes de marchandises	1	Appris via l'ICE fournisseur: 002012861000010	f	\N	2026-05-07 01:17:35.523978
141	129	5	LAQUE CELL REF 90006 1/2 NOIR	12.000	\N	28.0000	336.00	20.00	67.20	403.20	7	7111	Ventes de marchandises	1	Appris via l'ICE fournisseur: 002012861000010	f	\N	2026-05-07 01:17:35.523978
142	129	6	ITRY LAC W001 K20 BLANC	3.000	\N	650.0000	1950.00	20.00	390.00	2340.00	7	7111	Ventes de marchandises	1	Appris via l'ICE fournisseur: 002012861000010	f	\N	2026-05-07 01:17:35.523978
143	129	7	ATLAS WOOD W800 ANTI UV L0.850	5.000	\N	80.0000	400.00	20.00	80.00	480.00	7	7111	Ventes de marchandises	1	Appris via l'ICE fournisseur: 002012861000010	f	\N	2026-05-07 01:17:35.523978
144	130	1	JET LAC GRIS FONCE / 4.6 KG	20.000	\N	95.8300	1916.67	20.00	383.33	2300.00	6	6121	Achats de matières premières	0.95	Le produit 'JET LAC' est une laque ou peinture de finition. Étant conditionné en KG (4.6 KG) et ayant un montant inférieur à 5000 MAD, il s'agit d'une matière consommable classée en charges (Classe 6) et non d'une immobilisation.	f	\N	2026-05-07 01:21:12.63834
145	130	2	JET LAC MARRON FONCE / 0.860 KG	300.000	\N	19.1700	5750.00	20.00	1150.00	6900.00	6	6121	Achats de matières premières	0.95	Le produit 'JET LAC' est une laque (peinture/vernis) conditionnée en KG, ce qui correspond à une matière première ou consommable. Selon les règles strictes énoncées, les produits de finition et chimiques ne sont jamais des immobilisations, même si le montant dépasse 5 000 MAD.	f	\N	2026-05-07 01:21:12.63834
146	130	3	CAFLEX BLANCHE / 5 KG	4.000	\N	62.5000	250.00	20.00	50.00	300.00	6	6121	Achats de matières premières	0.95	Le produit 'CAFLEX BLANCHE' est un matériau de construction ou de finition (type colle ou enduit) conditionné en 5 KG. Il s'agit d'un bien consommable utilisé dans le cadre de l'activité, classé en achats de matières premières (6121) conformément aux règles de la classe 6.	f	\N	2026-05-07 01:21:12.63834
147	131	1	SABBIA SILVER 700 20KG	5.000	KG	740.0000	3700.00	20.00	740.00	4440.00	6	6121	Achats de matières premières	0.95	Le produit 'SABBIA SILVER' conditionné en 20KG est un matériau de finition (peinture ou enduit décoratif). Selon les règles de classification, les produits chimiques, peintures et articles pesés en KG sont des consommables de classe 6 et non des immobilisations.	f	\N	2026-05-07 01:26:35.923223
148	131	2	AFRIVINYL V2 30KG	7.000	KG	180.0000	1260.00	20.00	252.00	1512.00	6	6121	Achats de matières premières	0.95	Le produit 'AFRIVINYL' est une peinture ou un revêtement (indiqué par 'VINYL' et le poids '30KG'), ce qui correspond à un achat de matières premières ou fournitures consommables pour le secteur du bâtiment/finition.	f	\N	2026-05-07 01:26:35.923223
149	131	3	SARAMAT 01KG	2.000	KG	20.0000	40.00	20.00	8.00	48.00	6	6121	Achats de matières premières	0.95	Le produit 'SARAMAT 01KG' correspond à une peinture ou un enduit de finition. Compte tenu de sa nature de consommable et de son faible montant (40 MAD), il est classé en achats de matières premières (6121) conformément aux instructions pour les produits de type peinture/enduit.	f	\N	2026-05-07 01:26:35.923223
151	133	1	DISJONCTEUR SECURIS UNIPOLAIRE 16A INGELEC	108.000	\N	11.5310	1245.33	20.00	249.07	1494.40	6	6122	Achats de matières et fournitures liées	0.95	Le disjoncteur est un composant électrique considéré comme une fourniture consommable. Le montant (1245.33 MAD) est inférieur au seuil de 5000 MAD requis pour une immobilisation.	f	\N	2026-05-07 11:40:43.158661
152	133	2	BLOC DE SECOURS LED FLASH 2W 6500K 150LM	35.000	\N	51.2080	1792.27	20.00	358.45	2150.73	6	6122	Achats de matières et fournitures liées	0.95	Le bloc de secours LED est un petit équipement électrique. Son montant (1792.27 MAD) est inférieur au seuil de 5 000 MAD requis pour une immobilisation, il est donc comptabilisé en charges comme fournitures consommables.	f	\N	2026-05-07 11:40:43.158661
153	133	3	POMPE CENTRIFUGE A EAU 0,5 HP / 370W AL 50 FERRI	11.000	\N	123.4210	1357.63	20.00	271.53	1629.15	6	6122	Achats de matières et fournitures liées	0.95	Le montant de 1357.63 MAD est inférieur au seuil de 5000 MAD requis pour une immobilisation en classe 2. Cette pompe centrifuge est donc traitée comme un petit matériel ou une fourniture consommable en classe 6.	f	\N	2026-05-07 11:40:43.158661
154	133	4	SADER BOIS 4 KG	4.000	\N	50.5770	202.31	20.00	40.46	242.77	6	6121	Achats de matières premières	0.95	SADER BOIS est une colle à bois, assimilée à une matière première ou un matériau de consommation (similaire aux peintures et vernis cités dans les règles). Le montant et le conditionnement (4 KG) confirment qu'il s'agit d'une charge et non d'une immobilisation.	f	\N	2026-05-07 11:40:43.158661
155	133	5	POUSSOIR ROND LUMINEUX NOIR SAFIR	4.000	\N	17.2820	69.13	20.00	13.83	82.95	6	6122	Achats de matières et fournitures liées	0.95	Le produit est un composant électrique (poussoir) de faible valeur (69.13 MAD), ce qui l'exclut des immobilisations. Il est classé comme fourniture consommable en classe 6.	f	\N	2026-05-07 11:40:43.158661
156	134	1	BOITE D'ENCASTREMENT CARREE VE	140.000	\N	1.8750	262.50	20.00	52.50	315.00	6	6122	Achats de matières et fournitures liées	0.95	Il s'agit d'un petit matériel électrique (boîte d'encastrement) utilisé comme fourniture consommable. Le montant est très inférieur au seuil d'immobilisation de 5 000 MAD et la nature du produit correspond à une charge d'exploitation de classe 6.	f	\N	2026-05-07 11:43:40.361317
157	134	2	MINUTERIE D'ESCAL 230V EMN001	3.000	\N	158.3330	475.00	20.00	95.00	570.00	6	6122	Achats de matières et fournitures liées	0.9	Il s'agit d'un composant électrique (minuterie) de faible valeur (475 MAD), bien en dessous du seuil d'immobilisation de 5000 MAD. Il est classé comme fourniture consommable.	f	\N	2026-05-07 11:43:40.361317
158	134	3	DISJONCTEUR SECURIS UNIPOLAIRE 16A ING	60.000	\N	13.3330	800.00	20.00	160.00	960.00	6	6122	Achats de matières et fournitures liées	0.95	Le disjoncteur est un composant électrique considéré comme une fourniture consommable. Le montant de 800 MAD est bien inférieur au seuil de 5 000 MAD requis pour une immobilisation.	f	\N	2026-05-07 11:43:40.361317
159	134	4	KREPP MIARCO 24mm x 45M	70.000	\N	4.7500	332.50	20.00	66.50	399.00	6	6122	Achats de matières et fournitures liées	0.95	Le produit 'KREPP MIARCO' est un ruban adhésif de masquage (fourniture consommable). Compte tenu de sa nature et de son faible montant (332.5 MAD), il s'agit d'une charge d'exploitation de classe 6.	f	\N	2026-05-07 11:43:40.361317
160	134	5	LAMPE LED 36W NN	50.000	\N	5.1670	258.33	20.00	51.67	310.00	6	6122	Achats de matières et fournitures liées	0.95	L'article est une lampe LED, un bien consommable de faible valeur (258.33 MAD), ce qui exclut une immobilisation. Il s'agit d'une fourniture consommable classée en charges.	f	\N	2026-05-07 11:43:40.361317
161	134	6	PRISE 2P+T GALAXY MARRON	30.000	\N	14.7500	442.50	20.00	88.50	531.00	6	6122	Achats de matières et fournitures liées	0.95	Il s'agit d'un petit matériel électrique (prise) dont le montant (442.5 MAD) est bien inférieur au seuil de capitalisation des immobilisations (5000 MAD). Il est donc classé en charges comme fourniture consommable.	f	\N	2026-05-07 11:43:40.361317
162	134	7	INTERRUPTEUR SA GALAXY MARRON	20.000	\N	11.3750	227.50	20.00	45.50	273.00	6	6122	Achats de matières et fournitures liées	0.95	L'interrupteur est un petit matériel électrique considéré comme une fourniture consommable. Étant donné son faible montant (227.5 MAD) et sa nature, il s'agit d'une charge d'exploitation et non d'une immobilisation.	f	\N	2026-05-07 11:43:40.361317
163	134	8	POUSSOIR ROND LUM GALAXY MARRON	20.000	\N	20.7080	414.17	20.00	82.83	497.00	6	6122	Achats de matières et fournitures consommables	0.95	Le produit est un composant électrique (poussoir) de faible valeur unitaire (414.17 MAD), ce qui l'exclut des immobilisations. Il est classé comme fourniture consommable dans les charges d'exploitation.	f	\N	2026-05-07 11:43:40.361317
166	134	11	FICHE 2P+T MALE COUDEE	20.000	\N	4.5830	91.67	20.00	18.33	110.00	\N	\N	\N	\N	\N	f	\N	2026-05-07 11:43:40.361317
167	134	12	SOUPLE SM 2X0,75 GRIS CLAIR	200.000	\N	2.8330	566.67	20.00	113.33	680.00	\N	\N	\N	\N	\N	f	\N	2026-05-07 11:43:40.361317
168	134	13	SOUPLE SM 2X1 GRIS CLAIR	100.000	\N	3.4170	341.67	20.00	68.33	410.00	\N	\N	\N	\N	\N	f	\N	2026-05-07 11:43:40.361317
164	134	9	PRISE 2P GALAXY MARRON	40.000	\N	11.3750	455.00	20.00	91.00	546.00	6	6122	Achats de matières et fournitures liées	0.95	Il s'agit d'un achat de petit matériel électrique (prise) considéré comme une fourniture consommable. Le montant de 455 MAD est bien inférieur au seuil de 5 000 MAD requis pour une immobilisation.	f	\N	2026-05-07 11:43:40.361317
165	134	10	ITL 16A 1P 230/240V A9C30811	5.000	\N	105.0000	525.00	20.00	105.00	630.00	6	6122	Achats de matières et fournitures liées	0.95	L'article ITL 16A est un composant électrique (télérupteur) considéré comme une fourniture consommable. Le montant de 525 MAD est inférieur au seuil d'immobilisation.	f	\N	2026-05-07 11:43:40.361317
169	134	14	SOUPLE SM 2X1,5 GRIS CLAIR	100.000	\N	4.2080	420.83	20.00	84.17	505.00	6	6122	Achats de matières et fournitures consommables	0.95	La description 'SOUPLE SM 2X1,5' correspond à du câble électrique, qui est une fourniture consommable. Le montant (420.83 MAD) est bien inférieur au seuil des immobilisations et la nature du produit exclut la classe 2.	f	\N	2026-05-07 11:43:40.361317
170	134	15	CABLE TORSADE ALUM 2 X 16 CORN	200.000	\N	5.3750	1075.00	20.00	215.00	1290.00	6	6122	Achats de matières et fournitures liées	0.95	Le câble torsadé en aluminium est une fourniture consommable utilisée pour des installations électriques ou la maintenance. Étant donné sa nature et son montant inférieur à 5 000 MAD, il est classé en charges (Classe 6) comme achat de fournitures.	f	\N	2026-05-07 11:43:40.361317
171	134	16	HUBLOT ROND EN VERRE B22 2006V	12.000	\N	26.6670	320.00	20.00	64.00	384.00	6	6122	Achats de matières et fournitures liées	0.95	L'article est un hublot en verre (fourniture de petit équipement). Le montant de 320 MAD est bien inférieur au seuil de 5 000 MAD pour une immobilisation, classant cet achat en charges consommables.	f	\N	2026-05-07 11:43:40.361317
172	134	17	EXTRACTEUR Q98/100M3/H 220V VF-B4	10.000	\N	40.8330	408.33	20.00	81.67	490.00	6	6122	Achats de matières et fournitures liées	0.95	L'extracteur est un petit équipement électrique dont le montant (408.33 MAD) est inférieur au seuil de 5 000 MAD pour une immobilisation. Il est donc comptabilisé en charges comme fourniture consommable.	f	\N	2026-05-07 11:43:40.361317
175	137	1	KONOUZ SILVER 01 20KG + GLITER	4.000	\N	558.3300	2233.33	20.00	446.67	2680.00	6	6121	Achats de matières premières	1	Appris via l'ICE fournisseur: 000086358000020	f	\N	2026-05-07 13:01:06.839347
176	137	2	SUPERSARAVINYL V10+ 30KG	5.000	\N	237.5000	1187.50	20.00	237.50	1425.00	6	6121	Achats de matières premières	1	Appris via l'ICE fournisseur: 000086358000020	f	\N	2026-05-07 13:01:06.839347
177	137	3	ENDUIT PATE SARA 2000 25KG	1.000	\N	108.3300	108.33	20.00	21.67	130.00	6	6121	Achats de matières premières	1	Appris via l'ICE fournisseur: 000086358000020	f	\N	2026-05-07 13:01:06.839347
178	137	4	VERNIS DIVA NACRE SILVER 100	1.000	\N	54.1700	54.17	20.00	10.83	65.00	6	6121	Achats de matières premières	1	Appris via l'ICE fournisseur: 000086358000020	f	\N	2026-05-07 13:01:06.839347
\.


--
-- Data for Name: lignes_paie; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.lignes_paie (id, bulletin_id, libelle, type_ligne, montant, taux, base_calcul, ordre) FROM stdin;
1	1	Salaire de base	GAIN	5000.00	\N	\N	1
2	1	Prime d'ancienneté	GAIN	250.00	0.0500	\N	2
3	1	Primes/Avantages	GAIN	1000.00	\N	\N	3
4	1	Heures supplémentaires	GAIN	500.00	\N	\N	4
5	1	CNSS salarié (4.48%)	RETENUE	268.80	0.0448	6000.00	10
6	1	AMO salarié (2.26%)	RETENUE	152.55	0.0226	6750.00	11
7	1	IR/IGR retenu	RETENUE	269.06	\N	\N	12
\.


--
-- Data for Name: lignes_releves; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.lignes_releves (id, releve_id, date_operation, date_valeur, description, reference, debit, credit, is_rapproche, rapprochement_type, entry_line_id, created_at) FROM stdin;
1	1	2026-02-06	2026-02-06	TAXE SUR VALEUR AJOUTEE	248575	3.50	0.00	t	\N	361	2026-05-07 19:59:24.888033
2	1	2026-02-06	2026-02-06	VIR. INSTANTANE EN FAVEUR DE OULMEKKI MO HAMED REF 260206248575 DU 20260206	248575	6000.00	0.00	t	\N	363	2026-05-07 19:59:24.888033
3	1	2026-02-06	2026-02-09	VERSEMENT EFFECTUE PAR ABDELKEBIR ATIFI V62229	7XG2P1	0.00	16500.00	t	\N	365	2026-05-07 19:59:24.888033
4	1	2026-02-10	2026-02-10	DROIT DE TIMBRE SUR VERSEMENT	10P6VN	1.00	0.00	t	\N	367	2026-05-07 19:59:24.888033
5	1	2026-02-10	2026-02-10	EFFET N 3100627 REMIS PAR ATW EN FAVEUR DE SEMACDO SARL	100627	5600.00	0.00	t	\N	369	2026-05-07 19:59:24.888033
6	1	2026-02-10	2026-02-11	VERSEMENT EFFECTUE PAR ABDELKEBIR ATIFI V62229	10P6VN	0.00	7400.00	t	\N	371	2026-05-07 19:59:24.888033
7	1	2026-02-11	2026-02-10	COTISATIONS CNSS	260211	1910.24	0.00	t	\N	373	2026-05-07 19:59:24.888033
8	1	2026-02-12	2026-02-12	DROIT DE TIMBRE SUR VERSEMENT	3T5R1R	1.00	0.00	t	\N	375	2026-05-07 19:59:24.888033
11	1	2026-02-16	2026-02-16	DROIT DE TIMBRE SUR VERSEMENT	7F07ZB	1.00	0.00	t	\N	377	2026-05-07 19:59:24.888033
12	1	2026-02-16	2026-02-16	PAIEMENT EFFET N 3100651 EN FAVEUR DE ME BANQUE POPULAIRE	100651	4300.00	0.00	t	\N	379	2026-05-07 19:59:24.888033
13	1	2026-02-16	2026-02-16	EFFET N 2600247 REMIS PAR ATW EN FAVEUR DE LAB SELEC SARL	600247	8900.00	0.00	t	\N	381	2026-05-07 19:59:24.888033
9	1	2026-02-12	2026-02-12	EFFET N 3100642 REMIS PAR ATW EN FAVEUR DE BHF ATLAS PEINTURES	100642	16500.00	0.00	t	\N	383	2026-05-07 19:59:24.888033
10	1	2026-02-12	2026-02-13	VERSEMENT EFFECTUE PAR ABDELKEBIR ATIFI V62229	3T5R1R	0.00	16500.00	t	\N	385	2026-05-07 19:59:24.888033
\.


--
-- Data for Name: mappings_fournisseurs; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.mappings_fournisseurs (id, cabinet_id, supplier_ice, pcm_account_code, created_at, updated_at) FROM stdin;
1	1	999888777	6144	2026-02-24 09:37:57	2026-02-24 09:37:57
2	2	002012861000010	7111	2026-05-07 01:10:50.247007	2026-05-07 01:10:50.247007
3	2	000204969000075	6121	2026-05-07 01:25:57.983739	2026-05-07 01:25:57.983739
4	2	000086358000020	6121	2026-05-07 01:28:12.458176	2026-05-07 01:28:12.458176
5	2	001535246000047	6122	2026-05-07 11:43:11.522938	2026-05-07 11:43:11.522938
6	2	001534521000028	6122	2026-05-07 11:51:12.786948	2026-05-07 11:51:12.786948
\.


--
-- Data for Name: releves_bancaires; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.releves_bancaires (id, societe_id, date_import, date_debut, date_fin, banque_nom, compte_bancaire, solde_initial, solde_final, file_path, file_name, created_at) FROM stdin;
1	6	2026-05-07 19:59:24.869386	2026-02-01	2026-02-28	BANQUE POPULAIRE	127 380 21211 0768289 001 0 55	10164.97	12981.71	/app/uploads/bd9f4661-5dfa-4464-b735-90d1225b4a67.jpg	CamScanner 02-04-2026 08.57_11.jpg	2026-05-07 19:59:24.869386
\.


--
-- Data for Name: societes; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.societes (id, cabinet_id, raison_sociale, ice, if_fiscal, rc, patente, adresse, cnss, logo_path, created_at, updated_at) FROM stdin;
1	1	Ma Societe Test	123456789012345	\N	\N	\N	\N	\N	\N	2026-02-24 09:37:57	2026-02-24 09:37:57
2	2	Ets. EL OUJDI & FILS	001234567890001	12345678	RC-12345	PAT-001	Quartier des Affaires, Casablanca	\N	\N	2026-05-06 12:03:59	2026-05-06 12:03:59
4	3	Entreprise Import-Export	003234567890003	11111111	RC-99999	PAT-003	Port de Casablanca	\N	\N	2026-05-06 12:03:59	2026-05-06 12:03:59
5	2	Entreprise de Test SARL	001234567890001	\N	\N	\N	\N	\N	\N	2026-05-06 12:09:30	2026-05-06 12:09:30
6	2	STE Comptoire Arrahma S.A.R.L	002012861000010	25005226 	2613  	\N	Tamoument 2 N° 17 Avenue La marche Verte -KHENIFRA	\N	\N	2026-05-06 23:45:03.678014	2026-05-06 23:47:59.06903
\.


--
-- Data for Name: utilisateurs_clients; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.utilisateurs_clients (id, societe_id, username, email, password_hash, nom, prenom, is_active, created_at) FROM stdin;
1	6	abdullah@gmail.com	abdullah@gmail.com	852bb51d1f77815d7a8f685085fefe1bc296664595ba79f9f4fdfcb82c570b74$d52c5f9e57f38ef542edb77ab13de9eac9314e6c131c5ca288104a33ca1b8aa4	fathi	abdullah	t	2026-05-07 20:47:12.658082
\.


--
-- Name: action_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.action_logs_id_seq', 261, true);


--
-- Name: agents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.agents_id_seq', 6, true);


--
-- Name: bulletins_paie_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.bulletins_paie_id_seq', 1, true);


--
-- Name: cabinets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.cabinets_id_seq', 4, true);


--
-- Name: compteurs_facturation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.compteurs_facturation_id_seq', 4, true);


--
-- Name: demandes_acces_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.demandes_acces_id_seq', 1, true);


--
-- Name: documents_transmis_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.documents_transmis_id_seq', 1, true);


--
-- Name: ecritures_journal_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.ecritures_journal_id_seq', 168, true);


--
-- Name: employes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.employes_id_seq', 4, true);


--
-- Name: factures_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.factures_id_seq', 142, true);


--
-- Name: immobilisations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.immobilisations_id_seq', 3, true);


--
-- Name: journaux_comptables_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.journaux_comptables_id_seq', 45, true);


--
-- Name: lignes_amortissement_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.lignes_amortissement_id_seq', 25, true);


--
-- Name: lignes_ecritures_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.lignes_ecritures_id_seq', 386, true);


--
-- Name: lignes_factures_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.lignes_factures_id_seq', 183, true);


--
-- Name: lignes_paie_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.lignes_paie_id_seq', 7, true);


--
-- Name: lignes_releves_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.lignes_releves_id_seq', 13, true);


--
-- Name: mappings_fournisseurs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.mappings_fournisseurs_id_seq', 6, true);


--
-- Name: releves_bancaires_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.releves_bancaires_id_seq', 1, true);


--
-- Name: societes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.societes_id_seq', 6, true);


--
-- Name: utilisateurs_clients_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.utilisateurs_clients_id_seq', 1, true);


--
-- Name: action_logs action_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.action_logs
    ADD CONSTRAINT action_logs_pkey PRIMARY KEY (id);


--
-- Name: agents agents_email_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.agents
    ADD CONSTRAINT agents_email_key UNIQUE (email);


--
-- Name: agents agents_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.agents
    ADD CONSTRAINT agents_pkey PRIMARY KEY (id);


--
-- Name: agents_societes agents_societes_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.agents_societes
    ADD CONSTRAINT agents_societes_pkey PRIMARY KEY (agent_id, societe_id);


--
-- Name: agents agents_username_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.agents
    ADD CONSTRAINT agents_username_key UNIQUE (username);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: bulletins_paie bulletins_paie_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.bulletins_paie
    ADD CONSTRAINT bulletins_paie_pkey PRIMARY KEY (id);


--
-- Name: cabinets cabinets_nom_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.cabinets
    ADD CONSTRAINT cabinets_nom_key UNIQUE (nom);


--
-- Name: cabinets cabinets_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.cabinets
    ADD CONSTRAINT cabinets_pkey PRIMARY KEY (id);


--
-- Name: comptes_pcm comptes_pcm_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.comptes_pcm
    ADD CONSTRAINT comptes_pcm_pkey PRIMARY KEY (code);


--
-- Name: compteurs_facturation compteurs_facturation_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.compteurs_facturation
    ADD CONSTRAINT compteurs_facturation_pkey PRIMARY KEY (id);


--
-- Name: demandes_acces demandes_acces_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.demandes_acces
    ADD CONSTRAINT demandes_acces_pkey PRIMARY KEY (id);


--
-- Name: documents_transmis documents_transmis_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.documents_transmis
    ADD CONSTRAINT documents_transmis_pkey PRIMARY KEY (id);


--
-- Name: ecritures_journal ecritures_journal_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.ecritures_journal
    ADD CONSTRAINT ecritures_journal_pkey PRIMARY KEY (id);


--
-- Name: employes employes_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.employes
    ADD CONSTRAINT employes_pkey PRIMARY KEY (id);


--
-- Name: factures factures_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.factures
    ADD CONSTRAINT factures_pkey PRIMARY KEY (id);


--
-- Name: immobilisations immobilisations_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.immobilisations
    ADD CONSTRAINT immobilisations_pkey PRIMARY KEY (id);


--
-- Name: journaux_comptables journaux_comptables_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.journaux_comptables
    ADD CONSTRAINT journaux_comptables_pkey PRIMARY KEY (id);


--
-- Name: lignes_amortissement lignes_amortissement_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lignes_amortissement
    ADD CONSTRAINT lignes_amortissement_pkey PRIMARY KEY (id);


--
-- Name: lignes_ecritures lignes_ecritures_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lignes_ecritures
    ADD CONSTRAINT lignes_ecritures_pkey PRIMARY KEY (id);


--
-- Name: lignes_factures lignes_factures_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lignes_factures
    ADD CONSTRAINT lignes_factures_pkey PRIMARY KEY (id);


--
-- Name: lignes_paie lignes_paie_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lignes_paie
    ADD CONSTRAINT lignes_paie_pkey PRIMARY KEY (id);


--
-- Name: lignes_releves lignes_releves_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lignes_releves
    ADD CONSTRAINT lignes_releves_pkey PRIMARY KEY (id);


--
-- Name: mappings_fournisseurs mappings_fournisseurs_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.mappings_fournisseurs
    ADD CONSTRAINT mappings_fournisseurs_pkey PRIMARY KEY (id);


--
-- Name: releves_bancaires releves_bancaires_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.releves_bancaires
    ADD CONSTRAINT releves_bancaires_pkey PRIMARY KEY (id);


--
-- Name: societes societes_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.societes
    ADD CONSTRAINT societes_pkey PRIMARY KEY (id);


--
-- Name: utilisateurs_clients utilisateurs_clients_email_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.utilisateurs_clients
    ADD CONSTRAINT utilisateurs_clients_email_key UNIQUE (email);


--
-- Name: utilisateurs_clients utilisateurs_clients_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.utilisateurs_clients
    ADD CONSTRAINT utilisateurs_clients_pkey PRIMARY KEY (id);


--
-- Name: utilisateurs_clients utilisateurs_clients_username_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.utilisateurs_clients
    ADD CONSTRAINT utilisateurs_clients_username_key UNIQUE (username);


--
-- Name: ix_action_logs_cabinet_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_action_logs_cabinet_id ON public.action_logs USING btree (cabinet_id);


--
-- Name: ix_action_logs_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_action_logs_id ON public.action_logs USING btree (id);


--
-- Name: ix_agents_cabinet_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_agents_cabinet_id ON public.agents USING btree (cabinet_id);


--
-- Name: ix_agents_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_agents_id ON public.agents USING btree (id);


--
-- Name: ix_agents_societes_agent_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_agents_societes_agent_id ON public.agents_societes USING btree (agent_id);


--
-- Name: ix_agents_societes_societe_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_agents_societes_societe_id ON public.agents_societes USING btree (societe_id);


--
-- Name: ix_bulletins_paie_employe_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_bulletins_paie_employe_id ON public.bulletins_paie USING btree (employe_id);


--
-- Name: ix_bulletins_paie_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_bulletins_paie_id ON public.bulletins_paie USING btree (id);


--
-- Name: ix_cabinets_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_cabinets_id ON public.cabinets USING btree (id);


--
-- Name: ix_compteurs_facturation_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_compteurs_facturation_id ON public.compteurs_facturation USING btree (id);


--
-- Name: ix_compteurs_facturation_societe_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_compteurs_facturation_societe_id ON public.compteurs_facturation USING btree (societe_id);


--
-- Name: ix_demandes_acces_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_demandes_acces_id ON public.demandes_acces USING btree (id);


--
-- Name: ix_documents_transmis_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_documents_transmis_id ON public.documents_transmis USING btree (id);


--
-- Name: ix_documents_transmis_societe_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_documents_transmis_societe_id ON public.documents_transmis USING btree (societe_id);


--
-- Name: ix_ecritures_journal_facture_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_ecritures_journal_facture_id ON public.ecritures_journal USING btree (facture_id);


--
-- Name: ix_ecritures_journal_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_ecritures_journal_id ON public.ecritures_journal USING btree (id);


--
-- Name: ix_ecritures_journal_societe_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_ecritures_journal_societe_id ON public.ecritures_journal USING btree (societe_id);


--
-- Name: ix_employes_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_employes_id ON public.employes USING btree (id);


--
-- Name: ix_employes_societe_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_employes_societe_id ON public.employes USING btree (societe_id);


--
-- Name: ix_factures_file_hash; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_factures_file_hash ON public.factures USING btree (file_hash);


--
-- Name: ix_factures_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_factures_id ON public.factures USING btree (id);


--
-- Name: ix_factures_societe_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_factures_societe_id ON public.factures USING btree (societe_id);


--
-- Name: ix_immobilisations_facture_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_immobilisations_facture_id ON public.immobilisations USING btree (facture_id);


--
-- Name: ix_immobilisations_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_immobilisations_id ON public.immobilisations USING btree (id);


--
-- Name: ix_immobilisations_societe_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_immobilisations_societe_id ON public.immobilisations USING btree (societe_id);


--
-- Name: ix_journaux_comptables_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_journaux_comptables_id ON public.journaux_comptables USING btree (id);


--
-- Name: ix_journaux_comptables_societe_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_journaux_comptables_societe_id ON public.journaux_comptables USING btree (societe_id);


--
-- Name: ix_lignes_amortissement_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_lignes_amortissement_id ON public.lignes_amortissement USING btree (id);


--
-- Name: ix_lignes_amortissement_immobilisation_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_lignes_amortissement_immobilisation_id ON public.lignes_amortissement USING btree (immobilisation_id);


--
-- Name: ix_lignes_ecritures_ecriture_journal_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_lignes_ecritures_ecriture_journal_id ON public.lignes_ecritures USING btree (ecriture_journal_id);


--
-- Name: ix_lignes_ecritures_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_lignes_ecritures_id ON public.lignes_ecritures USING btree (id);


--
-- Name: ix_lignes_factures_facture_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_lignes_factures_facture_id ON public.lignes_factures USING btree (facture_id);


--
-- Name: ix_lignes_factures_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_lignes_factures_id ON public.lignes_factures USING btree (id);


--
-- Name: ix_lignes_paie_bulletin_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_lignes_paie_bulletin_id ON public.lignes_paie USING btree (bulletin_id);


--
-- Name: ix_lignes_paie_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_lignes_paie_id ON public.lignes_paie USING btree (id);


--
-- Name: ix_lignes_releves_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_lignes_releves_id ON public.lignes_releves USING btree (id);


--
-- Name: ix_lignes_releves_releve_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_lignes_releves_releve_id ON public.lignes_releves USING btree (releve_id);


--
-- Name: ix_mappings_fournisseurs_cabinet_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_mappings_fournisseurs_cabinet_id ON public.mappings_fournisseurs USING btree (cabinet_id);


--
-- Name: ix_mappings_fournisseurs_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_mappings_fournisseurs_id ON public.mappings_fournisseurs USING btree (id);


--
-- Name: ix_mappings_fournisseurs_supplier_ice; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_mappings_fournisseurs_supplier_ice ON public.mappings_fournisseurs USING btree (supplier_ice);


--
-- Name: ix_releves_bancaires_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_releves_bancaires_id ON public.releves_bancaires USING btree (id);


--
-- Name: ix_releves_bancaires_societe_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_releves_bancaires_societe_id ON public.releves_bancaires USING btree (societe_id);


--
-- Name: ix_societes_cabinet_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_societes_cabinet_id ON public.societes USING btree (cabinet_id);


--
-- Name: ix_societes_ice; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_societes_ice ON public.societes USING btree (ice);


--
-- Name: ix_societes_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_societes_id ON public.societes USING btree (id);


--
-- Name: ix_utilisateurs_clients_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_utilisateurs_clients_id ON public.utilisateurs_clients USING btree (id);


--
-- Name: ix_utilisateurs_clients_societe_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_utilisateurs_clients_societe_id ON public.utilisateurs_clients USING btree (societe_id);


--
-- Name: action_logs action_logs_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.action_logs
    ADD CONSTRAINT action_logs_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES public.agents(id) ON DELETE SET NULL;


--
-- Name: action_logs action_logs_cabinet_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.action_logs
    ADD CONSTRAINT action_logs_cabinet_id_fkey FOREIGN KEY (cabinet_id) REFERENCES public.cabinets(id) ON DELETE CASCADE;


--
-- Name: agents agents_cabinet_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.agents
    ADD CONSTRAINT agents_cabinet_id_fkey FOREIGN KEY (cabinet_id) REFERENCES public.cabinets(id);


--
-- Name: agents_societes agents_societes_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.agents_societes
    ADD CONSTRAINT agents_societes_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES public.agents(id) ON DELETE CASCADE;


--
-- Name: agents_societes agents_societes_societe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.agents_societes
    ADD CONSTRAINT agents_societes_societe_id_fkey FOREIGN KEY (societe_id) REFERENCES public.societes(id) ON DELETE CASCADE;


--
-- Name: bulletins_paie bulletins_paie_employe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.bulletins_paie
    ADD CONSTRAINT bulletins_paie_employe_id_fkey FOREIGN KEY (employe_id) REFERENCES public.employes(id) ON DELETE CASCADE;


--
-- Name: bulletins_paie bulletins_paie_journal_entry_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.bulletins_paie
    ADD CONSTRAINT bulletins_paie_journal_entry_id_fkey FOREIGN KEY (journal_entry_id) REFERENCES public.ecritures_journal(id);


--
-- Name: compteurs_facturation compteurs_facturation_societe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.compteurs_facturation
    ADD CONSTRAINT compteurs_facturation_societe_id_fkey FOREIGN KEY (societe_id) REFERENCES public.societes(id);


--
-- Name: demandes_acces demandes_acces_cabinet_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.demandes_acces
    ADD CONSTRAINT demandes_acces_cabinet_id_fkey FOREIGN KEY (cabinet_id) REFERENCES public.cabinets(id);


--
-- Name: documents_transmis documents_transmis_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.documents_transmis
    ADD CONSTRAINT documents_transmis_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.utilisateurs_clients(id) ON DELETE SET NULL;


--
-- Name: documents_transmis documents_transmis_facture_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.documents_transmis
    ADD CONSTRAINT documents_transmis_facture_id_fkey FOREIGN KEY (facture_id) REFERENCES public.factures(id);


--
-- Name: documents_transmis documents_transmis_societe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.documents_transmis
    ADD CONSTRAINT documents_transmis_societe_id_fkey FOREIGN KEY (societe_id) REFERENCES public.societes(id) ON DELETE CASCADE;


--
-- Name: ecritures_journal ecritures_journal_facture_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.ecritures_journal
    ADD CONSTRAINT ecritures_journal_facture_id_fkey FOREIGN KEY (facture_id) REFERENCES public.factures(id) ON DELETE CASCADE;


--
-- Name: ecritures_journal ecritures_journal_societe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.ecritures_journal
    ADD CONSTRAINT ecritures_journal_societe_id_fkey FOREIGN KEY (societe_id) REFERENCES public.societes(id);


--
-- Name: employes employes_societe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.employes
    ADD CONSTRAINT employes_societe_id_fkey FOREIGN KEY (societe_id) REFERENCES public.societes(id);


--
-- Name: factures factures_societe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.factures
    ADD CONSTRAINT factures_societe_id_fkey FOREIGN KEY (societe_id) REFERENCES public.societes(id);


--
-- Name: immobilisations immobilisations_facture_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.immobilisations
    ADD CONSTRAINT immobilisations_facture_id_fkey FOREIGN KEY (facture_id) REFERENCES public.factures(id);


--
-- Name: immobilisations immobilisations_societe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.immobilisations
    ADD CONSTRAINT immobilisations_societe_id_fkey FOREIGN KEY (societe_id) REFERENCES public.societes(id);


--
-- Name: journaux_comptables journaux_comptables_societe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.journaux_comptables
    ADD CONSTRAINT journaux_comptables_societe_id_fkey FOREIGN KEY (societe_id) REFERENCES public.societes(id) ON DELETE CASCADE;


--
-- Name: lignes_amortissement lignes_amortissement_immobilisation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lignes_amortissement
    ADD CONSTRAINT lignes_amortissement_immobilisation_id_fkey FOREIGN KEY (immobilisation_id) REFERENCES public.immobilisations(id) ON DELETE CASCADE;


--
-- Name: lignes_ecritures lignes_ecritures_ecriture_journal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lignes_ecritures
    ADD CONSTRAINT lignes_ecritures_ecriture_journal_id_fkey FOREIGN KEY (ecriture_journal_id) REFERENCES public.ecritures_journal(id) ON DELETE CASCADE;


--
-- Name: lignes_factures lignes_factures_facture_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lignes_factures
    ADD CONSTRAINT lignes_factures_facture_id_fkey FOREIGN KEY (facture_id) REFERENCES public.factures(id) ON DELETE CASCADE;


--
-- Name: lignes_paie lignes_paie_bulletin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lignes_paie
    ADD CONSTRAINT lignes_paie_bulletin_id_fkey FOREIGN KEY (bulletin_id) REFERENCES public.bulletins_paie(id) ON DELETE CASCADE;


--
-- Name: lignes_releves lignes_releves_entry_line_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lignes_releves
    ADD CONSTRAINT lignes_releves_entry_line_id_fkey FOREIGN KEY (entry_line_id) REFERENCES public.lignes_ecritures(id) ON DELETE SET NULL;


--
-- Name: lignes_releves lignes_releves_releve_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lignes_releves
    ADD CONSTRAINT lignes_releves_releve_id_fkey FOREIGN KEY (releve_id) REFERENCES public.releves_bancaires(id) ON DELETE CASCADE;


--
-- Name: mappings_fournisseurs mappings_fournisseurs_cabinet_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.mappings_fournisseurs
    ADD CONSTRAINT mappings_fournisseurs_cabinet_id_fkey FOREIGN KEY (cabinet_id) REFERENCES public.cabinets(id);


--
-- Name: releves_bancaires releves_bancaires_societe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.releves_bancaires
    ADD CONSTRAINT releves_bancaires_societe_id_fkey FOREIGN KEY (societe_id) REFERENCES public.societes(id);


--
-- Name: societes societes_cabinet_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.societes
    ADD CONSTRAINT societes_cabinet_id_fkey FOREIGN KEY (cabinet_id) REFERENCES public.cabinets(id);


--
-- Name: utilisateurs_clients utilisateurs_clients_societe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.utilisateurs_clients
    ADD CONSTRAINT utilisateurs_clients_societe_id_fkey FOREIGN KEY (societe_id) REFERENCES public.societes(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict 0njt2Zz3tL4miRVVHxCvIFDxe065vm7d1QcJG8gmxjEfEdBx4agE7X6uR1QTeML

