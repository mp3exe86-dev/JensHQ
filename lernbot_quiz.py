"""
lernbot_quiz.py
JensHQ – AZ-900 Fragenkatalog
Alle Fragen mit Antworten, Erklärungen und Themen-Zuordnung
Unterstützt Einzelauswahl (richtig: "B") und Mehrfachauswahl (richtig: ["A", "C"])
"""

FRAGEN = [
    # ──────────────────────────────────────────
    #  CLOUD-KONZEPTE
    # ──────────────────────────────────────────
    {
        "id": "cc_01",
        "thema": "Cloud-Konzepte",
        "frage": "Was ist ein Merkmal von IaaS?",
        "antworten": {
            "A": "Der Anbieter verwaltet Betriebssystem und Middleware",
            "B": "Du verwaltest das Betriebssystem, der Anbieter die Hardware",
            "C": "Du nutzt nur die fertige Anwendung",
            "D": "Der Anbieter übernimmt alles inklusive Datenpflege"
        },
        "richtig": "B",
        "erklaerung": "Bei IaaS stellt der Anbieter Hardware, Netzwerk und Virtualisierung bereit. Du bist verantwortlich für OS, Middleware, Runtime und Anwendungen. Beispiel: Azure Virtual Machines."
    },
    {
        "id": "cc_02",
        "thema": "Cloud-Konzepte",
        "frage": "Welches Modell beschreibt Microsoft 365 am besten?",
        "antworten": {
            "A": "IaaS",
            "B": "PaaS",
            "C": "SaaS",
            "D": "On-Premises"
        },
        "richtig": "C",
        "erklaerung": "Microsoft 365 ist SaaS. Du nutzt die fertige Anwendung – kein OS, keine Middleware, keine Infrastruktur musst du verwalten."
    },
    {
        "id": "cc_03",
        "thema": "Cloud-Konzepte",
        "frage": "Was ist ein Vorteil der Cloud gegenüber On-Premises?",
        "antworten": {
            "A": "Höhere Kontrolle über physische Hardware",
            "B": "Keine Internetverbindung notwendig",
            "C": "Elastische Skalierbarkeit nach Bedarf",
            "D": "Günstigere Lizenzkosten in jedem Fall"
        },
        "richtig": "C",
        "erklaerung": "Elastizität ist ein Kernvorteil der Cloud: Ressourcen können schnell hoch- und runterskaliert werden. On-Premises erfordert Vorab-Investitionen in Hardware."
    },
    {
        "id": "cc_04",
        "thema": "Cloud-Konzepte",
        "frage": "Welches Modell nutzt Azure App Service (Web Apps)?",
        "antworten": {
            "A": "IaaS",
            "B": "PaaS",
            "C": "SaaS",
            "D": "FaaS"
        },
        "richtig": "B",
        "erklaerung": "Azure App Service ist PaaS. Du deployst deinen Code, Azure verwaltet OS, Patches, Skalierung und Infrastruktur."
    },
    {
        "id": "cc_05",
        "thema": "Cloud-Konzepte",
        "frage": "Was beschreibt das Shared Responsibility Model?",
        "antworten": {
            "A": "Kunde und Anbieter teilen sich die monatlichen Kosten",
            "B": "Der Anbieter ist immer für alles verantwortlich",
            "C": "Verantwortlichkeiten für Sicherheit sind je nach Servicemodell aufgeteilt",
            "D": "Nur der Kunde trägt Verantwortung für Datensicherheit"
        },
        "richtig": "C",
        "erklaerung": "Das Shared Responsibility Model definiert wer für was verantwortlich ist. Bei IaaS trägt der Kunde mehr Verantwortung, bei SaaS fast keine. Der Anbieter ist immer für physische Infrastruktur verantwortlich."
    },
    {
        "id": "cc_06",
        "thema": "Cloud-Konzepte",
        "frage": "Was ist eine Private Cloud?",
        "antworten": {
            "A": "Cloud-Dienste die nur über VPN erreichbar sind",
            "B": "Cloud-Infrastruktur die exklusiv für eine Organisation betrieben wird",
            "C": "Ein Microsoft-Rechenzentrum für Einzelpersonen",
            "D": "Azure-Dienste mit privatem Pricing"
        },
        "richtig": "B",
        "erklaerung": "Eine Private Cloud wird exklusiv für eine Organisation betrieben. Sie bietet mehr Kontrolle, ist aber teurer als Public Cloud."
    },
    {
        "id": "cc_07",
        "thema": "Cloud-Konzepte",
        "frage": "Welche ZWEI Aussagen beschreiben Vorteile von Cloud Computing korrekt?",
        "antworten": {
            "A": "Kapitalausgaben (CapEx) werden höher",
            "B": "Betriebsausgaben (OpEx) statt Kapitalausgaben (CapEx)",
            "C": "Keine Vorab-Investitionen in Hardware nötig",
            "D": "Volle physische Kontrolle über alle Server"
        },
        "richtig": ["B", "C"],
        "erklaerung": "Cloud wechselt von CapEx (Kauf von Hardware) zu OpEx (laufende Kosten). Keine Vorab-Investitionen nötig – du zahlst nur was du nutzt."
    },
    {
        "id": "cc_08",
        "thema": "Cloud-Konzepte",
        "frage": "Was ist eine Hybrid Cloud?",
        "antworten": {
            "A": "Eine Kombination aus Public und Private Cloud",
            "B": "Zwei Public Cloud Anbieter gleichzeitig",
            "C": "Eine Cloud nur für hybride Arbeitsmodelle",
            "D": "Azure + AWS kombiniert"
        },
        "richtig": "A",
        "erklaerung": "Hybrid Cloud kombiniert On-Premises/Private Cloud mit Public Cloud. Daten und Anwendungen können zwischen beiden wechseln – bietet Flexibilität und mehr Kontrollmöglichkeiten."
    },
    {
        "id": "cc_09",
        "thema": "Cloud-Konzepte",
        "frage": "Welche ZWEI Merkmale gehören zu PaaS?",
        "antworten": {
            "A": "Du verwaltest das Betriebssystem selbst",
            "B": "Der Anbieter verwaltet OS und Middleware",
            "C": "Du deployest nur deinen Code/deine Anwendung",
            "D": "Du nutzt eine fertige Software ohne Anpassung"
        },
        "richtig": ["B", "C"],
        "erklaerung": "Bei PaaS verwaltet der Anbieter OS, Middleware und Runtime. Du kümmerst dich nur um deinen Code und deine Daten. Beispiele: Azure App Service, Azure SQL Database."
    },
    {
        "id": "cc_10",
        "thema": "Cloud-Konzepte",
        "frage": "Was bedeutet 'Hochverfügbarkeit' in der Cloud?",
        "antworten": {
            "A": "Der Dienst ist 100% der Zeit verfügbar ohne Ausnahme",
            "B": "Maximale Verfügbarkeit durch Redundanz, mit definierter SLA",
            "C": "Der Dienst läuft auf besonders schneller Hardware",
            "D": "Nur Premium-Kunden erhalten hohe Verfügbarkeit"
        },
        "richtig": "B",
        "erklaerung": "Hochverfügbarkeit bedeutet maximale Betriebszeit durch Redundanz – nicht 100%, sondern eine garantierte SLA (z.B. 99,9%). Ausfälle werden minimiert aber nicht ausgeschlossen."
    },

    # ──────────────────────────────────────────
    #  SLA-REGELN
    # ──────────────────────────────────────────
    {
        "id": "sla_01",
        "thema": "SLA-Regeln",
        "frage": "Was bedeutet eine SLA von 99,9%?",
        "antworten": {
            "A": "Der Dienst ist maximal 8,76 Stunden pro Jahr nicht verfügbar",
            "B": "Der Dienst ist maximal 1 Minute pro Tag nicht verfügbar",
            "C": "Der Dienst ist garantiert immer verfügbar",
            "D": "Der Dienst hat 99,9% Sicherheit gegen Angriffe"
        },
        "richtig": "A",
        "erklaerung": "99,9% SLA = 0,1% Ausfallzeit = ca. 8,76 Stunden/Jahr oder ~43,8 Minuten/Monat. Merkhilfe: Jede weitere 9 reduziert die Ausfallzeit um Faktor 10."
    },
    {
        "id": "sla_02",
        "thema": "SLA-Regeln",
        "frage": "Wie berechnet sich die Composite SLA bei zwei Diensten (99,9% und 99,95%)?",
        "antworten": {
            "A": "99,9% + 99,95% = 199,85%",
            "B": "99,9% × 99,95% = ~99,85%",
            "C": "Min(99,9%, 99,95%) = 99,9%",
            "D": "Max(99,9%, 99,95%) = 99,95%"
        },
        "richtig": "B",
        "erklaerung": "Composite SLA = SLA_A × SLA_B. Bei zwei Diensten: 0,999 × 0,9995 = ~99,85%. Die kombinierte SLA ist immer schlechter als die einzelnen SLAs."
    },
    {
        "id": "sla_03",
        "thema": "SLA-Regeln",
        "frage": "Welche Maßnahme erhöht die effektive SLA am meisten?",
        "antworten": {
            "A": "Mehr RAM in der VM",
            "B": "Deployment in mehrere Availability Zones",
            "C": "Größere Festplatte wählen",
            "D": "Premium Support buchen"
        },
        "richtig": "B",
        "erklaerung": "Availability Zones sind physisch getrennte Rechenzentren. Deployment über mehrere Zonen erhöht die SLA auf 99,99%+. RAM oder Storage ändern die SLA nicht."
    },
    {
        "id": "sla_04",
        "thema": "SLA-Regeln",
        "frage": "Was ist KEIN Faktor der die Azure SLA beeinflusst?",
        "antworten": {
            "A": "Anzahl der Availability Zones",
            "B": "Verwendung von Availability Sets",
            "C": "Die Farbe des Azure Portals",
            "D": "Region Pairs für Disaster Recovery"
        },
        "richtig": "C",
        "erklaerung": "SLA wird durch Redundanz und Architektur beeinflusst. Das Portal-Design hat keinerlei Einfluss."
    },
    {
        "id": "sla_05",
        "thema": "SLA-Regeln",
        "frage": "Eine VM hat SLA 99,9% und eine SQL Database 99,99%. Welche Composite SLA ergibt sich?",
        "antworten": {
            "A": "99,99%",
            "B": "99,9%",
            "C": "~99,89%",
            "D": "~99,80%"
        },
        "richtig": "C",
        "erklaerung": "0,999 × 0,9999 = 0,9989 = ~99,89%. Die Composite SLA ist schlechter als die schlechteste Einzel-SLA."
    },
    {
        "id": "sla_06",
        "thema": "SLA-Regeln",
        "frage": "Welche ZWEI Aussagen über SLAs sind korrekt?",
        "antworten": {
            "A": "Kostenlose Azure-Dienste haben keine SLA-Garantie",
            "B": "SLAs gelten auch für kostenlose Dienste",
            "C": "Höhere Redundanz verbessert die effektive SLA",
            "D": "SLAs können nicht durch Architektur beeinflusst werden"
        },
        "richtig": ["A", "C"],
        "erklaerung": "Kostenlose Azure-Dienste (Free Tier) haben keine SLA-Garantie. Durch Redundanz (mehrere Zonen, Regionen) kann die effektive SLA der Gesamtlösung erhöht werden."
    },
    {
        "id": "sla_07",
        "thema": "SLA-Regeln",
        "frage": "Was ist ein Azure Region Pair?",
        "antworten": {
            "A": "Zwei VMs die sich gegenseitig absichern",
            "B": "Zwei Azure-Regionen die für Disaster Recovery gekoppelt sind",
            "C": "Ein Backup-Dienst für Azure Storage",
            "D": "Zwei Subscriptions unter einem Tenant"
        },
        "richtig": "B",
        "erklaerung": "Region Pairs sind zwei Azure-Regionen innerhalb derselben Geografie die für gegenseitiges Failover ausgelegt sind. Bei Ausfall einer Region übernimmt die gepaarte Region."
    },
    {
        "id": "sla_08",
        "thema": "SLA-Regeln",
        "frage": "Was sind Availability Zones?",
        "antworten": {
            "A": "Verschiedene Azure-Regionen weltweit",
            "B": "Physisch getrennte Rechenzentren innerhalb einer Region",
            "C": "Virtuelle Netzwerke mit hoher Verfügbarkeit",
            "D": "Backup-Standorte außerhalb von Azure"
        },
        "richtig": "B",
        "erklaerung": "Availability Zones sind physisch isolierte Rechenzentren innerhalb einer Azure-Region mit eigener Stromversorgung, Kühlung und Netzwerk. Deployment über Zonen erhöht die SLA auf 99,99%."
    },

    # ──────────────────────────────────────────
    #  IDENTITY & SECURITY
    # ──────────────────────────────────────────
    {
        "id": "id_01",
        "thema": "Identity & Security",
        "frage": "Was ist der Unterschied zwischen Authentifizierung und Autorisierung?",
        "antworten": {
            "A": "Authentifizierung = Was darf ich? Autorisierung = Wer bin ich?",
            "B": "Beides bedeutet dasselbe in Azure",
            "C": "Authentifizierung = Wer bin ich? Autorisierung = Was darf ich?",
            "D": "Authentifizierung gilt nur für Menschen, Autorisierung für Apps"
        },
        "richtig": "C",
        "erklaerung": "AuthN = Identität prüfen: 'Wer bist du?' AuthZ = Berechtigungen prüfen: 'Was darfst du?'"
    },
    {
        "id": "id_02",
        "thema": "Identity & Security",
        "frage": "Was ist Azure Active Directory (AAD)?",
        "antworten": {
            "A": "Ein lokaler Domain Controller in der Cloud",
            "B": "Ein cloudbasierter Identity & Access Management Dienst",
            "C": "Ein Backup-Dienst für Active Directory",
            "D": "Ein VPN-Dienst für sichere Verbindungen"
        },
        "richtig": "B",
        "erklaerung": "Azure AD (jetzt Microsoft Entra ID) ist Microsofts cloudbasierter IAM-Dienst. Er ist KEIN klassischer AD Domain Controller."
    },
    {
        "id": "id_03",
        "thema": "Identity & Security",
        "frage": "Welches sind die drei Zero Trust Prinzipien?",
        "antworten": {
            "A": "Verify, Block, Isolate",
            "B": "Verify explicitly, Use least privilege, Assume breach",
            "C": "Trust, Verify, Monitor",
            "D": "Authenticate, Authorize, Audit"
        },
        "richtig": "B",
        "erklaerung": "Zero Trust: 1) Verify explicitly 2) Use least privilege 3) Assume breach. Kein implizites Vertrauen im Netzwerk."
    },
    {
        "id": "id_04",
        "thema": "Identity & Security",
        "frage": "Was macht Microsoft Defender for Cloud?",
        "antworten": {
            "A": "Antivirus für Azure VMs",
            "B": "Cloud Security Posture Management und Bedrohungsschutz",
            "C": "Firewall für Azure Virtual Networks",
            "D": "Backup-Lösung für Azure Ressourcen"
        },
        "richtig": "B",
        "erklaerung": "Microsoft Defender for Cloud bietet CSPM und CWP. Es bewertet deine Sicherheitskonfiguration und schützt vor Bedrohungen."
    },
    {
        "id": "id_05",
        "thema": "Identity & Security",
        "frage": "Was ist Multi-Factor Authentication (MFA)?",
        "antworten": {
            "A": "Login mit mehreren Passwörtern",
            "B": "Verifikation über mehrere unabhängige Faktoren (Wissen, Besitz, Biometrie)",
            "C": "Ein Dienst der mehrere Azure-Tenants verbindet",
            "D": "Verschlüsselung mit mehreren Schlüsseln"
        },
        "richtig": "B",
        "erklaerung": "MFA kombiniert mindestens zwei Faktoren: Wissen (Passwort), Besitz (Smartphone), Biometrie (Fingerabdruck)."
    },
    {
        "id": "id_06",
        "thema": "Identity & Security",
        "frage": "Welche ZWEI Dienste gehören zu Azure Identity?",
        "antworten": {
            "A": "Azure Firewall",
            "B": "Azure Active Directory (Entra ID)",
            "C": "Multi-Factor Authentication (MFA)",
            "D": "Microsoft Sentinel"
        },
        "richtig": ["B", "C"],
        "erklaerung": "Azure AD (Entra ID) und MFA sind Identity-Dienste. Azure Firewall und Sentinel gehören zu Security/Netzwerk."
    },
    {
        "id": "id_07",
        "thema": "Identity & Security",
        "frage": "Was ist Azure Conditional Access?",
        "antworten": {
            "A": "Ein VPN-Dienst für bedingte Verbindungen",
            "B": "Richtlinien die Zugriff basierend auf Bedingungen erlauben oder blockieren",
            "C": "Eine Firewall-Regel für bedingte IP-Adressen",
            "D": "Ein Backup-Mechanismus für AAD"
        },
        "richtig": "B",
        "erklaerung": "Conditional Access wertet Signale aus (Benutzer, Gerät, Standort, App) und entscheidet dann ob Zugriff gewährt, blockiert oder MFA verlangt wird."
    },
    {
        "id": "id_08",
        "thema": "Identity & Security",
        "frage": "Was ist der Unterschied zwischen Azure AD und lokalem Active Directory?",
        "antworten": {
            "A": "Kein Unterschied, beide sind identisch",
            "B": "Azure AD nutzt HTTP/HTTPS und OAuth, lokales AD nutzt Kerberos/LDAP",
            "C": "Lokales AD ist moderner als Azure AD",
            "D": "Azure AD kann keine Gruppen verwalten"
        },
        "richtig": "B",
        "erklaerung": "Azure AD ist für cloudbasierte Authentifizierung mit modernen Protokollen (OAuth, OIDC, SAML) ausgelegt. Lokales AD nutzt ältere Protokolle wie Kerberos und LDAP."
    },
    {
        "id": "id_09",
        "thema": "Identity & Security",
        "frage": "Welche ZWEI Aussagen über Microsoft Sentinel sind korrekt?",
        "antworten": {
            "A": "Sentinel ist ein SIEM und SOAR Dienst",
            "B": "Sentinel ersetzt Azure Firewall",
            "C": "Sentinel sammelt und analysiert Sicherheitsdaten aus verschiedenen Quellen",
            "D": "Sentinel ist ein Identity-Dienst"
        },
        "richtig": ["A", "C"],
        "erklaerung": "Microsoft Sentinel ist ein cloudbasiertes SIEM (Security Information and Event Management) und SOAR (Security Orchestration, Automation, Response). Es sammelt Logs und erkennt Bedrohungen."
    },
    {
        "id": "id_10",
        "thema": "Identity & Security",
        "frage": "Was ist Privileged Identity Management (PIM)?",
        "antworten": {
            "A": "Ein Passwort-Manager für Admins",
            "B": "Just-in-Time Zugriff auf privilegierte Rollen mit Genehmigungsworkflow",
            "C": "Ein Tool zum Verwalten von Service Principals",
            "D": "MFA speziell für Admin-Accounts"
        },
        "richtig": "B",
        "erklaerung": "PIM ermöglicht Just-in-Time privilegierten Zugriff: Admins aktivieren ihre Rolle nur wenn nötig, für eine begrenzte Zeit, mit optionalem Genehmigungsworkflow."
    },

    # ──────────────────────────────────────────
    #  PRICING & COST MANAGEMENT
    # ──────────────────────────────────────────
    {
        "id": "price_01",
        "thema": "Pricing & Cost Management",
        "frage": "Wofür wird der Azure TCO Calculator verwendet?",
        "antworten": {
            "A": "Um den genauen Preis einer Azure VM zu berechnen",
            "B": "Um On-Premises Kosten mit Azure Kosten zu vergleichen",
            "C": "Um Budgets in Azure Cost Management einzurichten",
            "D": "Um Rabatte für Enterprise Agreements zu berechnen"
        },
        "richtig": "B",
        "erklaerung": "TCO = Total Cost of Ownership. Vergleicht On-Premises Kosten mit Azure. Für konkrete Azure-Preise den Pricing Calculator nutzen."
    },
    {
        "id": "price_02",
        "thema": "Pricing & Cost Management",
        "frage": "Was sind Azure Reservations?",
        "antworten": {
            "A": "Reservierte IP-Adressen in Azure",
            "B": "Vorauszahlung für 1-3 Jahre Ressourcennutzung mit Rabatt",
            "C": "Gespeicherte ARM-Templates",
            "D": "Backup-Slots für kritische VMs"
        },
        "richtig": "B",
        "erklaerung": "Azure Reservations ermöglichen Vorauszahlung für 1 oder 3 Jahre mit bis zu 72% Rabatt. Sinnvoll für stabile, vorhersehbare Workloads."
    },
    {
        "id": "price_03",
        "thema": "Pricing & Cost Management",
        "frage": "Welcher Faktor beeinflusst Azure-Kosten NICHT?",
        "antworten": {
            "A": "Gewählte Azure Region",
            "B": "VM-Größe und SKU",
            "C": "Anzahl der Azure-Portal-Logins",
            "D": "Ausgehender Datenverkehr (Egress)"
        },
        "richtig": "C",
        "erklaerung": "Portal-Logins kosten nichts. Region, VM-Größe, Storage, Netzwerk-Egress und Laufzeit beeinflussen die Kosten."
    },
    {
        "id": "price_04",
        "thema": "Pricing & Cost Management",
        "frage": "Was ist Azure Cost Management?",
        "antworten": {
            "A": "Ein Tool zum automatischen Herunterfahren von VMs",
            "B": "Ein Dienst zum Überwachen, Analysieren und Optimieren von Azure-Kosten",
            "C": "Ein Rabattprogramm für Enterprise-Kunden",
            "D": "Ein Billing-Portal für Rechnungen"
        },
        "richtig": "B",
        "erklaerung": "Azure Cost Management ermöglicht Kostenüberwachung, Budgets mit Alerts, Kostenanalyse nach Tags/Ressourcen und Empfehlungen zur Kostenoptimierung."
    },
    {
        "id": "price_05",
        "thema": "Pricing & Cost Management",
        "frage": "Welche ZWEI Faktoren beeinflussen den Preis einer Azure VM?",
        "antworten": {
            "A": "Die Anzahl der Benutzer die darauf zugreifen",
            "B": "Die gewählte Region (z.B. West Europe vs East US)",
            "C": "Die VM-Größe (CPU/RAM)",
            "D": "Die Farbe des VM-Icons im Portal"
        },
        "richtig": ["B", "C"],
        "erklaerung": "Region und VM-Größe sind direkte Kostenfaktoren. Preise variieren je nach Region erheblich. Mehr CPU/RAM = höherer Preis."
    },
    {
        "id": "price_06",
        "thema": "Pricing & Cost Management",
        "frage": "Was ist der Azure Spot Price?",
        "antworten": {
            "A": "Der günstigste verfügbare VM-Preis zu einem bestimmten Zeitpunkt für überschüssige Kapazität",
            "B": "Ein Festpreis für alle Azure VMs",
            "C": "Der Preis für Reserved Instances",
            "D": "Ein Notfallpreis bei hoher Nachfrage"
        },
        "richtig": "A",
        "erklaerung": "Azure Spot VMs nutzen überschüssige Azure-Kapazität zu stark reduzierten Preisen (bis 90% günstiger). Nachteil: können jederzeit unterbrochen werden."
    },
    {
        "id": "price_07",
        "thema": "Pricing & Cost Management",
        "frage": "Was ist der Unterschied zwischen CapEx und OpEx in der Cloud?",
        "antworten": {
            "A": "Kein Unterschied in der Cloud",
            "B": "CapEx = einmalige Vorabkosten (Hardware), OpEx = laufende Betriebskosten",
            "C": "OpEx = Vorabkosten, CapEx = laufende Kosten",
            "D": "CapEx ist immer teurer als OpEx"
        },
        "richtig": "B",
        "erklaerung": "Cloud verschiebt IT-Kosten von CapEx (Server kaufen) zu OpEx (monatlich zahlen). Das verbessert die Liquidität und ermöglicht flexiblere Investitionen."
    },

    # ──────────────────────────────────────────
    #  GOVERNANCE
    # ──────────────────────────────────────────
    {
        "id": "gov_01",
        "thema": "Governance",
        "frage": "Was ist der Unterschied zwischen Azure Policy und RBAC?",
        "antworten": {
            "A": "Kein Unterschied, beide machen dasselbe",
            "B": "RBAC = Was darf getan werden, Policy = Wer darf etwas tun",
            "C": "RBAC = Wer darf etwas tun, Policy = Was darf getan werden",
            "D": "Policy gilt nur für Ressourcengruppen, RBAC für Subscriptions"
        },
        "richtig": "C",
        "erklaerung": "RBAC steuert WER Aktionen durchführen darf. Azure Policy steuert WAS erlaubt ist. Beide ergänzen sich."
    },
    {
        "id": "gov_02",
        "thema": "Governance",
        "frage": "Welche RBAC-Rolle hat vollen Zugriff inkl. Rechtevergabe?",
        "antworten": {
            "A": "Contributor",
            "B": "Reader",
            "C": "Owner",
            "D": "Administrator"
        },
        "richtig": "C",
        "erklaerung": "Owner hat vollen Zugriff UND kann Rollen vergeben. Contributor kann alles außer Rechtevergabe. Reader hat nur Lesezugriff."
    },
    {
        "id": "gov_03",
        "thema": "Governance",
        "frage": "Was ist die richtige Azure-Hierarchie von oben nach unten?",
        "antworten": {
            "A": "Subscription → Management Group → Resource Group → Resource",
            "B": "Management Group → Subscription → Resource Group → Resource",
            "C": "Resource Group → Subscription → Management Group → Resource",
            "D": "Management Group → Resource Group → Subscription → Resource"
        },
        "richtig": "B",
        "erklaerung": "Azure Hierarchie: Management Groups → Subscriptions → Resource Groups → Resources. Policies und RBAC werden von oben nach unten vererbt."
    },
    {
        "id": "gov_04",
        "thema": "Governance",
        "frage": "Was macht Azure Blueprints?",
        "antworten": {
            "A": "Erstellt visuelle Diagramme der Azure-Infrastruktur",
            "B": "Paketiert Policies, RBAC und ARM-Templates für wiederholbare Umgebungen",
            "C": "Optimiert automatisch Azure-Kosten",
            "D": "Erstellt Backup-Pläne für Azure Ressourcen"
        },
        "richtig": "B",
        "erklaerung": "Azure Blueprints kombiniert Policies, RBAC und ARM-Templates für konsistente, konforme Umgebungen."
    },
    {
        "id": "gov_05",
        "thema": "Governance",
        "frage": "Was ist Azure Resource Lock?",
        "antworten": {
            "A": "Ein Passwortschutz für Azure-Ressourcen",
            "B": "Verhindert versehentliches Löschen oder Ändern von Ressourcen",
            "C": "Sperrt eine Subscription für neue Ressourcen",
            "D": "Ein Compliance-Tool für regulierte Branchen"
        },
        "richtig": "B",
        "erklaerung": "Resource Locks verhindern versehentliche Änderungen: 'ReadOnly' verhindert alle Änderungen, 'Delete' verhindert nur das Löschen. Sinnvoll für kritische Produktionsressourcen."
    },
    {
        "id": "gov_06",
        "thema": "Governance",
        "frage": "Welche ZWEI Aussagen über Azure Tags sind korrekt?",
        "antworten": {
            "A": "Tags sind Name-Wert-Paare zur Kategorisierung von Ressourcen",
            "B": "Tags werden automatisch auf alle Ressourcen einer Resource Group vererbt",
            "C": "Tags können für Kostenzuordnung nach Abteilung verwendet werden",
            "D": "Jede Ressource kann maximal 3 Tags haben"
        },
        "richtig": ["A", "C"],
        "erklaerung": "Tags sind Name-Wert-Paare (z.B. Umgebung:Produktion) zur Organisation. Sie werden NICHT automatisch vererbt und können für Kostenreporting nach Kostenstellen genutzt werden."
    },
    {
        "id": "gov_07",
        "thema": "Governance",
        "frage": "Was ist der Azure Policy Compliance Score?",
        "antworten": {
            "A": "Ein Sicherheitsscore für Azure Ressourcen",
            "B": "Prozentsatz der Ressourcen die den zugewiesenen Policies entsprechen",
            "C": "Eine Bewertung der Azure SLA Einhaltung",
            "D": "Ein Score für die Kosteneffizienz"
        },
        "richtig": "B",
        "erklaerung": "Der Compliance Score zeigt welcher Prozentsatz deiner Ressourcen den zugewiesenen Azure Policies entspricht. Hilft bei der Identifizierung nicht-konformer Ressourcen."
    },

    # ──────────────────────────────────────────
    #  AZURE DIENSTE
    # ──────────────────────────────────────────
    {
        "id": "svc_01",
        "thema": "Azure Dienste",
        "frage": "Was ist Azure Blob Storage am besten geeignet für?",
        "antworten": {
            "A": "Relationale Datenbankdaten",
            "B": "Unstrukturierte Daten wie Bilder, Videos, Backups",
            "C": "VM Betriebssystemdateien",
            "D": "Active Directory Konfigurationsdaten"
        },
        "richtig": "B",
        "erklaerung": "Azure Blob Storage ist für unstrukturierte Daten optimiert: Bilder, Videos, Backups, Logs. Für VMs nimm Managed Disks, für Datenbanken Azure SQL."
    },
    {
        "id": "svc_02",
        "thema": "Azure Dienste",
        "frage": "Was ist Azure Virtual Network (VNet)?",
        "antworten": {
            "A": "Ein VPN-Dienst für Home Office Mitarbeiter",
            "B": "Ein privates Netzwerk in Azure für isolierte Kommunikation",
            "C": "Ein globales CDN für schnelle Inhaltsauslieferung",
            "D": "Ein Monitoring-Dienst für Netzwerkperformance"
        },
        "richtig": "B",
        "erklaerung": "Ein VNet ist ein logisch isoliertes Netzwerk in Azure. Ressourcen im selben VNet kommunizieren sicher. VNets können per Peering oder VPN Gateway verbunden werden."
    },
    {
        "id": "svc_03",
        "thema": "Azure Dienste",
        "frage": "Was ist der Unterschied zwischen Azure SQL Database und SQL Server auf einer VM?",
        "antworten": {
            "A": "Kein Unterschied",
            "B": "Azure SQL Database ist PaaS, SQL auf VM ist IaaS",
            "C": "Azure SQL Database ist immer günstiger",
            "D": "SQL auf VM unterstützt keine Windows Authentication"
        },
        "richtig": "B",
        "erklaerung": "Azure SQL Database ist PaaS: Microsoft verwaltet Patching, Backups, HA. SQL auf VM ist IaaS: du verwaltest OS und SQL selbst, hast aber mehr Kontrolle."
    },
    {
        "id": "svc_04",
        "thema": "Azure Dienste",
        "frage": "Was ist Azure CDN?",
        "antworten": {
            "A": "Ein Netzwerk zur schnellen Auslieferung von Inhalten über global verteilte Server",
            "B": "Ein VPN-Dienst für sichere Verbindungen",
            "C": "Ein DNS-Dienst für Azure-Domains",
            "D": "Ein Monitoring-Tool für Netzwerklatenz"
        },
        "richtig": "A",
        "erklaerung": "Azure CDN (Content Delivery Network) verteilt Inhalte über global verteilte Edge-Server. Nutzer erhalten Inhalte vom nächstgelegenen Server – reduziert Latenz."
    },
    {
        "id": "svc_05",
        "thema": "Azure Dienste",
        "frage": "Welche ZWEI Speichertypen bietet Azure an?",
        "antworten": {
            "A": "Blob Storage für unstrukturierte Daten",
            "B": "Quantum Storage für Quantencomputing",
            "C": "Azure Files für SMB/NFS Dateifreigaben",
            "D": "Pixel Storage für Bilddaten"
        },
        "richtig": ["A", "C"],
        "erklaerung": "Azure Blob Storage (unstrukturierte Daten) und Azure Files (SMB/NFS Dateifreigaben, Lift-and-Shift für Fileserver) sind reale Azure Speicherdienste."
    },
    {
        "id": "svc_06",
        "thema": "Azure Dienste",
        "frage": "Was ist Azure Load Balancer?",
        "antworten": {
            "A": "Verteilt eingehenden Netzwerkverkehr auf mehrere Backend-Ressourcen",
            "B": "Optimiert die CPU-Last einer einzelnen VM",
            "C": "Ein Tool zum Balancieren von Azure-Kosten",
            "D": "Ein DNS-Dienst für Lastverteilung"
        },
        "richtig": "A",
        "erklaerung": "Azure Load Balancer verteilt eingehenden Traffic auf mehrere VMs oder Dienste. Verbessert Verfügbarkeit und Skalierbarkeit. Arbeitet auf Layer 4 (TCP/UDP)."
    },
    {
        "id": "svc_07",
        "thema": "Azure Dienste",
        "frage": "Was ist Azure Functions?",
        "antworten": {
            "A": "Eine Sammlung von Azure Management Funktionen",
            "B": "Serverless Computing – Code ausführen ohne Server zu verwalten",
            "C": "Ein Tool zum Erstellen von Azure Policies",
            "D": "Ein Monitoring-Dienst für Azure-Ressourcen"
        },
        "richtig": "B",
        "erklaerung": "Azure Functions ist Serverless (FaaS). Du schreibst nur den Code, Azure kümmert sich um alles andere. Abrechnung nur für tatsächliche Ausführungszeit."
    },
    {
        "id": "svc_08",
        "thema": "Azure Dienste",
        "frage": "Welche ZWEI Aussagen über Azure Kubernetes Service (AKS) sind korrekt?",
        "antworten": {
            "A": "AKS ist ein verwalteter Kubernetes-Dienst",
            "B": "AKS erfordert manuelle Installation von Kubernetes",
            "C": "AKS eignet sich für containerbasierte Anwendungen",
            "D": "AKS kann nur Windows-Container ausführen"
        },
        "richtig": ["A", "C"],
        "erklaerung": "AKS ist ein vollständig verwalteter Kubernetes-Dienst von Azure. Ideal für containerbasierte Workloads – Azure übernimmt die Kubernetes-Control-Plane."
    },
    {
        "id": "svc_09",
        "thema": "Azure Dienste",
        "frage": "Was ist Azure Monitor?",
        "antworten": {
            "A": "Ein Antivirusprogramm für Azure VMs",
            "B": "Eine Plattform zum Sammeln, Analysieren und Reagieren auf Telemetriedaten",
            "C": "Ein Tool zum Überwachen von Azure-Kosten",
            "D": "Ein Netzwerk-Monitoring Tool"
        },
        "richtig": "B",
        "erklaerung": "Azure Monitor sammelt Metriken und Logs aus Azure-Ressourcen, ermöglicht Alerts, Dashboards und Integration mit Log Analytics. Zentrale Monitoring-Plattform in Azure."
    },
    {
        "id": "svc_10",
        "thema": "Azure Dienste",
        "frage": "Was ist der Unterschied zwischen Azure Backup und Azure Site Recovery?",
        "antworten": {
            "A": "Kein Unterschied, beide machen dasselbe",
            "B": "Backup = Datensicherung, Site Recovery = Disaster Recovery / Failover",
            "C": "Site Recovery ist nur für on-premises",
            "D": "Backup ist nur für Datenbanken"
        },
        "richtig": "B",
        "erklaerung": "Azure Backup sichert Daten (VMs, Datenbanken, Files). Azure Site Recovery repliziert VMs für Disaster Recovery und ermöglicht Failover bei einem Ausfall."
    },
]

# Themen-Übersicht
THEMEN = list(dict.fromkeys(f["thema"] for f in FRAGEN))

def get_fragen_by_thema(thema: str) -> list[dict]:
    return [f for f in FRAGEN if f["thema"] == thema]

def get_frage_by_id(frage_id: str) -> dict | None:
    return next((f for f in FRAGEN if f["id"] == frage_id), None)

def ist_mehrfachauswahl(frage: dict) -> bool:
    return isinstance(frage.get("richtig"), list)

def ist_antwort_korrekt(frage: dict, antwort) -> bool:
    """Prüft ob eine Antwort korrekt ist (Einzel- oder Mehrfachauswahl)."""
    richtig = frage["richtig"]
    if isinstance(richtig, list):
        if isinstance(antwort, list):
            return sorted(antwort) == sorted(richtig)
        return False
    return antwort == richtig

if __name__ == "__main__":
    mehrfach = [f for f in FRAGEN if isinstance(f.get("richtig"), list)]
    print(f"Fragenkatalog: {len(FRAGEN)} Fragen in {len(THEMEN)} Themen")
    print(f"Davon Mehrfachauswahl: {len(mehrfach)}")
    for t in THEMEN:
        print(f"  {t}: {len(get_fragen_by_thema(t))} Fragen")