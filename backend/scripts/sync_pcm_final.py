import re
from database import SessionLocal
from models import PcmAccount

# Le texte brut fourni par l'utilisateur
RAW_PCM_TEXT = """
CLASSE 1 : COMPTES DE FINANCEMENT PERMANENT 
11 CAPITAUX PROPRES 
111 Capital social ou personnel 
1111 Capital social 
1112 Fonds de dotation 
1117 Capital personnel 
11171 Capital individuel 
11175 Compte de l'exploitant 
1119 Actionnaires, capital souscrit-non appelé 
112 Primes d'émission, de fusion et d'apport 
1121 Primes d'émission 
1122 Primes de fusion 
1123 Primes d'apport 
113 Ecarts de réévaluation 
1130 Ecarts de réévaluation 
114 Réserve légale 
1140 Réserve légale 
115 Autres réserves 
1151 Réserves statutaires ou contractuelles 
1152 Réserves facultatives 
1155 Réserves réglementées 
116 Report à nouveau 
1161 Report à nouveau (solde créditeur) 
1169 Report à nouveau (solde débiteur) 
118 Résultats nets en instance d'affectation 
1181 Résultats nets en instance d'affectation (solde créditeur) 
1189 Résultats nets en instance d'affectation (solde débiteur) 
119 Résultat net de l'exercice 
1191 Résultat net de l'exercice (solde créditeur) 
1199 Résultat net de l'exercice (solde débiteur) 
13 CAPITAUX PROPRES ASSIMILES 
131 Subventions d'investissement 
1311 Subventions d'investissement reçues 
1319 Subventions d'investissement inscrites au CPC 
135 Provisions réglementées 
1351 Provisions pour amortissements dérogatoires 
1352 Provisions pour plus-values en instance d'imposition 
1354 Provisions pour investissements 
1355 Provisions pour reconstitution des gisements 
1356 Provisions pour acquisition et construction de logements 
1358 Autres provisions réglementées 
14 DETTES DE FINANCEMENT 
141 Emprunts obligataires 
1410 Emprunts obligataires 
148 Autres dettes de financement 
1481 Emprunts auprès des établissements de crédit 
1482 Avances de l'Etat 
1483 Dettes rattachées à des participations 
1484 Billets de fonds 
1485 Avances reçues et comptes courants bloqués 
1486 Fournisseurs d'immobilisation 
1487 Dépôts et cautionnements reçues 
1488 Dettes de financement diverses 
15 Provisions durables pour risques et charges 
151 Provisions pour risques 
1511 Provisions pour litiges 
1512 Provisions pour garanties données aux clients 
1513 Provisions pour propre assureur 
1514 Provision pour pertes sur marchés à terme 
1515 Provisions pour amendes, double droits, pénalités 
1516 Provisions pour pertes de change 
1518 Autres provisions pour risques 
155 Provisions pour charges 
1551 Provisions pour impôts 
1552 Provisions pour pensions de retraite et obligations similaires 
1555 Provisions pour charges à répartir sur plusieurs exercices 
1558 Autres provisions pour charges 
16 COMPTES DE LIAISON DES ETABLISSEMENTS ET SUCCURSALES 
160 Comptes de liaison des établissements et succursales 
1601 Comptes de liaison du siège 
1605 Comptes de liaison des établissements 
17 Ecarts de conversion - Passif 
171 Augmentation des créances immobilisées 
1710 Augmentation des créances immobilisées 
172 Diminution des dettes de financement 
1720 Diminution des dettes de financement 
21 IMMOBILISATIONS EN NON-VALEURS 
211 Frais préliminaires 
2111 Frais de constitution 
2112 Frais préalables au démarrage 
2113 Frais d'augmentation du capital 
2114 Frais sur opérations de fusions, scissions et transformations 
2116 Frais de prospection 
2117 Frais de publicité 
2118 Autres frais préliminaires 
212 Charges à répartir sur plusieurs exercices 
2121 Frais d'acquisitition des immobilisations 
2125 Frais d'émission des emprunts 
2128 Autres charges à répartir 
213 Primes de remboursement des obligations 
2130 Primes de remboursement des obligations 
22 IMMOBILISATIONS INCORPORELLES 
221 Immobilisation en recherche et développement 
2210 Immobilisation en recherche et développement 
222 Brevets, marques, droits et valeurs similaires 
2220 Brevets, marques, droits et valeurs similaires 
223 Fonds commercial 
2230 Fonds commercial 
228 Autres immobilisations incorporelles 
2285 Autres immobilisations incorporelles 
23 IMMOBILISATIONS CORPORELLES 
231 Terrains 
2311 Terrains nus 
2312 Terrains aménagés 
2313 Terrains bâtis 
2314 Terrains de gisement 
2316 Agencements et aménagements de terrains 
2318 Autres terrains 
232 Constructions 
2321 Bâtiments 
23211 Bâtiments industriels 
23214 Bâtiments administratifs et commerciaux 
23218 Autres bâtiments 
2323 Constructions sur terrains d'autrui 
2325 Ouvrages d'infrastructure 
2327 Agencements et aménagements des constructions 
2328 Autres constructions 
233 Installations techniques, matériel et outillage 
2331 Installations techniques 
2332 Matériel et outillage 
23321 Matériel 
23324 Outillage 
2333 Emballages récupérables identifiables 
2338 Autres installations techniques, matériel et outillage 
234 Matériel de transport 
2340 Matériel de transport 
235 Mobilier, matériel de bureau et aménagements divers 
2351 Mobilier de bureau 
2352 Matériel de bureau 
2355 Matériel informatique 
2356 Agencements, installations et aménagements divers 
2358 Autres mobilier, matériel de bureau et aménagements divers 
238 Autres immobilisations corporelles 
2380 Autres immobilisations corporelles 
239 Immobilisations corporelles en cours 
2392 Immobilisations corporelles en cours des terrains et constructions 
2393 Immobilisations corporelles en cours des installations techniques, matériel et outillage 
2394 Immobilisations corporelles en cours de matériel de transport 
2395 Immobilisations corporelles en cours de mobilier, matériel de bureau et aménagements divers 
2397 Avances et acomptes versés sur commandes d'immobilisations corporelles 
2398 Autres immobilisations corporelles en cours 
241 Prêts immobilsés 
2441 Prêts au personnel 
2415 Prêts aux associés 
2416 Billets de fonds 
2418 Autres prêts 
248 Autres créances financières 
2481 Titres immobilisés (droits de créance) 
24811 Obligations 
24813 Bons d'équipement 
24818 Bons divers 
2483 Créances rattachées à des participations 
2486 Dépôts et cautionnements versés 
24861 Dépôts 
24864 Cautionnements 
2487 Créances immobilisées 
2488 Créances financères diverses 
251 Titres de participation 
2510 Titres de participation 
258 Autres titres immobilisés 
2581 Actions 
2588 Titres divers 
271 Diminution des créances immobilisées 
2710 Diminution des créances immobilisées 
272 Augmentation des dettes de financement 
2720 Augmentation des dettes de financement 
281 Amortissements des non-valeurs 
2811 Amortissements des frais préliminaires 
28111 Amortissements des frais de constitution 
28112 Amortissements des frais préliminaires au démarrage 
28113 Amortissements des frais d'augmentation du capital 
28114 Amortissements des frais sur opérations de fusions, scissions, et transformations 
28116 Amortissements des frais de prospection 
28117 Amortissements des frais de publicité 
28118 Amortissements des autres frais préliminaires 
2812 Amortissements des charges à répartir 
28121 Amortissements des frais d'acquisition des immobilisations 
28125 Amortissements des frais d'émission des emprunts 
28128 Amortissements des autres charges à répartir 
2813 Amortissements des primes de remboursement des obligations 
2821 Amortissements de l'immobilisation en recherche et développement 
2822 Amortissements des brevets, marques, droits et valeurs similaires 
2823 Amortissements du fonds commercial 
2828 Amortissements des autres immobilisations incorporelles 
2831 Amortissements des terrains 
28311 Amortissements des terrains nus 
28312 Amortissements des terrains aménagés 
28313 Amortissements des terrains bâtis 
28314 Amortissements des terrains de gisement 
28316 Amortissements des agencements et aménagements de terrains 
28318 Amortissements des autres terrains 
2832 Amortissements des constructions 
28321 Amortissements des bâtiments 
28323 Amortissements des constructions sur terrains d'autrui 
28325 Amortissements des ouvrages d'infrastructure 
28327 Amortissements des installations, agencements et aménagements des constructions 
28328 Amortissements des autres constructions 
2833 Amortissements des installations techniques, matériel et outillage 
28331 Amortissements des installations techniques 
28332 Amortissements du matériel et outillage 
28333 Amortissements des emballages récupérables identifiables 
28338 Amortissements des autres installations techniques, matériel et outillage 
2834 Amortissements du matériel de transport 
2835 Amortissements du mobilier, matériel de bureau et aménagements divers 
28351 Amortissements du mobilier de bureau 
28352 Amortissements du matériel de bureau 
28355 Amortissements du matériel informatique 
28356 Amortissements des agencements, installations et aménagements divers 
28358 Amortissements des autres mobilier, matériel de bureau et aménagements divers 
2838 Amortissements des autres immobilisations corporelles 
2920 Provisions pour dépréciation des immobilisations incorporelles 
2930 Provisions pour dépréciation des immobilisations corporelles 
2941 Provisions pour dépréciation des prêts immobilisés 
2948 Provisions pour dépréciation des autres créances financières 
2951 Provisions pour dépréciation des titres de participation 
2958 Provisions pour dépréciation des autres titres immobilisés 
3111 Marchandises 
3121 Matières premières 
3122 Matières et fournitures consommables 
31227 Fournitures de bureau 
3123 Emballages 
3151 Produits finis 
3411 Fournisseurs - avances et acomptes versés sur commandes d'exploitation 
3421 Clients 
3425 Clients - effets à recevoir 
3431 Avances et acomptes au personnel 
3451 Subventions à recevoir 
3453 Acomptes sur impôts sur les résultats 
3455 Etat - TVA récupérable 
34551 Etat - TVA récupérable sur immobilisations 
34552 Etat - TVA récupérable sur charges 
3456 Etat - crédit de TVA 
3461 Associés - comptes d'apport en société 
3463 Comptes courants des associés débiteurs 
3481 Créances sur cessions d'immobilisations 
3491 Charges constatées d'avance 
3501 Actions, partie libérée 
3504 Obligations 
4411 Fournisseurs 
4413 Fournisseurs - retenues de garantie 
4415 Fournisseurs - effets à payer 
4417 Fournisseurs - factures non parvenues 
4421 Clients - avances et acomptes reçus sur commandes en cours 
4432 Rémunérations dues au personnel 
4434 Oppositions sur salaires 
4441 Caisse Nationale de la Sécurité Sociale 
4443 Caisses de retraite 
4445 Mutuelles 
4447 Charges sociales à payer 
4448 Autres organismes sociaux 
4452 Etat - Impôts, taxes et assimilés 
44525 Etat - IGR 
4455 Etat - TVA facturée 
4456 Etat - TVA due 
4463 Comptes courants des associés créditeurs 
4481 Dettes sur acquisitions d'immobilisations 
4491 Produits constatés d'avance 
5111 Chèques à encaisser ou à l'encaissement 
5141 Banques (solde débiteur) 
5161 Caisses 
5541 Banques (solde créditeur) 
6111 Achats de marchandises 
6114 Variation de stocks de marchandises 
6119 Rabais, remises et ristournes obtenus sur achats de marchandises 
6121 Achats de matières premières 
6122 Achats de matières et fournitures consommables 
6124 Variation des stocks de matières et fournitures 
61251 Achats de fournitures non stockables (eau, électricité) 
61252 Achats de fournitures d'entretien 
61254 Achats de fournitures de bureau 
61311 Locations de terrains 
61312 Locations de constructions 
61313 Locations de matériel et d'outillage 
61331 Entretien et réparations des biens immobiliers 
61341 Assurances multirisque 
61361 Commissions et courtages 
61365 Honoraires 
61411 Etudes générales 
61421 Transports du personnel 
61431 Voyages et déplacements 
61441 Annonces et insertions 
61455 Frais de téléphone 
61473 Frais et commisions sur services bancaires 
61612 Patente 
61671 Droits d’enregistrement et de timbre 
61711 Appointements et salaires 
61741 Cotisations de sécurité sociale 
61742 Cotisations aux caisses de retraite 
61743 Cotisations aux mutuelles 
6181 Jetons de présence 
61933 D.E.A. des installations techniques, matériel et outillage 
61934 D.E.A. du matériel de transport 
61935 D.E.A. des mobiliers, matériels de bureau et aménagements divers 
7111 Ventes de marchandises au Maroc 
7113 Ventes de marchandises à l’étranger 
71211 Ventes de produits finis 
71243 Prestations de services 
"""

def parse_and_sync():
    db = SessionLocal()
    lines = RAW_PCM_TEXT.strip().split('\n')
    
    count = 0
    pattern = re.compile(r'^(\d{3,5})\s+(.+)$')
    
    try:
        for line in lines:
            line = line.strip()
            match = pattern.match(line)
            if match:
                code = match.group(1)
                label = match.group(2).strip()
                pcm_class = int(code[0])
                
                # Déterminer le type (logique simplifiée mais robuste)
                acc_type = "BILAN"
                if code.startswith('6'): acc_type = "CHARGE"
                elif code.startswith('7'): acc_type = "PRODUIT"
                elif code.startswith('3') or code.startswith('4'): acc_type = "TIERS"
                
                acc = db.query(PcmAccount).filter(PcmAccount.code == code).first()
                if acc:
                    if acc.label != label:
                        print(f"MAJ {code}: {acc.label} -> {label}")
                        acc.label = label
                        acc.account_type = acc_type
                        count += 1
                else:
                    print(f"ADD {code}: {label}")
                    db.add(PcmAccount(
                        code=code, label=label, pcm_class=pcm_class, account_type=acc_type
                    ))
                    count += 1
        
        db.commit()
        print(f"--- SYNCHRONISATION TERMINÉE : {count} modifications ---")
    except Exception as e:
        db.rollback()
        print(f"ERREUR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    parse_and_sync()
