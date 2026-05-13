"""Génère 20 appels d'offres IT réalistes (8-15 pages chacun) dans docs/."""

import random
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

BLUE_DARK = HexColor("#1a3a5c")
BLUE_MED  = HexColor("#2e6da4")
GRAY_LIGHT = HexColor("#f0f4f8")
GRAY_MED   = HexColor("#cccccc")

OUTPUT_DIR = Path("docs")
OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Données
# ---------------------------------------------------------------------------

PROJECTS = [
    {
        "type": "ERP", "num": 1,
        "title": "Déploiement d'un progiciel de gestion intégré (ERP) Microsoft Dynamics 365",
        "domain": "Gestion d'entreprise et finances",
        "context": (
            "La structure fait face à une hétérogénéité de ses systèmes d'information, "
            "avec des applications métier cloisonnées ne communiquant pas entre elles. "
            "Le système actuel, vieux de plus de 12 ans, génère des saisies redondantes, "
            "des erreurs de consolidation financière et un manque de visibilité sur les "
            "indicateurs de performance clés. La direction a acté la nécessité d'une "
            "refonte complète du SI de gestion pour répondre aux enjeux de transformation "
            "numérique et d'efficience opérationnelle fixés par le plan stratégique 2026-2030."
        ),
        "reqs": [
            "Modules comptabilité générale et analytique, achats, ventes, stocks, RH et paie",
            "Portail self-service collaborateurs pour notes de frais, congés et absences",
            "Intégration native Microsoft 365 (Teams, SharePoint, Outlook, Power Platform)",
            "Tableau de bord décisionnel avec Power BI embedded et exports automatisés",
            "API REST pour interfaçage avec les applications métier existantes (8 connecteurs)",
            "Reprise des données historiques sur 7 années avec validation et réconciliation",
            "Formation des utilisateurs clés (50 personnes) et des administrateurs (5 personnes)",
            "SLA de disponibilité 99,5% en heures ouvrées avec astreinte 24/7 pour le N3",
            "Conformité au plan comptable public M57 et interopérabilité Chorus Pro",
        ],
        "constraints": [
            "Hébergement en cloud souverain certifié SecNumCloud ou HDS",
            "Respect du RGPD pour les données RH (données sensibles catégorie 9 RGPD)",
            "Interopérabilité avec la plateforme de dématérialisation Chorus Pro",
            "Accompagnement conduite du changement pour 320 agents impactés",
        ],
        "lots": [("Lot 1", "Licence, paramétrage et infrastructure ERP", 42),
                 ("Lot 2", "Migration et reprise des données historiques", 18),
                 ("Lot 3", "Formation et conduite du changement", 20),
                 ("Lot 4", "Maintenance évolutive et support N3 (3 ans)", 20)],
        "criteria": [("Valeur technique de l'offre", 50), ("Prix global", 30),
                     ("Qualité du planning et méthodologie projet", 12), ("Références similaires", 8)],
        "phases": [("Phase 1 – Cadrage et paramétrage", 3), ("Phase 2 – Recette et formation", 3),
                   ("Phase 3 – Déploiement et run", 6)],
    },
    {
        "type": "CRM", "num": 2,
        "title": "Acquisition et déploiement d'une solution CRM et gestion de la relation usager",
        "domain": "Gestion de la relation client et usager",
        "context": (
            "Dans le cadre de sa stratégie de modernisation de l'accueil et du service aux usagers, "
            "la structure souhaite se doter d'un outil CRM permettant de centraliser l'ensemble "
            "des interactions multicanales (téléphone, courriel, guichet, application mobile). "
            "Le volume traité est estimé à 18 000 contacts actifs et 2 500 demandes mensuelles. "
            "Le taux de satisfaction actuel de 61% est bien en deçà de l'objectif de 85% "
            "fixé par la direction générale pour l'exercice 2027."
        ),
        "reqs": [
            "Gestion des contacts, comptes et historique des interactions sur 5 ans",
            "Suivi des tickets et demandes usagers avec workflow d'escalade paramétrable",
            "Portail usager en ligne avec authentification France Connect niveau substantiel",
            "Intégration téléphonie CTI et messagerie (Outlook, webmail)",
            "Reporting et tableaux de bord personnalisables par profil",
            "Application mobile iOS/Android pour les agents terrain",
            "Import/export des données au format CSV, XML et JSON (open data)",
            "Archivage légal des échanges selon durées légales (RGPD Article 17)",
            "Accessibilité RGAA niveau AA pour le portail usager",
        ],
        "constraints": [
            "Données hébergées exclusivement en France (RGPD)",
            "Authentification SSO via SAML 2.0 sur l'AD existant",
            "Temps de réponse < 2 secondes pour 95% des requêtes en charge nominale",
            "Formation de 80 agents utilisateurs et 5 administrateurs fonctionnels",
        ],
        "lots": [("Lot 1", "Licence CRM et infrastructure cloud", 38),
                 ("Lot 2", "Paramétrage, développements spécifiques et workflows", 32),
                 ("Lot 3", "Intégrations SI et connecteurs téléphonie", 15),
                 ("Lot 4", "Support et maintenance évolutive (2 ans)", 15)],
        "criteria": [("Adéquation fonctionnelle avec les besoins", 45), ("Prix total", 30),
                     ("Ergonomie et expérience utilisateur", 15), ("Références secteur public", 10)],
        "phases": [("Phase 1 – Configuration et paramétrage", 4), ("Phase 2 – Tests et recette", 2),
                   ("Phase 3 – Déploiement et accompagnement", 3)],
    },
    {
        "type": "CYBERSÉCURITÉ", "num": 3,
        "title": "Mise en place d'un SOC managé (Security Operations Center) 24/7",
        "domain": "Cybersécurité et surveillance des systèmes",
        "context": (
            "Face à la recrudescence des cyberattaques visant les organismes publics et de santé "
            "(hausse de 148% en 2023 selon l'ANSSI), et suite à deux incidents de sécurité "
            "internes au cours des 18 derniers mois, la structure a décidé de renforcer "
            "sa posture de cybersécurité en s'appuyant sur un SOC externalisé. "
            "L'absence d'un SIEM opérationnel, la non-supervision des équipements réseau "
            "et l'absence de procédure de réponse aux incidents ont été identifiées comme "
            "vulnérabilités critiques lors de l'audit ANSSI conduit en mars 2025."
        ),
        "reqs": [
            "Déploiement et gestion d'un SIEM nouvelle génération (Splunk, Microsoft Sentinel ou équivalent)",
            "Surveillance 24/7/365 avec centre opérationnel de sécurité certifié PDIS",
            "Collecte et corrélation des logs (AD, firewalls, endpoints, serveurs, cloud)",
            "Détection des menaces avec threat intelligence intégrée (IOC, TTP MITRE ATT&CK)",
            "Réponse à incidents avec playbooks SOAR automatisés et astreinte de crise",
            "Rapport mensuel de sécurité et tableau de bord RSSI",
            "Audit de vulnérabilités trimestriel et test d'intrusion annuel",
            "Accompagnement PSSI et plan de sensibilisation des 420 utilisateurs",
        ],
        "constraints": [
            "Prestataire certifié PRIS (Prestataire de Réponse aux Incidents de Sécurité) ANSSI",
            "Analystes sécurité de niveau minimum N3 avec habilitation confidentiel défense",
            "SIEM hébergé sur territoire français ou cloud souverain",
            "Temps de détection < 30 minutes et notification < 1h pour incidents P1",
        ],
        "lots": [("Lot 1", "SOC managé 24/7 et SIEM", 58),
                 ("Lot 2", "Audit de vulnérabilités et tests d'intrusion", 22),
                 ("Lot 3", "Formation et sensibilisation utilisateurs", 10),
                 ("Lot 4", "Gouvernance sécurité et conformité ANSSI", 10)],
        "criteria": [("Capacités techniques SOC et certifications", 50), ("Prix annuel", 28),
                     ("Délais de détection et réponse contractualisés", 12), ("Expérience sectorielle", 10)],
        "phases": [("Phase 1 – Intégration et collecte des logs", 2), ("Phase 2 – Tuning et baseline", 2),
                   ("Phase 3 – Run SOC nominal", 36)],
    },
    {
        "type": "CLOUD AZURE", "num": 4,
        "title": "Migration de l'infrastructure on-premise vers Microsoft Azure (IaaS/PaaS)",
        "domain": "Infrastructure cloud et migration",
        "context": (
            "La structure exploite actuellement un datacenter on-premise hébergeant 48 serveurs "
            "physiques (dont 35 virtualisés sous VMware vSphere 6.5), des baies de stockage SAN "
            "et des équipements réseau en fin de vie dont les contrats de maintenance expirent "
            "dans 14 mois. Le coût de renouvellement estimé à 1,8M€ et la difficulté de maintenir "
            "des compétences techniques en interne ont conduit à la décision stratégique "
            "de migrer l'intégralité des workloads vers Microsoft Azure sur 18 mois."
        ),
        "reqs": [
            "Assessment complet de l'existant avec Azure Migrate et TCO Analysis",
            "Architecture cible hybride (IaaS/PaaS) et roadmap de migration par vagues",
            "Migration des 35 VMs avec stratégie Lift & Shift puis Refactoring",
            "Connectivité hybride sécurisée (Azure ExpressRoute 1 Gbps)",
            "Microsoft Entra ID, Conditional Access et architecture Zero Trust",
            "Stratégie de sauvegarde (Azure Backup) et PRA inter-régions",
            "FinOps : optimisation continue des coûts avec Azure Cost Management",
            "Formation Azure Administrator (AZ-104) pour 4 techniciens",
        ],
        "constraints": [
            "Données hébergées exclusivement en région Azure France Central et France South",
            "RTO < 4h et RPO < 1h pour les 10 applications critiques",
            "Titulaire certifié Microsoft Solutions Partner (Infrastructure Azure)",
            "Interruption de service < 2h par workload lors de la migration",
        ],
        "lots": [("Lot 1", "Assessment, architecture et POC", 8),
                 ("Lot 2", "Migration infrastructure et workloads", 52),
                 ("Lot 3", "Sécurité, gouvernance et FinOps", 22),
                 ("Lot 4", "Formation et transfert de compétences", 18)],
        "criteria": [("Méthodologie de migration et gestion des risques", 45), ("Prix global", 32),
                     ("Certifications Microsoft et références", 13), ("Planning proposé", 10)],
        "phases": [("Phase 1 – Assessment et architecture", 2), ("Phase 2 – Vague 1 (apps non critiques)", 4),
                   ("Phase 3 – Vague 2 (apps critiques)", 6), ("Phase 4 – Optimisation et formation", 4)],
    },
    {
        "type": "IA & ML", "num": 5,
        "title": "Déploiement d'une plateforme d'intelligence artificielle et d'analyse prédictive",
        "domain": "Intelligence artificielle et data science",
        "context": (
            "Dans le cadre de sa feuille de route data 2025-2028, la structure souhaite "
            "exploiter ses gisements de données pour développer des capacités d'analyse prédictive "
            "et d'aide à la décision. Les cas d'usage prioritaires identifiés incluent : "
            "la prévision de la demande à J+30 et J+90, l'optimisation automatique des plannings, "
            "la détection d'anomalies financières en temps réel et l'analyse prédictive de la "
            "maintenance des équipements. Le volume de données traitées est estimé à 800 Go/mois."
        ),
        "reqs": [
            "Plateforme MLOps (Azure ML, Databricks ou équivalent) avec CI/CD des modèles",
            "Pipeline de données ELT automatisé avec orchestration (Apache Airflow)",
            "Data lake Azure Data Lake Storage Gen2 avec gouvernance (Purview)",
            "Développement des 4 cas d'usage IA prioritaires avec documentation",
            "Interface de visualisation et d'explication (XAI – SHAP, LIME)",
            "API d'inférence REST temps réel (< 100ms) et batch",
            "Catalogue de données avec dictionnaire métier",
            "Conformité IA Act européen (classification, documentation, biais)",
        ],
        "constraints": [
            "Données personnelles anonymisées ou pseudonymisées avant entraînement",
            "Explicabilité obligatoire des décisions algorithmiques impactant des personnes",
            "Documentation conforme aux exigences de l'IA Act (catégorie haut risque)",
            "Propriété intellectuelle des modèles transférée au donneur d'ordre",
        ],
        "lots": [("Lot 1", "Plateforme data et infrastructure IA/MLOps", 33),
                 ("Lot 2", "Développement des 4 modèles ML prioritaires", 37),
                 ("Lot 3", "Interfaces métier et intégrations", 20),
                 ("Lot 4", "Maintenance, monitoring et amélioration continue", 10)],
        "criteria": [("Qualité technique et maturité IA de l'offre", 48), ("Prix global", 28),
                     ("Explicabilité et conformité IA Act", 14), ("Expérience data science sectorielle", 10)],
        "phases": [("Phase 1 – Data engineering et gouvernance", 3), ("Phase 2 – Développement modèles", 6),
                   ("Phase 3 – Intégration et mise en production", 3)],
    },
    {
        "type": "HELPDESK ITSM", "num": 6,
        "title": "Externalisation du support informatique N1/N2 et déploiement d'un outil ITSM",
        "domain": "Support utilisateurs et gestion des services IT",
        "context": (
            "La structure dispose d'un parc informatique de 920 postes répartis sur 7 sites. "
            "L'équipe informatique interne (5 personnes) n'est plus en mesure d'assurer "
            "le support de niveau 1 et 2 dans des délais acceptables. Le délai moyen de "
            "résolution des incidents est actuellement de 3,2 jours contre un objectif de 4 heures. "
            "Le taux de satisfaction des utilisateurs est de 58% selon l'enquête conduite en 2025. "
            "L'absence d'outil ITSM structuré entraîne une perte d'information et un manque "
            "de traçabilité des demandes."
        ),
        "reqs": [
            "Service desk externalisé avec plage horaire 7h30-19h30, lundi au vendredi",
            "Astreinte téléphonique P1 24/7 pour incidents bloquants",
            "Outil ITSM conforme ITIL v4 (incidents, demandes, changements, actifs, CMDB)",
            "Prise en main à distance sécurisée chiffrée des postes utilisateurs",
            "Base de connaissances collaborative et portail libre-service",
            "Gestion automatique du parc (inventaire, déploiement, patching WSUS/MECM)",
            "Rapports mensuels avec KPI : TRT, TRS, CSAT, taux de résolution N1",
            "Intégration Active Directory, Microsoft 365 et téléphonie",
        ],
        "constraints": [
            "TRT moyen < 4h pour incidents bloquants (P1/P2), < 24h pour P3",
            "Taux de résolution au premier appel (FCR) > 72%",
            "Disponibilité de l'outil ITSM 99,9% (hors maintenance programmée)",
            "Agents titulaires de la certification ITIL 4 Foundation minimum",
        ],
        "lots": [("Lot 1", "Service desk externalisé N1 et N2", 52),
                 ("Lot 2", "Outil ITSM, licences et infrastructure", 22),
                 ("Lot 3", "Gestion du parc et MCO postes de travail", 26)],
        "criteria": [("Qualité du service desk et des engagements SLA", 48), ("Prix global annuel", 32),
                     ("Ergonomie de l'outil ITSM", 12), ("Références clients similaires", 8)],
        "phases": [("Phase 1 – Déploiement outil et formation", 2), ("Phase 2 – Run progressif (70% des tickets)", 2),
                   ("Phase 3 – Run nominal et optimisation", 24)],
    },
    {
        "type": "RÉSEAU LAN/WAN", "num": 7,
        "title": "Refonte de l'infrastructure réseau LAN/WAN et WiFi multi-sites (8 sites)",
        "domain": "Infrastructure réseau et télécommunications",
        "context": (
            "L'infrastructure réseau actuelle est hétérogène, constituée d'équipements "
            "de trois générations différentes (Cisco 2010, HP Aruba 2015, D-Link 2018). "
            "Les performances sont insuffisantes pour les nouveaux usages numériques "
            "(visioconférence 4K, cloud Azure, IoT bâtiment, 280 terminaux mobiles). "
            "La supervision est quasi inexistante, rendant la détection des pannes réactive "
            "et non proactive. Les 8 sites sont interconnectés par des liaisons MPLS "
            "dont les contrats arrivent à échéance dans 16 mois."
        ),
        "reqs": [
            "Architecture réseau cœur redondante 25/100 Gbps avec spanning tree MSTP",
            "Déploiement WiFi 6E (802.11ax) avec contrôleur centralisé cloud-managed",
            "SD-WAN pour l'interconnexion sécurisée et résiliente des 8 sites",
            "Microsegmentation VLAN et politique de sécurité Zero Trust Network Access",
            "NMS (Network Management System) avec alertes proactives et cartographie",
            "Pare-feux NGFW avec inspection SSL, IPS/IDS et filtrage URL",
            "QoS prioritaire pour la VoIP, la visioconférence et les flux critiques",
            "Documentation complète : schémas réseau, plans d'adressage, procédures",
        ],
        "constraints": [
            "Mise en service sans interruption du service > 4h consécutives par site",
            "Garantie matérielle Next Business Day pendant 5 ans minimum",
            "Constructeur unique pour les équipements LAN (cohérence opérationnelle)",
            "Rapport de bilan carbone et efficacité énergétique des équipements fourni",
        ],
        "lots": [("Lot 1", "Équipements actifs réseau LAN (switches, routeurs)", 38),
                 ("Lot 2", "Infrastructure WiFi 6E et contrôleurs", 22),
                 ("Lot 3", "SD-WAN et connectivité WAN (opérateur inclus)", 25),
                 ("Lot 4", "Supervision réseau, sécurité et NGFW", 15)],
        "criteria": [("Performance technique et architecture proposée", 50), ("Prix global", 28),
                     ("Garanties et SLA de maintenance", 12), ("Références multi-sites similaires", 10)],
        "phases": [("Phase 1 – Audit et conception détaillée", 2), ("Phase 2 – Déploiement sites pilotes (2 sites)", 3),
                   ("Phase 3 – Déploiement généralisé (6 sites)", 5)],
    },
    {
        "type": "RGPD / DPO", "num": 8,
        "title": "Accompagnement à la conformité RGPD et désignation d'un DPO mutualisé externalisé",
        "domain": "Conformité réglementaire et protection des données personnelles",
        "context": (
            "Depuis l'entrée en vigueur du RGPD en mai 2018, la structure n'a pas formalisé "
            "sa mise en conformité. Un audit interne conduit en 2025 a identifié des lacunes "
            "majeures : absence de registre des traitements à jour, clauses sous-traitants "
            "non conformes à l'Article 28, absence de procédure de réponse aux violations "
            "et de traitement des exercices de droits. La CNIL a adressé un questionnaire "
            "de contrôle auquel la structure doit répondre dans un délai de 90 jours."
        ),
        "reqs": [
            "Audit complet de conformité RGPD avec scoring par domaine (sur 500 points)",
            "Rédaction et implémentation du registre des traitements (42 traitements identifiés)",
            "Réalisation de 6 Analyses d'Impact sur la Protection des Données (AIPD)",
            "Mise à jour de toutes les mentions légales, CGU et politiques de confidentialité",
            "Formation des référents RGPD internes (DPD délégué + 12 correspondants métier)",
            "Procédures opérationnelles : droits des personnes, violations, sous-traitants",
            "Rédaction des clauses Article 28 RGPD pour les 34 sous-traitants identifiés",
            "Tableau de bord de conformité avec feuille de route priorisée",
        ],
        "constraints": [
            "DPO désigné répondant aux critères de l'Article 37 RGPD (indépendance, expertise)",
            "Confidentialité absolue sur l'ensemble des données et traitements examinés",
            "Droit français et européen applicable (loi Informatique et Libertés modifiée)",
            "Délai d'intervention < 72h pour signalement de violation de données",
        ],
        "lots": [("Lot 1", "Audit de conformité et cartographie initiale", 18),
                 ("Lot 2", "DPO mutualisé externalisé (36 mois)", 48),
                 ("Lot 3", "Formation et sensibilisation du personnel", 14),
                 ("Lot 4", "Outils, documentation et registre numérique", 20)],
        "criteria": [("Expertise RGPD et qualification du DPO proposé", 52), ("Prix global", 28),
                     ("Méthodologie et outils proposés", 12), ("Disponibilité et réactivité", 8)],
        "phases": [("Phase 1 – Audit et état des lieux", 2), ("Phase 2 – Mise en conformité prioritaire", 4),
                   ("Phase 3 – DPO en run et amélioration continue", 30)],
    },
    {
        "type": "TÉLÉPHONIE IP", "num": 9,
        "title": "Migration vers une solution de communications unifiées UCaaS (Microsoft Teams Phone)",
        "domain": "Communications unifiées et téléphonie d'entreprise",
        "context": (
            "Le système PABX Alcatel-Lucent installé en 2008 est en fin de vie absolue, "
            "plus maintenu par le constructeur depuis janvier 2024. Les pièces de remplacement "
            "sont introuvables et trois pannes majeures ont affecté la disponibilité "
            "du service téléphonique au cours des 12 derniers mois. La structure compte "
            "340 postes téléphoniques sur 5 sites et souhaite migrer vers une solution "
            "cloud UCaaS moderne, intégrée à son environnement Microsoft 365 déjà déployé."
        ),
        "reqs": [
            "Solution UCaaS cloud Microsoft Teams Phone avec Direct Routing SIP",
            "Trunk SIP redondant avec opérateur certifié Microsoft (2 opérateurs pour résilience)",
            "Portabilité de l'intégralité des numéros existants (340 DDI + numéros groupements)",
            "Postes IP physiques Teams-certifiés et softphones pour tous les utilisateurs",
            "Standard automatique, groupes d'appels, files d'attente avec IVR",
            "Enregistrement des appels chiffré pour les services réglementés",
            "Intégration annuaire LDAP et synchronisation Active Directory",
            "Statistiques et rapports d'utilisation mensuels",
        ],
        "constraints": [
            "Continuité du service téléphonique garantie pendant la migration (zéro coupure)",
            "Qualité audio MOS > 4,0 mesuré contractuellement",
            "Disponibilité de la plateforme UCaaS 99,99% (accord de niveau Microsoft inclus)",
            "Opérateur SIP certifié Microsoft Teams Direct Routing obligatoire",
        ],
        "lots": [("Lot 1", "Licences UCaaS, abonnement opérateur SIP et trunk", 48),
                 ("Lot 2", "Postes téléphoniques IP et casques audio certifiés Teams", 24),
                 ("Lot 3", "Déploiement, migration et portabilité", 16),
                 ("Lot 4", "Formation des utilisateurs et support (2 ans)", 12)],
        "criteria": [("Qualité technique de la solution UCaaS", 45), ("Prix total de possession (TCO 3 ans)", 32),
                     ("Qualité du plan de migration", 13), ("Service après-vente et SLA", 10)],
        "phases": [("Phase 1 – Configuration et tests", 2), ("Phase 2 – Pilote (40 utilisateurs)", 1),
                   ("Phase 3 – Déploiement progressif par site", 4)],
    },
    {
        "type": "BUSINESS INTELLIGENCE", "num": 10,
        "title": "Déploiement d'une plateforme de Business Intelligence et pilotage de la performance",
        "domain": "Décisionnel, reporting et pilotage stratégique",
        "context": (
            "La direction générale souffre d'un manque critique de visibilité sur les "
            "indicateurs de performance opérationnelle et financière. Les reportings actuels "
            "sont produits manuellement sous Excel, mobilisent 3 ETP chaque mois et comportent "
            "fréquemment des erreurs de consolidation. La structure génère des données "
            "dans 9 applications métier distinctes (ERP, CRM, GRH, GED, etc.) "
            "qu'il convient d'agréger dans un entrepôt de données unique pour une vision "
            "360° de l'activité et une prise de décision fondée sur des données fiables."
        ),
        "reqs": [
            "Entrepôt de données (Data Warehouse) cloud-native avec modélisation dimensionnelle",
            "Pipeline ETL/ELT automatisé pour l'alimentation depuis les 9 sources de données",
            "Outil de reporting et datavisualisation Power BI Premium avec 50 licences",
            "Tableaux de bord exécutifs (C-Level) et opérationnels (managers, agents)",
            "Gestion des habilitations et Row-Level Security par profil et périmètre",
            "Rafraîchissement des données en quasi temps réel (latence < 15 minutes)",
            "Catalogue de données avec dictionnaire métier et data lineage documenté",
            "Formation de 50 utilisateurs à l'autonomie sur Power BI",
        ],
        "constraints": [
            "Latence de rafraîchissement contractuellement garantie < 15 minutes",
            "Historique des données conservé sur 10 ans minimum avec archivage progressif",
            "Export en formats ouverts : CSV, XLSX, JSON, PDF (accessibilité RGAA)",
            "Audit trail complet des accès aux données (conformité RGPD)",
        ],
        "lots": [("Lot 1", "Data Warehouse cloud et infrastructure ETL", 38),
                 ("Lot 2", "Licences Power BI Premium et environnement", 22),
                 ("Lot 3", "Développement des rapports et tableaux de bord (50 livrables)", 28),
                 ("Lot 4", "Formation, documentation et transfert de compétences", 12)],
        "criteria": [("Couverture fonctionnelle et qualité des démonstrations", 45), ("Prix global", 30),
                     ("Performance technique et latence garantie", 15), ("Qualité de la formation", 10)],
        "phases": [("Phase 1 – Data warehouse et ETL", 3), ("Phase 2 – Développement tableaux de bord", 4),
                   ("Phase 3 – Déploiement, formation et run", 3)],
    },
    {
        "type": "GED / ARCHIVAGE", "num": 11,
        "title": "Acquisition d'une solution de GED, dématérialisation et archivage électronique probant",
        "domain": "Gestion documentaire et dématérialisation",
        "context": (
            "La structure produit et reçoit annuellement plus de 220 000 documents "
            "(courriers, contrats, factures, actes, rapports). L'organisation actuelle "
            "est défaillante : documents éparpillés sur 14 partages réseau non structurés, "
            "absence de versioning, doublons fréquents et délais de recherche excessifs "
            "(moyenne 18 minutes par document). La réglementation impose des durées d'archivage "
            "allant de 5 à 50 ans selon la nature des documents."
        ),
        "reqs": [
            "GED avec moteur de recherche full-text, métadonnées et plan de classement hiérarchique",
            "Workflow de validation configurable et circuit de signature électronique avancée",
            "Archivage à valeur probante avec horodatage qualifié (eIDAS niveau avancé)",
            "Capture documentaire avec LAD/RAD et connecteurs scanners/MFP",
            "Connecteurs vers 6 applications métier existantes (ERP, CRM, GRH, etc.)",
            "Gestion fine des habilitations (droits d'accès, modification, suppression)",
            "Purge automatique avec workflow de validation selon les durées légales",
            "Interface web responsive et application mobile (iOS/Android)",
        ],
        "constraints": [
            "Conformité NF Z 42-013 pour le système d'archivage électronique (SAE)",
            "Signature électronique qualifiée conforme eIDAS règlement EU 910/2014",
            "Hébergement sur territoire européen avec certification ISO 27001",
            "Interopérabilité avec les formats d'échange SEDA v2.1 et EAD3",
        ],
        "lots": [("Lot 1", "Licence GED, SAE et infrastructure", 33),
                 ("Lot 2", "Paramétrage, workflows et développements", 27),
                 ("Lot 3", "Numérisation du fonds documentaire existant (1,2M pages)", 25),
                 ("Lot 4", "Formation et conduite du changement (180 agents)", 15)],
        "criteria": [("Conformité fonctionnelle et réglementaire", 48), ("Prix global", 28),
                     ("Ergonomie et expérience utilisateur", 14), ("Pérennité et références", 10)],
        "phases": [("Phase 1 – Paramétrage et recette", 4), ("Phase 2 – Numérisation et migration", 6),
                   ("Phase 3 – Déploiement et formation", 3)],
    },
    {
        "type": "SIRH / RH", "num": 12,
        "title": "Déploiement d'un SIRH complet avec portail collaborateur et gestion des talents",
        "domain": "Ressources humaines et système d'information RH",
        "context": (
            "La gestion des ressources humaines repose sur un logiciel Cegid paie vieillissant "
            "ne couvrant que la paie et les congés. Les processus de recrutement, d'évaluation "
            "annuelle, de gestion de la formation et des compétences sont gérés dans "
            "des tableurs Excel par 8 gestionnaires RH. La structure compte 520 agents "
            "sur 4 sites et les délais de traitement des demandes RH dépassent 10 jours "
            "en moyenne, générant une insatisfaction croissante des managers."
        ),
        "reqs": [
            "Modules : paie, administration du personnel, congés/absences, recrutement, formation, évaluation",
            "Portail collaborateur self-service : fiches de paie, demandes, soldes de congés",
            "Gestion des compétences, des parcours et des plans de développement individuels",
            "Conformité DSN mensuelle, DADS-U, DPAE et déclarations sociales obligatoires",
            "Coffre-fort numérique individuel pour les bulletins de paie (durée légale 50 ans)",
            "Tableaux de bord RH : masse salariale, absentéisme, turnover, pyramide des âges",
            "Application mobile managers pour validation des demandes et accès aux KPI",
            "Intégration Active Directory et synchronisation avec l'ERP financier",
        ],
        "constraints": [
            "Données RH hébergées exclusivement en France (données sensibles CNIL catégorie 9)",
            "Conformité DSN phase 3 et évolutions légales garanties pour la durée du contrat",
            "Disponibilité 99,5% en heures ouvrées avec MCO inclus dans le contrat",
            "Accessibilité RGAA niveau AA pour le portail collaborateur",
        ],
        "lots": [("Lot 1", "SIRH Core (paie et administration RH)", 38),
                 ("Lot 2", "Portail collaborateur et self-service manager", 27),
                 ("Lot 3", "Talent management (recrutement, formation, évaluation)", 22),
                 ("Lot 4", "Intégrations, reprise de données et formation", 13)],
        "criteria": [("Couverture fonctionnelle et conformité légale", 50), ("Prix global (TCO 5 ans)", 28),
                     ("Ergonomie du portail collaborateur", 12), ("Qualité du support et évolutivité", 10)],
        "phases": [("Phase 1 – Paramétrage paie et RH core", 4), ("Phase 2 – Portail et self-service", 3),
                   ("Phase 3 – Talent management et intégrations", 3)],
    },
    {
        "type": "DATACENTER", "num": 13,
        "title": "Construction d'une salle informatique sécurisée Tier III et exploitation MCO",
        "domain": "Infrastructure datacenter et hébergement physique",
        "context": (
            "La salle informatique actuelle (28 m²) ne répond plus aux exigences de disponibilité "
            "et de sécurité. Elle ne dispose ni de groupe électrogène, ni d'onduleurs redondants, "
            "ni d'un système de climatisation de précision avec redondance. "
            "Trois pannes électriques majeures en 2024 ont causé des arrêts de service "
            "totalisant 14 heures d'indisponibilité. La décision a été prise de construire "
            "une nouvelle salle de 60 m² en Tier III selon la norme TIA-942."
        ),
        "reqs": [
            "Salle informatique 60 m² Tier III (TIA-942) : disponibilité garantie 99,982%",
            "Alimentation électrique redondante architecture 2N avec groupe électrogène 200 kVA",
            "Climatisation précision N+1 avec free-cooling économique",
            "Système de détection et extinction incendie à gaz (Novec 1230)",
            "Contrôle d'accès biométrique multipoint et vidéosurveillance 24/7",
            "Câblage structuré catégorie 6A et fibre optique OM4 avec traçabilité",
            "DCIM (Data Center Infrastructure Management) avec alerting temps réel",
            "Baies 42U avec PDU intelligentes et monitoring par circuit",
        ],
        "constraints": [
            "PUE (Power Usage Effectiveness) contractualisé < 1,4",
            "Certification Tier III de l'Uptime Institute à la livraison",
            "Livraison de la salle opérationnelle avant le 1er juillet 2027",
            "Garantie décennale sur le génie civil et garantie constructeur 10 ans sur les équipements",
        ],
        "lots": [("Lot 1", "Génie civil, second œuvre et aménagement", 22),
                 ("Lot 2", "Alimentation électrique, UPS et groupe électrogène", 32),
                 ("Lot 3", "Climatisation de précision et gestion thermique", 22),
                 ("Lot 4", "Câblage structuré, sécurité physique et DCIM", 24)],
        "criteria": [("Conformité Tier III et performance technique", 52), ("Prix global", 26),
                     ("Planning de réalisation et gestion des risques", 12), ("Références datacenter similaires", 10)],
        "phases": [("Phase 1 – Études et permis", 3), ("Phase 2 – Génie civil et second œuvre", 6),
                   ("Phase 3 – Équipements techniques et recette", 4)],
    },
    {
        "type": "VIDÉOPROTECTION", "num": 14,
        "title": "Déploiement d'un système de vidéoprotection IP intelligent sur 12 sites",
        "domain": "Sécurité physique et vidéosurveillance",
        "context": (
            "La structure souhaite moderniser son dispositif de sécurité physique "
            "en déployant un système de vidéoprotection IP de nouvelle génération "
            "sur l'ensemble de ses 12 sites. Le système analogique actuel (caméras SD "
            "de 2011) ne fournit pas une qualité d'image suffisante pour l'identification, "
            "n'offre pas de capacité d'analyse intelligente et son archivage de 7 jours "
            "est insuffisant au regard des obligations légales. Le projet concerne "
            "environ 200 caméras et une salle de supervision centralisée (CSU)."
        ),
        "reqs": [
            "Caméras IP 4K H.265 avec analyse vidéo intelligente (intrusion, franchissement de ligne)",
            "VMS (Video Management System) centralisé multi-sites avec accès sécurisé distant",
            "Archivage sécurisé 30 jours en résolution maximale (stockage redondant NAS)",
            "Caméras thermiques PTZ pour les périmètres extérieurs sensibles",
            "Intégration avec le contrôle d'accès existant (déclenchement automatique)",
            "Détection comportementale par IA (attroupement, baggage abandonné)",
            "Interface opérateur ergonomique sur grand écran (mur d'images 6 écrans)",
            "Conformité CNIL et procédure d'autorisation préfectorale incluse",
        ],
        "constraints": [
            "Autorisation préfectorale de système de vidéoprotection requise (accompagnement inclus)",
            "Conformité RGPD pour les durées de conservation et les droits d'accès",
            "Résolution minimale 4K pour les zones d'entrée/sortie et espaces critiques",
            "Délai d'export d'une séquence vidéo < 2 minutes pour réquisition judiciaire",
        ],
        "lots": [("Lot 1", "Caméras IP 4K et infrastructure réseau vidéo", 42),
                 ("Lot 2", "VMS, stockage NAS et salle de supervision", 28),
                 ("Lot 3", "Travaux d'installation, câblage et mise en service", 18),
                 ("Lot 4", "Maintenance préventive et curative (5 ans)", 12)],
        "criteria": [("Qualité technique des équipements et de l'analyse IA", 48), ("Prix global", 28),
                     ("Qualité du plan de maintenance", 14), ("Références installations similaires", 10)],
        "phases": [("Phase 1 – Études techniques et autorisation préfectorale", 3),
                   ("Phase 2 – Installation et raccordement", 5), ("Phase 3 – Paramétrage VMS et recette", 2)],
    },
    {
        "type": "APPLICATION MOBILE", "num": 15,
        "title": "Développement d'une application mobile citoyenne multiservices",
        "domain": "Développement applicatif et services numériques",
        "context": (
            "Dans le cadre de sa politique de dématérialisation 100% des services publics, "
            "la collectivité souhaite développer une application mobile citoyenne permettant "
            "d'accéder à l'ensemble des services numériques depuis un point d'entrée unique. "
            "L'enquête citoyenne 2025 révèle que 78% des usagers souhaitent interagir "
            "avec leur collectivité via une application mobile. Les 26 démarches en ligne "
            "actuelles sont dispersées sur des plateformes distinctes non intégrées."
        ),
        "reqs": [
            "Application cross-platform Flutter ou React Native (iOS 15+ et Android 11+)",
            "Authentification France Connect niveau substantiel et biométrie locale",
            "Module signalement géolocalisé (voirie, mobilier urbain) avec suivi en temps réel",
            "Paiement en ligne sécurisé (PayFip et carte bancaire 3DS2)",
            "Notifications push personnalisables par thématique et géolocalisation",
            "Mode hors-ligne pour la consultation des documents personnels",
            "Accessibilité WCAG 2.1 niveau AA et RGAA 4.1",
            "API REST backend documentée OpenAPI 3.0 avec sandbox développeur",
        ],
        "constraints": [
            "Code source intégralement remis à la collectivité (transfert pleine propriété IP)",
            "Hébergement sur infrastructure cloud souveraine certifiée SecNumCloud",
            "Conformité DSFR (Design System de l'État) pour l'interface",
            "Taux de crash en production < 0,1% et temps de démarrage < 3 secondes",
        ],
        "lots": [("Lot 1", "Architecture backend, API et authentification", 28),
                 ("Lot 2", "Application mobile iOS et Android", 42),
                 ("Lot 3", "Intégrations métier, paiement et notifications", 18),
                 ("Lot 4", "Tests, déploiement store et MCO (2 ans)", 12)],
        "criteria": [("Qualité technique et ergonomie de l'application", 48), ("Prix global", 28),
                     ("Conformité RGAA et accessibilité", 14), ("Délais de livraison", 10)],
        "phases": [("Phase 1 – Design UX/UI et backend", 3), ("Phase 2 – Développement mobile", 5),
                   ("Phase 3 – Tests, déploiement et lancement", 2)],
    },
    {
        "type": "SITE WEB / PORTAIL", "num": 16,
        "title": "Refonte du site web institutionnel et déploiement d'un portail de services en ligne",
        "domain": "Web, accessibilité et services numériques",
        "context": (
            "Le site web institutionnel actuel, développé en 2014 sous WordPress 4, "
            "présente de nombreuses lacunes bloquantes : non-conformité RGAA (score 28/100), "
            "absence de version mobile responsive, temps de chargement moyen de 8,4 secondes "
            "et interface vieillissante incompatible avec les standards 2025. "
            "L'audit d'accessibilité commandé en 2025 a révélé 847 non-conformités. "
            "Par ailleurs, les 28 démarches en ligne utilisent des outils disparates "
            "générant confusion et abandons (taux d'abandon : 67%)."
        ),
        "reqs": [
            "CMS headless moderne (Strapi ou Directus) avec architecture découplée (JAMstack)",
            "Design System de l'État (DSFR) obligatoire sur toutes les pages",
            "Conformité RGAA 4.1 niveau AA certifiée par auditeur tiers accrédité",
            "Performance Core Web Vitals : LCP < 2,5s, INP < 200ms, CLS < 0,1",
            "28 formulaires de démarches en ligne avec suivi de dossier en temps réel",
            "Authentification France Connect pour les démarches nécessitant identification",
            "Multilinguisme FR/EN avec traduction automatique (breton optionnel)",
            "Matomo Analytics self-hosted (conformité CNIL sans consentement)",
        ],
        "constraints": [
            "Conformité RGAA niveau AA certifiée avant mise en production (auditeur tiers)",
            "Hébergement sur infrastructure souveraine (pas de GAFAM)",
            "Core Web Vitals > 90 sur Google PageSpeed Insights (mobile et desktop)",
            "Déclaration d'accessibilité obligatoire publiée sur le site",
        ],
        "lots": [("Lot 1", "Architecture CMS headless et infrastructure d'hébergement", 28),
                 ("Lot 2", "Design graphique, intégration DSFR et accessibilité", 22),
                 ("Lot 3", "Développement des 28 démarches en ligne et API", 36),
                 ("Lot 4", "SEO technique, performance et audit d'accessibilité", 14)],
        "criteria": [("Conformité RGAA et accessibilité démontrée", 40), ("Prix global", 28),
                     ("Performance technique et Core Web Vitals", 18), ("Ergonomie et design", 14)],
        "phases": [("Phase 1 – Conception UX et architecture", 2), ("Phase 2 – Développement CMS et DSFR", 4),
                   ("Phase 3 – Démarches en ligne et intégrations", 4), ("Phase 4 – Audit et mise en production", 2)],
    },
    {
        "type": "PRA / PCA", "num": 17,
        "title": "Mise en place d'un Plan de Reprise d'Activité (PRA) et de Continuité d'Activité (PCA)",
        "domain": "Continuité d'activité et résilience des systèmes d'information",
        "context": (
            "L'analyse de risques conduite par le RSSI en 2025 a identifié trois scénarios "
            "de sinistres majeurs pour lesquels la structure n'est pas résiliente : "
            "incendie du datacenter principal, attaque ransomware et panne prolongée "
            "de la connectivité WAN. L'impact financier estimé d'une indisponibilité "
            "de 48h des systèmes critiques est de 480 000 euros de pertes directes "
            "et d'image. La structure ne dispose pas de site de secours ni de PRA formalisé."
        ),
        "reqs": [
            "Business Impact Analysis (BIA) couvrant les 18 processus métier critiques",
            "Définition contractuelle des RTO et RPO par application (10 apps critiques)",
            "Site de secours géographiquement distant (> 150 km) avec infrastructure miroir",
            "Réplication synchrone des données critiques (latence < 100ms garantie)",
            "Infrastructure de basculement automatique (failover) avec détection de panne",
            "Tests de bascule réels semestriels avec rapport d'exécution",
            "Plan de Continuité d'Activité (PCA) métier avec procédures dégradées",
            "Exercices de gestion de crise et formation des équipes de direction",
        ],
        "constraints": [
            "Site PRA certifié Tier III minimum avec distance > 150 km du site principal",
            "RTO contractuel < 4h et RPO < 1h pour les 10 applications critiques",
            "Tests de bascule réels (pas de simulation sur maquette) obligatoires",
            "Documents PCA/PRA classifiés diffusion restreinte (confidentialité renforcée)",
        ],
        "lots": [("Lot 1", "Audit de risques et Business Impact Analysis", 8),
                 ("Lot 2", "Infrastructure PRA, réplication et failover", 58),
                 ("Lot 3", "Tests de bascule et validation opérationnelle", 14),
                 ("Lot 4", "Rédaction PCA/PRA, formation et exercices de crise", 20)],
        "criteria": [("Qualité technique du PRA et des garanties RTO/RPO", 50), ("Prix global", 28),
                     ("Qualité de la méthodologie PCA", 12), ("Certifications du site de secours", 10)],
        "phases": [("Phase 1 – BIA et conception architecture PRA", 2),
                   ("Phase 2 – Déploiement infrastructure PRA", 5), ("Phase 3 – Tests et documentation", 2)],
    },
    {
        "type": "FORMATION NUMÉRIQUE", "num": 18,
        "title": "Formation et accompagnement à la transformation numérique (1200 agents)",
        "domain": "Formation professionnelle et conduite du changement",
        "context": (
            "La structure a engagé un vaste programme de modernisation numérique 2024-2027 "
            "impliquant le déploiement de Microsoft 365, d'un nouvel ERP, d'un SIRH "
            "et d'outils collaboratifs. L'enquête interne conduite en 2025 révèle que "
            "72% des agents se déclarent peu ou pas à l'aise avec les nouveaux outils numériques. "
            "Un plan de formation pluriannuel est indispensable pour réduire la fracture "
            "numérique interne et garantir le succès du programme de transformation."
        ),
        "reqs": [
            "Diagnostic des compétences numériques par assessment individuel en ligne (1200 agents)",
            "Parcours de formation personnalisés par profil : dirigeant, manager, technicien, administratif",
            "Formation présentielle en petits groupes (12 personnes max) et distanciel synchrone",
            "Plateforme LMS cloud avec e-learning, SCORM 2004 et suivi des progressions",
            "Modules certifiants Microsoft 365 (Teams, SharePoint, OneDrive, Power Automate, Power BI)",
            "Formation des formateurs internes (ToT) : 24 agents certifiés formateur Microsoft",
            "Évaluation des acquis : QCM, mises en situation et certification ECDL ou PIX Pro",
            "Rapport trimestriel de suivi : taux de complétion, scores, ROI formation estimé",
        ],
        "constraints": [
            "Organisme certifié Qualiopi (audit de renouvellement à jour) obligatoire",
            "Formateurs certifiés Microsoft Certified Trainer (MCT) pour les modules M365",
            "Accessibilité des formations aux personnes en situation de handicap (référent RQTH)",
            "Éligibilité CPF pour les certifications proposées (financement OPCO possible)",
        ],
        "lots": [("Lot 1", "Diagnostic, ingénierie pédagogique et LMS", 12),
                 ("Lot 2", "Formations présentielles et distancielles (1200 agents)", 42),
                 ("Lot 3", "Certifications Microsoft et ECDL/PIX Pro", 28),
                 ("Lot 4", "Formation des formateurs (ToT) et suivi (2 ans)", 18)],
        "criteria": [("Qualité pédagogique et personnalisation des parcours", 45), ("Prix par stagiaire", 30),
                     ("Certifications et qualifications Qualiopi/MCT", 15), ("Outils LMS et reporting", 10)],
        "phases": [("Phase 1 – Diagnostic et conception des parcours", 2),
                   ("Phase 2 – Déploiement vague 1 (400 agents)", 4), ("Phase 3 – Vagues 2 et 3 (800 agents)", 8)],
    },
    {
        "type": "IOT / SMART BUILDING", "num": 19,
        "title": "Déploiement d'une infrastructure IoT pour la gestion intelligente des bâtiments (GTB)",
        "domain": "IoT, efficacité énergétique et smart building",
        "context": (
            "Dans le cadre de sa stratégie RSE et des obligations du décret tertiaire "
            "(réduction de 40% des consommations énergétiques d'ici 2030), la structure "
            "souhaite instrumenter ses 6 bâtiments principaux (42 000 m² au total) "
            "avec des capteurs IoT connectés. Les factures énergétiques représentent "
            "1,8M€ annuels avec une augmentation de 23% en 2024. L'objectif est de réduire "
            "les consommations de 25% en 36 mois grâce au pilotage automatique."
        ),
        "reqs": [
            "Capteurs température, humidité, CO2, luminosité et présence dans 850 espaces",
            "Compteurs intelligents électricité, eau, gaz et froid avec télérelève",
            "Réseau IoT bas débit longue portée LoRaWAN privé (gateway par bâtiment)",
            "Plateforme IoT cloud avec digital twin 3D des 6 bâtiments",
            "Alertes automatiques et actions correctives sur les GTB existants (Siemens Desigo)",
            "API ouverte MQTT/REST pour intégration avec les systèmes de GTC",
            "Tableau de bord énergie temps réel et rapports de conformité décret tertiaire",
            "Cybersécurité IoT : segmentation réseau, firmware signé, mises à jour OTA",
        ],
        "constraints": [
            "Durée de vie des capteurs > 7 ans avec batterie remplaçable ou energy harvesting",
            "Protocoles ouverts et interopérables obligatoires (MQTT, CoAP, OpenADR 2.0)",
            "Données d'exploitation hébergées sur infrastructure souveraine",
            "Réduction énergétique mesurée et certifiée par organisme tiers accrédité COFRAC",
        ],
        "lots": [("Lot 1", "Capteurs IoT, gateways LoRaWAN et réseau", 33),
                 ("Lot 2", "Plateforme IoT cloud et digital twin", 30),
                 ("Lot 3", "Intégration GTB/GTC et automatismes", 22),
                 ("Lot 4", "Maintenance, télégestion et MCO (5 ans)", 15)],
        "criteria": [("Performance technique et interopérabilité", 45), ("Prix global et TCO 5 ans", 28),
                     ("Réduction énergétique garantie contractuellement", 17), ("Pérennité de la solution", 10)],
        "phases": [("Phase 1 – Audit énergétique et architecture IoT", 2),
                   ("Phase 2 – Déploiement bâtiments pilotes (2 sites)", 4),
                   ("Phase 3 – Généralisation (4 sites restants)", 6)],
    },
    {
        "type": "API MANAGEMENT / INTÉGRATION SI", "num": 20,
        "title": "Mise en place d'une plateforme d'API Management et urbanisation du SI (18 applications)",
        "domain": "Architecture SI, intégration et API Management",
        "context": (
            "La structure exploite 18 applications métier hétérogènes qui communiquent "
            "principalement via des exports/imports de fichiers plats et des interfaces "
            "point-à-point difficiles à maintenir. Cette architecture en spaghetti génère "
            "des incohérences de données (3 référentiels clients distincts), des délais "
            "de synchronisation de 24 à 48 heures et des coûts de maintenance estimés "
            "à 280 000€ annuels. La mise en place d'une plateforme d'API Management "
            "est la condition préalable à toute évolution du SI."
        ),
        "reqs": [
            "Plateforme API Management (Azure APIM, Kong ou MuleSoft) en mode cloud managé",
            "Conception et développement des API RESTful (standard OAS 3.0) pour les 18 apps",
            "Portail développeur self-service avec documentation interactive Swagger UI",
            "Gestion des accès OAuth 2.0, rate limiting et quotas par consommateur",
            "Monitoring temps réel et observabilité (logs, métriques, traces distribuées)",
            "Event streaming pour les échanges temps réel (Azure Event Hub ou Kafka)",
            "Patterns d'intégration : orchestration, chorégraphie, saga et outbox",
            "Tests automatisés (contrats API, charge, sécurité OWASP) en CI/CD",
        ],
        "constraints": [
            "API conformes aux recommandations de la DINUM et référencées sur api.gouv.fr",
            "Versioning sémantique SemVer obligatoire avec gestion de la rétrocompatibilité",
            "Disponibilité de la plateforme API Management 99,9% (SLA mensuel garanti)",
            "Audit de sécurité OWASP API Security Top 10 réalisé avant mise en production",
        ],
        "lots": [("Lot 1", "Plateforme API Management et infrastructure", 33),
                 ("Lot 2", "Développement des 18 connecteurs et API métier", 42),
                 ("Lot 3", "Monitoring, observabilité et sécurité", 12),
                 ("Lot 4", "Portail développeur, documentation et formation", 13)],
        "criteria": [("Qualité de l'architecture et de la plateforme API", 48), ("Prix global", 28),
                     ("Sécurité et conformité OWASP", 14), ("Qualité du portail développeur", 10)],
        "phases": [("Phase 1 – Plateforme et architecture cible", 3),
                   ("Phase 2 – API prioritaires (6 apps critiques)", 4),
                   ("Phase 3 – Généralisation (12 apps restantes)", 5)],
    },
]

BUYERS = [
    {"name": "Mairie de Rennes", "type": "Commune", "city": "Rennes (35)", "contact": "Direction des Systèmes d'Information"},
    {"name": "CHU de Bordeaux", "type": "Établissement public de santé", "city": "Bordeaux (33)", "contact": "Direction du Numérique en Santé"},
    {"name": "Conseil Régional de Normandie", "type": "Collectivité régionale", "city": "Rouen (76)", "contact": "Direction Générale des Services Numériques"},
    {"name": "Ministère de l'Éducation Nationale", "type": "Ministère", "city": "Paris (75)", "contact": "Direction du Numérique pour l'Éducation"},
    {"name": "Communauté Urbaine de Strasbourg", "type": "EPCI", "city": "Strasbourg (67)", "contact": "Service Informatique et Télécommunications"},
    {"name": "Agence Régionale de Santé Occitanie", "type": "Établissement public d'État", "city": "Toulouse (31)", "contact": "Département Systèmes d'Information"},
    {"name": "Université Paris-Saclay", "type": "Établissement d'enseignement supérieur", "city": "Gif-sur-Yvette (91)", "contact": "Direction des Systèmes d'Information"},
    {"name": "OPAC du Rhône", "type": "Office public de l'habitat", "city": "Lyon (69)", "contact": "Direction Informatique"},
    {"name": "Nantes Métropole", "type": "Métropole", "city": "Nantes (44)", "contact": "Pôle Numérique et Innovation"},
    {"name": "EHPAD Les Hauts de Seine", "type": "Établissement médico-social", "city": "Boulogne-Billancourt (92)", "contact": "Direction Administrative"},
    {"name": "Département du Finistère", "type": "Collectivité départementale", "city": "Quimper (29)", "contact": "Direction des Systèmes d'Information"},
    {"name": "CCI Marseille Provence", "type": "Chambre de Commerce et d'Industrie", "city": "Marseille (13)", "contact": "Direction Numérique"},
    {"name": "SEML Énergie Isère", "type": "Société d'Économie Mixte Locale", "city": "Grenoble (38)", "contact": "Direction des Opérations"},
    {"name": "GHT Seine-Oise", "type": "Groupement Hospitalier de Territoire", "city": "Versailles (78)", "contact": "DSI Territoriale"},
    {"name": "Collectivité Territoriale de Corse", "type": "Collectivité territoriale unique", "city": "Ajaccio (2A)", "contact": "Direction du Numérique"},
    {"name": "Préfecture Auvergne-Rhône-Alpes", "type": "Service de l'État", "city": "Lyon (69)", "contact": "SGAR – Numérique"},
    {"name": "Caisse d'Allocations Familiales 31", "type": "Organisme de protection sociale", "city": "Toulouse (31)", "contact": "Direction Informatique"},
    {"name": "Établissement Public Territorial Grand Paris Sud", "type": "EPT", "city": "Évry (91)", "contact": "Direction des Technologies de l'Information"},
    {"name": "Agence de l'Eau Loire-Bretagne", "type": "Établissement public national", "city": "Orléans (45)", "contact": "Système d'Information et Transition Numérique"},
    {"name": "Autorité de Sûreté Nucléaire", "type": "Autorité administrative indépendante", "city": "Paris (75)", "contact": "Direction des Systèmes d'Information"},
]

BUDGETS = [92000, 148000, 195000, 267000, 345000, 480000, 620000,
           790000, 1050000, 1380000, 1750000, 2200000, 2950000, 3800000]

DURATIONS = [("6 mois", 6), ("9 mois", 9), ("12 mois", 12),
             ("18 mois", 18), ("24 mois", 24), ("36 mois", 36)]


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

def build_styles():
    base = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle("cover_title", parent=base["Heading1"],
            fontSize=20, textColor=white, alignment=TA_CENTER, spaceAfter=10, leading=26),
        "cover_sub": ParagraphStyle("cover_sub", parent=base["Normal"],
            fontSize=12, textColor=white, alignment=TA_CENTER, spaceAfter=6),
        "cover_ref": ParagraphStyle("cover_ref", parent=base["Normal"],
            fontSize=10, textColor=HexColor("#c8d8e8"), alignment=TA_CENTER, spaceAfter=4),
        "h1": ParagraphStyle("h1", parent=base["Heading1"],
            fontSize=14, textColor=BLUE_DARK, spaceBefore=18, spaceAfter=8, borderPad=4),
        "h2": ParagraphStyle("h2", parent=base["Heading2"],
            fontSize=12, textColor=BLUE_MED, spaceBefore=12, spaceAfter=6),
        "body": ParagraphStyle("body", parent=base["Normal"],
            fontSize=10, alignment=TA_JUSTIFY, spaceAfter=6, leading=14),
        "bullet": ParagraphStyle("bullet", parent=base["Normal"],
            fontSize=10, spaceAfter=4, leftIndent=14, leading=13),
        "label": ParagraphStyle("label", parent=base["Normal"],
            fontSize=9, textColor=HexColor("#555555"), spaceAfter=2),
    }


def fmt_euro(n):
    s = f"{n:,.0f}".replace(",", " ")  # narrow no-break space
    return f"{s} EUR HT"


# ---------------------------------------------------------------------------
# PDF builder
# ---------------------------------------------------------------------------

def build_pdf(project, buyer, budget, duration_label, duration_months, idx):
    filename = OUTPUT_DIR / f"ao_{idx:03d}.pdf"
    rng = random.Random(idx * 17 + 3)

    doc = SimpleDocTemplate(str(filename), pagesize=A4,
        leftMargin=2.5*cm, rightMargin=2.5*cm,
        topMargin=2.5*cm, bottomMargin=2.5*cm)

    S = build_styles()
    story = []
    year = 2026

    ref = f"AO-{year}-{project['type'][:6].upper().replace(' ','')}-{idx:03d}"

    # --- PAGE DE GARDE ---
    cover_data = [
        [Paragraph(buyer["name"].upper(), S["cover_title"])],
        [Paragraph(buyer["type"], S["cover_sub"])],
        [Spacer(1, 0.4*cm)],
        [Paragraph("AVIS D'APPEL PUBLIC À LA CONCURRENCE", S["cover_sub"])],
        [Paragraph(f"Référence : {ref}", S["cover_ref"])],
        [Spacer(1, 0.6*cm)],
        [Paragraph(project["title"], ParagraphStyle("ct2", parent=S["cover_title"], fontSize=15, leading=20))],
        [Spacer(1, 0.4*cm)],
        [Paragraph(f"Domaine : {project['domain']}", S["cover_ref"])],
        [Spacer(1, 0.8*cm)],
        [Paragraph(f"Budget estimatif : {fmt_euro(budget)}", S["cover_sub"])],
        [Paragraph(f"Durée : {duration_label}", S["cover_sub"])],
        [Paragraph(f"Date de publication : 15 janvier {year}", S["cover_ref"])],
        [Paragraph(f"Date limite de remise des offres : 15 mars {year} à 17h00", S["cover_ref"])],
        [Spacer(1, 0.6*cm)],
        [Paragraph(f"Contact : {buyer['contact']}", S["cover_ref"])],
        [Paragraph(buyer["city"], S["cover_ref"])],
    ]
    tbl = Table([[r[0]] for r in cover_data], colWidths=[15*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BLUE_DARK),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 20),
        ("RIGHTPADDING", (0, 0), (-1, -1), 20),
        ("ROWBACKGROUNDS", (0, 6), (-1, 6), [BLUE_MED]),
    ]))
    story.append(tbl)
    story.append(PageBreak())

    # --- ARTICLE 1 – OBJET ---
    story.append(Paragraph(f"Article 1 – Objet du marché", S["h1"]))
    story.append(Paragraph(
        f"Le présent appel d'offres, lancé par <b>{buyer['name']}</b> ({buyer['type']}, "
        f"{buyer['city']}), a pour objet la mise en œuvre du projet suivant :", S["body"]))
    story.append(Paragraph(f"<b>{project['title']}</b>", S["body"]))
    story.append(Paragraph(
        f"Ce marché est passé selon la procédure d'appel d'offres ouvert conformément aux "
        f"articles L2124-2 et R2124-2 du Code de la commande publique. "
        f"Le montant estimatif du marché est de <b>{fmt_euro(budget)}</b> pour une durée de "
        f"<b>{duration_label}</b>. Le marché prend effet à compter de sa date de notification "
        f"et couvre l'ensemble des prestations décrites dans le présent Cahier des Clauses "
        f"Techniques Particulières (CCTP).", S["body"]))
    story.append(Paragraph(
        f"Le code CPV principal de ce marché est 72000000-5 (Services de technologies de "
        f"l'information, conseil, développement de logiciels, internet et appui). "
        f"Les codes CPV complémentaires sont précisés à l'Annexe A du présent document.", S["body"]))
    story.append(Spacer(1, 0.3*cm))

    # --- ARTICLE 2 – CONTEXTE ---
    story.append(Paragraph("Article 2 – Contexte et enjeux", S["h1"]))
    story.append(Paragraph("2.1 Présentation de l'organisme acheteur", S["h2"]))
    story.append(Paragraph(
        f"<b>{buyer['name']}</b> est un organisme de type {buyer['type']} situé à {buyer['city']}. "
        f"La structure est dotée d'un service informatique rattaché à la {buyer['contact']}. "
        f"Elle emploie entre 300 et 1200 agents selon les sites et gère un budget de "
        f"fonctionnement annuel adapté à ses missions de service public.", S["body"]))
    story.append(Paragraph("2.2 Contexte et problématique", S["h2"]))
    story.append(Paragraph(project["context"], S["body"]))
    story.append(Paragraph("2.3 Objectifs stratégiques du projet", S["h2"]))
    objectives = [
        "Moderniser le système d'information et réduire la dette technique accumulée",
        "Améliorer la qualité de service rendu aux usagers et aux agents",
        "Optimiser les coûts opérationnels et la productivité des équipes",
        "Garantir la conformité réglementaire et la sécurité des données",
        "Renforcer la résilience et la continuité d'activité du système d'information",
    ]
    for obj in objectives:
        story.append(Paragraph(f"• {obj}", S["bullet"]))
    story.append(Spacer(1, 0.3*cm))

    # --- ARTICLE 3 – CAHIER DES CHARGES ---
    story.append(Paragraph("Article 3 – Périmètre et exigences générales", S["h1"]))
    story.append(Paragraph("3.1 Périmètre des prestations", S["h2"]))
    story.append(Paragraph(
        "Le titulaire du marché devra assurer l'ensemble des prestations décrites ci-après. "
        "Les exigences listées constituent des obligations contractuelles dont le respect "
        "sera vérifié lors des phases de recette fonctionnelle et technique. "
        "Toute dérogation devra être explicitement mentionnée et justifiée dans l'offre.", S["body"]))
    story.append(Paragraph("3.2 Exigences fonctionnelles et techniques", S["h2"]))
    for req in project["reqs"]:
        story.append(Paragraph(f"• {req}", S["bullet"]))
    story.append(Paragraph("3.3 Contraintes et prérequis", S["h2"]))
    for c in project["constraints"]:
        story.append(Paragraph(f"• {c}", S["bullet"]))
    story.append(Paragraph("3.4 Livrables attendus", S["h2"]))
    livrables = [
        "Note de cadrage et plan projet détaillé avec jalons contractuels",
        "Architecture technique détaillée et dossier de conception (DAT/DOE)",
        "Environnements de développement, recette et production opérationnels",
        "Jeux de tests fonctionnels et résultats de recette documentés",
        "Documentation technique administrateur et guide utilisateur final",
        "Rapport de bilan et retour d'expérience (RETEX) post-déploiement",
    ]
    for l in livrables:
        story.append(Paragraph(f"• {l}", S["bullet"]))
    story.append(Spacer(1, 0.3*cm))

    # --- ARTICLE 4 – LOTS ---
    story.append(Paragraph("Article 4 – Décomposition en lots", S["h1"]))
    story.append(Paragraph(
        "Le marché est décomposé en plusieurs lots distincts. Les candidats peuvent "
        "répondre à un ou plusieurs lots. Chaque lot fera l'objet d'un marché distinct. "
        "La pondération indicative des lots par rapport au montant total est la suivante :", S["body"]))
    lot_rows = [["N° de lot", "Intitulé du lot", "Pondération (%)", "Montant estimatif"]]
    for lot_name, lot_desc, pct in project["lots"]:
        lot_budget = int(budget * pct / 100)
        lot_rows.append([lot_name, lot_desc, f"{pct}%", fmt_euro(lot_budget)])
    lot_rows.append(["", "TOTAL", "100%", fmt_euro(budget)])

    lot_tbl = Table(lot_rows, colWidths=[2*cm, 7*cm, 2.5*cm, 3.5*cm])
    lot_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [white, GRAY_LIGHT]),
        ("BACKGROUND", (0, -1), (-1, -1), BLUE_MED),
        ("TEXTCOLOR", (0, -1), (-1, -1), white),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, GRAY_MED),
        ("ALIGN", (2, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(lot_tbl)
    story.append(Spacer(1, 0.3*cm))

    # --- ARTICLE 5 – CCTP ---
    story.append(Paragraph("Article 5 – Cahier des Clauses Techniques Particulières (CCTP)", S["h1"]))
    story.append(Paragraph("5.1 Architecture et infrastructure", S["h2"]))
    story.append(Paragraph(
        "Le titulaire proposera une architecture robuste, scalable et évolutive, "
        "compatible avec les standards de l'état de l'art au moment de la remise de l'offre. "
        "L'architecture devra être documentée selon le standard ArchiMate ou UML "
        "et présentée lors d'un atelier technique de cadrage dans les 15 premiers jours du marché. "
        "Elle devra notamment couvrir les aspects de haute disponibilité, de reprise sur panne "
        "et de sécurité des données.", S["body"]))
    story.append(Paragraph("5.2 Sécurité et conformité", S["h2"]))
    story.append(Paragraph(
        "L'ensemble des composants devront respecter les recommandations de l'ANSSI "
        "(Guide d'hygiène informatique, référentiels PGSSI-S le cas échéant) "
        "et les bonnes pratiques OWASP. Un plan d'assurance sécurité (PAS) sera remis "
        "au maître d'ouvrage dans les 30 jours suivant la notification du marché. "
        "Les données à caractère personnel seront traitées conformément au RGPD "
        "et une analyse d'impact (AIPD) sera réalisée si nécessaire.", S["body"]))
    story.append(Paragraph("5.3 Conditions de recette", S["h2"]))
    story.append(Paragraph(
        "La recette des prestations se déroulera en deux phases successives : "
        "la Recette Usine (RU) conduite dans les locaux du titulaire, "
        "suivie de la Recette Site (RS) dans les locaux du maître d'ouvrage. "
        "Pour chaque lot, un protocole de recette sera établi conjointement "
        "dans les 10 premiers jours du marché. Les anomalies seront classées "
        "en trois niveaux de criticité (bloquante, majeure, mineure) avec des délais "
        "de correction contractualisés.", S["body"]))
    story.append(Paragraph("5.4 Gestion de projet et gouvernance", S["h2"]))
    story.append(Paragraph(
        "Le titulaire désignera un chef de projet dédié, interlocuteur unique "
        "du maître d'ouvrage, disponible pendant toute la durée du marché. "
        "Des comités de pilotage (COPIL) mensuels et des comités techniques (COTECH) "
        "bimensuels seront organisés. Un tableau de bord projet hebdomadaire "
        "(avancement, risques, actions) sera transmis par voie électronique. "
        "La méthode de conduite de projet Agile (Scrum ou SAFe) est préconisée "
        "avec des sprints de 2 semaines et des démonstrations régulières.", S["body"]))
    story.append(Spacer(1, 0.3*cm))

    # --- ARTICLE 6 – CRITERES ---
    story.append(Paragraph("Article 6 – Critères d'attribution", S["h1"]))
    story.append(Paragraph(
        "Les offres seront jugées selon les critères ci-dessous. Le marché sera attribué "
        "à l'offre économiquement la plus avantageuse, après classement des offres "
        "selon la méthode de notation définie au règlement de consultation (RC).", S["body"]))
    crit_rows = [["Critère d'attribution", "Pondération", "Sous-critères"]]
    for crit, pct in project["criteria"]:
        crit_rows.append([crit, f"{pct}%", "Détaillés au RC §4.3"])
    crit_tbl = Table(crit_rows, colWidths=[7*cm, 2.5*cm, 5.5*cm])
    crit_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, GRAY_LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.5, GRAY_MED),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(crit_tbl)
    story.append(Spacer(1, 0.3*cm))

    # --- ARTICLE 7 – DELAIS ---
    story.append(Paragraph("Article 7 – Délais d'exécution et planning", S["h1"]))
    story.append(Paragraph(
        f"La durée totale du marché est fixée à <b>{duration_label}</b> à compter "
        f"de la date de notification. Le planning prévisionnel ci-dessous est donné "
        f"à titre indicatif ; le titulaire proposera un planning détaillé dans son offre "
        f"en respectant les jalons contractuels obligatoires.", S["body"]))
    phase_rows = [["Phase", "Description", "Durée", "Jalon contractuel"]]
    for phase_name, phase_months in project["phases"]:
        phase_rows.append([phase_name, "Voir CCTP §5", f"{phase_months} mois", "Livrable signé"])
    phase_tbl = Table(phase_rows, colWidths=[4.5*cm, 4.5*cm, 2*cm, 4*cm])
    phase_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, GRAY_LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.5, GRAY_MED),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(phase_tbl)
    story.append(Paragraph(
        "Tout retard imputable au titulaire fera l'objet d'une pénalité de 1/1000 "
        "du montant total TTC du marché par jour calendaire de retard, "
        "plafonnée à 10% du montant total du marché.", S["body"]))
    story.append(Spacer(1, 0.3*cm))

    # --- ARTICLE 8 – BUDGET ---
    story.append(Paragraph("Article 8 – Budget et modalités financières", S["h1"]))
    story.append(Paragraph("8.1 Montant estimatif du marché", S["h2"]))
    story.append(Paragraph(
        f"Le montant estimatif global du marché est de <b>{fmt_euro(budget)}</b>. "
        f"Ce montant est donné à titre indicatif et ne constitue pas un engagement "
        f"de la part du pouvoir adjudicateur. Les prix seront fermes la première année "
        f"puis révisables annuellement selon la formule de révision définie au CCAP.", S["body"]))
    story.append(Paragraph("8.2 Décomposition budgétaire par lot", S["h2"]))
    budget_rows = [["Lot", "Intitulé", "Budget estimatif HT", "% du total"]]
    for lot_name, lot_desc, pct in project["lots"]:
        budget_rows.append([lot_name, lot_desc, fmt_euro(int(budget * pct / 100)), f"{pct}%"])
    budget_rows.append(["Total", "", fmt_euro(budget), "100%"])
    budget_tbl = Table(budget_rows, colWidths=[2*cm, 7*cm, 3.5*cm, 2.5*cm])
    budget_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [white, GRAY_LIGHT]),
        ("BACKGROUND", (0, -1), (-1, -1), BLUE_MED),
        ("TEXTCOLOR", (0, -1), (-1, -1), white),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, GRAY_MED),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(budget_tbl)
    story.append(Paragraph("8.3 Modalités de paiement", S["h2"]))
    story.append(Paragraph(
        "Le règlement des prestations s'effectuera par virement administratif "
        "dans un délai de 30 jours à compter de la réception de la facture, "
        "conformément aux articles L2192-10 et suivants du Code de la commande publique. "
        "Les factures seront émises sur la plateforme Chorus Pro au format Factur-X. "
        "Une avance forfaitaire de 20% du montant initial pourra être accordée "
        "conformément à l'article R2191-3 du Code de la commande publique.", S["body"]))
    story.append(Spacer(1, 0.3*cm))

    # --- ANNEXE A ---
    story.append(Paragraph("Annexe A – Conditions de candidature et pièces du marché", S["h1"]))
    story.append(Paragraph("A.1 Pièces constitutives du dossier de consultation (DCE)", S["h2"]))
    pieces = [
        "Règlement de consultation (RC)",
        "Cahier des Clauses Administratives Particulières (CCAP)",
        "Cahier des Clauses Techniques Particulières (CCTP) – présent document",
        "Bordereau des Prix Unitaires (BPU)",
        "Détail Quantitatif Estimatif (DQE)",
        "Acte d'engagement (DC3 / AE) et ses annexes",
    ]
    for p in pieces:
        story.append(Paragraph(f"• {p}", S["bullet"]))
    story.append(Paragraph("A.2 Capacités et références requises", S["h2"]))
    story.append(Paragraph(
        "Les candidats devront justifier de capacités professionnelles, techniques et financières "
        "suffisantes pour l'exécution du marché. Ils fourniront notamment : "
        "un chiffre d'affaires annuel moyen supérieur à 50% du montant du présent marché "
        "sur les 3 derniers exercices, au moins 3 références de marchés similaires "
        "exécutés dans les 5 dernières années, les certifications et qualifications requises "
        "mentionnées au présent CCTP.", S["body"]))
    story.append(Paragraph("A.3 Modalités de remise des offres", S["h2"]))
    story.append(Paragraph(
        "Les offres seront remises exclusivement par voie dématérialisée sur la plateforme "
        "de dématérialisation marches-publics.fr ou via le profil acheteur accessible "
        "depuis le site institutionnel du pouvoir adjudicateur, au plus tard "
        "le 15 mars 2026 à 17h00 (heure de Paris). Toute offre remise hors délai "
        "sera éliminée sans examen. Les questions des candidats seront posées "
        "uniquement par voie électronique avant le 1er mars 2026.", S["body"]))

    # --- ANNEXE B – GLOSSAIRE ---
    story.append(Paragraph("Annexe B – Glossaire et abréviations", S["h1"]))
    glossaire = [
        ("ANSSI", "Agence Nationale de la Sécurité des Systèmes d'Information"),
        ("AIPD", "Analyse d'Impact relative à la Protection des Données"),
        ("CCAP", "Cahier des Clauses Administratives Particulières"),
        ("CCTP", "Cahier des Clauses Techniques Particulières"),
        ("CPV", "Common Procurement Vocabulary – nomenclature européenne des marchés"),
        ("DINUM", "Direction Interministérielle du Numérique"),
        ("DSN", "Déclaration Sociale Nominative"),
        ("DSFR", "Design System de l'État Français"),
        ("MOA", "Maîtrise d'Ouvrage – le pouvoir adjudicateur"),
        ("MOE", "Maîtrise d'Œuvre – le titulaire du marché"),
        ("RGAA", "Référentiel Général d'Amélioration de l'Accessibilité"),
        ("RGPD", "Règlement Général sur la Protection des Données"),
        ("RPO", "Recovery Point Objective – perte de données maximale admissible"),
        ("RTO", "Recovery Time Objective – durée maximale d'interruption admissible"),
        ("SLA", "Service Level Agreement – accord de niveau de service"),
        ("TCO", "Total Cost of Ownership – coût total de possession sur la durée"),
    ]
    glos_rows = [["Abréviation", "Définition"]] + [[a, d] for a, d in glossaire]
    glos_tbl = Table(glos_rows, colWidths=[3.5*cm, 11.5*cm])
    glos_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, GRAY_LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.3, GRAY_MED),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(glos_tbl)

    doc.build(story)
    return filename


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    rng = random.Random(42)
    buyer_order = list(range(len(BUYERS)))
    rng.shuffle(buyer_order)

    total_bytes = 0
    for i, project in enumerate(PROJECTS, 1):
        buyer   = BUYERS[buyer_order[i - 1]]
        budget  = rng.choice(BUDGETS)
        dur_lbl, dur_months = rng.choice(DURATIONS)

        path = build_pdf(project, buyer, budget, dur_lbl, dur_months, i)
        size = path.stat().st_size
        total_bytes += size
        print(f"  [{i:02d}/20] {path.name}  {size / 1024:.0f} Ko  — {project['type']} / {buyer['name']}")

    total_mb = total_bytes / (1024 * 1024)
    print(f"\n[OK] 20 PDFs generes dans docs/  |  Taille totale : {total_mb:.1f} Mo")


if __name__ == "__main__":
    main()
