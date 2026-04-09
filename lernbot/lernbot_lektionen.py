"""
lernbot_lektionen.py
JensHQ – Tägliche Lektionen (kein Quiz!)
Stil: Erklärungen wie für 10-Jährige / Schrödinger Programmiert
Themen: Docker, Kubernetes, CI/CD, Terraform, IaC, Git, Netzwerk
3 Lektionen pro Tag (alle 6h: 07:00 / 13:00 / 19:00)
"""

LEKTIONEN = [

    # ══════════════════════════════════════════════
    #  DOCKER
    # ══════════════════════════════════════════════
    {
        "id": "docker_01",
        "thema": "Docker",
        "titel": "Was ist Docker? 🐳",
        "inhalt": (
            "🐳 <b>Docker – Die Lunchbox der IT</b>\n\n"
            "Stell dir vor, du kochst ein Gericht und packst <b>alles</b> – Zutaten, Töpfe, Gewürze, Rezept – in eine einzige Lunchbox.\n\n"
            "Diese Lunchbox kannst du jemandem geben, und er kocht <i>exakt dasselbe Gericht</i> – egal ob er eine andere Küche hat, einen anderen Herd, oder in einem anderen Land wohnt.\n\n"
            "📦 <b>Genau das macht Docker mit Software.</b>\n\n"
            "Eine App braucht normalerweise: bestimmte Bibliotheken, eine bestimmte Python-Version, bestimmte Konfigurationsdateien.\n\n"
            "Ohne Docker passiert das: \"Bei mir läuft es!\" – \"Bei mir nicht.\"\n"
            "Mit Docker: Die App läuft überall gleich. Immer.\n\n"
            "🔑 <b>Wichtige Begriffe:</b>\n"
            "• <b>Image</b> = das Rezept (unveränderlich)\n"
            "• <b>Container</b> = die fertige Lunchbox (läuft gerade)\n"
            "• <b>Dockerfile</b> = dein Kochbuch (wie man das Image baut)\n\n"
            "💡 <i>Merksatz: Docker packt eine App + alles was sie braucht in eine Box. Die Box läuft überall.</i>"
        ),
    },
    {
        "id": "docker_02",
        "thema": "Docker",
        "titel": "Docker Images & Container 📦",
        "inhalt": (
            "📦 <b>Image vs. Container – Kuchenform vs. Kuchen</b>\n\n"
            "Ein <b>Docker Image</b> ist wie eine Kuchenform.\n"
            "Du kannst damit beliebig viele Kuchen backen – die Form selbst verändert sich nie.\n\n"
            "Ein <b>Container</b> ist der fertige Kuchen.\n"
            "Du kannst 10 Container aus dem gleichen Image starten – alle sind identisch.\n\n"
            "🛠️ <b>Wie baust du ein Image?</b>\n\n"
            "Du schreibst ein <code>Dockerfile</code>:\n"
            "<code>FROM python:3.11\n"
            "COPY app.py .\n"
            "RUN pip install flask\n"
            "CMD [\"python\", \"app.py\"]</code>\n\n"
            "Das bedeutet:\n"
            "1️⃣ Nimm Python 3.11 als Basis\n"
            "2️⃣ Kopiere meine App rein\n"
            "3️⃣ Installiere Flask\n"
            "4️⃣ Starte die App\n\n"
            "Dann: <code>docker build -t meine-app .</code>\n"
            "Und: <code>docker run meine-app</code>\n\n"
            "💡 <i>Merksatz: Image = Bauplan. Container = das fertige Gebäude das gerade benutzt wird.</i>"
        ),
    },
    {
        "id": "docker_03",
        "thema": "Docker",
        "titel": "Docker in der Praxis 🛠️",
        "inhalt": (
            "🛠️ <b>Docker im Alltag – Was macht man damit wirklich?</b>\n\n"
            "Szenario: Du entwickelst eine Web-App. Sie braucht Python 3.11, PostgreSQL 15 und Redis.\n\n"
            "Ohne Docker: Du installierst alles lokal. Dein Kollege hat Python 3.9. Es kracht.\n\n"
            "Mit Docker Compose:\n"
            "<code>version: '3'\n"
            "services:\n"
            "  web:\n"
            "    build: .\n"
            "    ports:\n"
            "      - \"5000:5000\"\n"
            "  db:\n"
            "    image: postgres:15\n"
            "  cache:\n"
            "    image: redis</code>\n\n"
            "Ein Befehl: <code>docker-compose up</code>\n"
            "→ Alle 3 Services starten. Sofort. Überall gleich.\n\n"
            "🔑 <b>Wichtige Docker-Befehle:</b>\n"
            "• <code>docker ps</code> – laufende Container zeigen\n"
            "• <code>docker stop [name]</code> – Container stoppen\n"
            "• <code>docker logs [name]</code> – Logs anzeigen\n"
            "• <code>docker exec -it [name] bash</code> – in Container reingehen\n\n"
            "💡 <i>Merksatz: Docker Compose = mehrere Container als Team starten mit einem Befehl.</i>"
        ),
    },

    # ══════════════════════════════════════════════
    #  KUBERNETES
    # ══════════════════════════════════════════════
    {
        "id": "k8s_01",
        "thema": "Kubernetes",
        "titel": "Was ist Kubernetes? ☸️",
        "inhalt": (
            "☸️ <b>Kubernetes – Der Chef über die Container</b>\n\n"
            "Du kennst jetzt Docker: eine App in einer Box.\n\n"
            "Aber was, wenn du <b>1000 Boxen</b> brauchst? Wer passt auf die auf?\n"
            "Wer startet eine neue Box wenn eine kaputt geht?\n"
            "Wer verteilt die Last, wenn zu viele Nutzer kommen?\n\n"
            "→ <b>Kubernetes</b> (kurz: K8s)\n\n"
            "K8s ist wie ein <b>Restaurant-Manager</b>:\n"
            "• Er stellt sicher dass immer genug Köche (Container) da sind\n"
            "• Fällt ein Koch aus → neuer Koch wird sofort eingestellt\n"
            "• Kommen mehr Gäste → mehr Köche werden geholt\n"
            "• Ist wenig los → Köche werden nach Hause geschickt (Kosten sparen)\n\n"
            "🔑 <b>Was K8s für dich tut:</b>\n"
            "• <b>Self-healing</b>: kaputte Container werden automatisch neu gestartet\n"
            "• <b>Scaling</b>: bei Last mehr Container, bei Ruhe weniger\n"
            "• <b>Load Balancing</b>: Anfragen werden verteilt\n"
            "• <b>Rolling Updates</b>: neue Version einführen ohne Ausfallzeit\n\n"
            "💡 <i>Merksatz: Docker macht Container. Kubernetes macht aus 1000 Containern ein organisiertes System.</i>"
        ),
    },
    {
        "id": "k8s_02",
        "thema": "Kubernetes",
        "titel": "Pods, Nodes & Cluster ☸️",
        "inhalt": (
            "☸️ <b>Kubernetes-Begriffe – Der Zoo der K8s-Welt</b>\n\n"
            "K8s hat eigene Begriffe. Hier sind die wichtigsten:\n\n"
            "🏙️ <b>Cluster</b> = die ganze Stadt\n"
            "Alles zusammen: alle Server, alle Apps, alles.\n\n"
            "🏢 <b>Node</b> = ein Gebäude in der Stadt\n"
            "Ein echter Server (oder VM) auf dem Container laufen.\n"
            "Ein Cluster hat viele Nodes.\n\n"
            "📦 <b>Pod</b> = eine Wohnung im Gebäude\n"
            "Der kleinste Baustein in K8s. Ein Pod enthält einen (oder selten mehrere) Container.\n"
            "Pods sind vergänglich – K8s erstellt und löscht sie ständig.\n\n"
            "📋 <b>Deployment</b> = der Bauplan für Wohnungen\n"
            "Du sagst: \"Ich will immer 3 Pods von meiner App laufen haben.\"\n"
            "K8s kümmert sich darum – auch wenn einer crasht.\n\n"
            "🌐 <b>Service</b> = die Adresse der Wohnung\n"
            "Pods wechseln ständig die IP. Ein Service gibt dir eine stabile Adresse.\n\n"
            "💡 <i>Merksatz: Cluster → Nodes → Pods → Container. Immer von groß nach klein denken.</i>"
        ),
    },
    {
        "id": "k8s_03",
        "thema": "Kubernetes",
        "titel": "Kubernetes YAML & kubectl 📝",
        "inhalt": (
            "📝 <b>Kubernetes in der Praxis – YAML und kubectl</b>\n\n"
            "In K8s beschreibst du alles in <b>YAML-Dateien</b>.\n"
            "Du sagst K8s WAS du willst – K8s macht WIE:\n\n"
            "<code>apiVersion: apps/v1\n"
            "kind: Deployment\n"
            "metadata:\n"
            "  name: meine-app\n"
            "spec:\n"
            "  replicas: 3\n"
            "  selector:\n"
            "    matchLabels:\n"
            "      app: meine-app\n"
            "  template:\n"
            "    spec:\n"
            "      containers:\n"
            "      - name: app\n"
            "        image: meine-app:1.0</code>\n\n"
            "Das bedeutet: \"Starte 3 Kopien meiner App. Immer.\"\n\n"
            "🛠️ <b>kubectl – das Steuer-Tool:</b>\n"
            "• <code>kubectl get pods</code> – alle Pods anzeigen\n"
            "• <code>kubectl apply -f app.yaml</code> – YAML anwenden\n"
            "• <code>kubectl logs [pod]</code> – Logs lesen\n"
            "• <code>kubectl describe pod [name]</code> – Details\n"
            "• <code>kubectl delete pod [name]</code> – Pod löschen (K8s startet sofort einen neuen!)\n\n"
            "💡 <i>Merksatz: YAML = dein Wunschzettel. kubectl = der Kassierer der ihn entgegennimmt.</i>"
        ),
    },

    # ══════════════════════════════════════════════
    #  CI/CD PIPELINES
    # ══════════════════════════════════════════════
    {
        "id": "cicd_01",
        "thema": "CI/CD",
        "titel": "Was ist CI/CD? 🚀",
        "inhalt": (
            "🚀 <b>CI/CD – Die Autobahn für deinen Code</b>\n\n"
            "Früher: Entwickler schreibt Code → testet manuell → packt es manuell zusammen → deployed manuell.\n"
            "Das dauert Stunden. Fehler passieren. Menschen vergessen Schritte.\n\n"
            "<b>CI/CD automatisiert das alles.</b>\n\n"
            "🔵 <b>CI = Continuous Integration</b>\n"
            "\"Ständige Zusammenführung\"\n\n"
            "Stell dir vor: 5 Entwickler arbeiten am gleichen Code.\n"
            "CI bedeutet: Jedes Mal wenn jemand Code hochlädt (push), wird automatisch:\n"
            "✅ Der Code gebaut\n"
            "✅ Tests ausgeführt\n"
            "✅ Fehler sofort gemeldet\n\n"
            "🟢 <b>CD = Continuous Delivery / Deployment</b>\n"
            "\"Ständige Auslieferung\"\n\n"
            "Nach CI wird der Code automatisch:\n"
            "✅ In eine Testumgebung deployed\n"
            "✅ (Optional) in Production deployed\n\n"
            "💡 <i>Merksatz: CI = \"Ist der Code gut?\" CD = \"Bring den guten Code raus.\"</i>"
        ),
    },
    {
        "id": "cicd_02",
        "thema": "CI/CD",
        "titel": "GitHub Actions – CI/CD in der Praxis ⚙️",
        "inhalt": (
            "⚙️ <b>GitHub Actions – deine Pipeline als Code</b>\n\n"
            "GitHub Actions ist das beliebteste CI/CD-Tool.\n"
            "Du schreibst eine YAML-Datei in deinem Repo und GitHub macht den Rest.\n\n"
            "Beispiel: Automatisch testen wenn jemand Code pusht:\n\n"
            "<code>name: Tests\n"
            "on: [push]\n"
            "jobs:\n"
            "  test:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "    - uses: actions/checkout@v3\n"
            "    - name: Python setup\n"
            "      uses: actions/setup-python@v4\n"
            "    - name: Tests ausführen\n"
            "      run: python -m pytest</code>\n\n"
            "Was passiert:\n"
            "1️⃣ Jemand pusht Code\n"
            "2️⃣ GitHub startet automatisch eine VM\n"
            "3️⃣ Holt den Code\n"
            "4️⃣ Installiert Python\n"
            "5️⃣ Führt Tests aus\n"
            "6️⃣ Meldet: ✅ Bestanden oder ❌ Fehler\n\n"
            "💡 <i>Merksatz: GitHub Actions = dein Roboter-Kollege der nie schläft und sofort testet.</i>"
        ),
    },
    {
        "id": "cicd_03",
        "thema": "CI/CD",
        "titel": "Pipeline Stages – Der Weg zum Deployment 🛤️",
        "inhalt": (
            "🛤️ <b>Pipeline Stages – Jeder Code macht eine Reise</b>\n\n"
            "Eine typische CI/CD Pipeline hat mehrere Stationen:\n\n"
            "1️⃣ <b>Build</b> – Code wird kompiliert/gebaut\n"
            "   → Funktioniert die Syntax überhaupt?\n\n"
            "2️⃣ <b>Test</b> – Automatische Tests\n"
            "   → Unit Tests: Funktioniert jede Funktion einzeln?\n"
            "   → Integration Tests: Funktionieren alle Teile zusammen?\n\n"
            "3️⃣ <b>Security Scan</b> – Sicherheitslücken prüfen\n"
            "   → Hat der Code bekannte Sicherheitsprobleme?\n\n"
            "4️⃣ <b>Build Docker Image</b> – App verpacken\n"
            "   → Container wird gebaut und in Registry hochgeladen\n\n"
            "5️⃣ <b>Deploy Staging</b> – Testumgebung\n"
            "   → App läuft auf einem Test-Server. Tester schauen drauf.\n\n"
            "6️⃣ <b>Deploy Production</b> – Live!\n"
            "   → Echte Nutzer sehen die neue Version\n\n"
            "❌ Schlägt eine Station fehl → Pipeline stoppt. Nichts kommt in Production.\n\n"
            "💡 <i>Merksatz: Pipeline = Qualitätskontrolle am Fließband. Schlechte Ware kommt nicht raus.</i>"
        ),
    },

    # ══════════════════════════════════════════════
    #  TERRAFORM / IaC
    # ══════════════════════════════════════════════
    {
        "id": "terraform_01",
        "thema": "Terraform",
        "titel": "Was ist Infrastructure as Code? 🏗️",
        "inhalt": (
            "🏗️ <b>IaC – Infrastruktur als Kochrezept</b>\n\n"
            "Früher: Ein Admin klickt sich durch AWS/Azure und erstellt manuell:\n"
            "- einen Server\n"
            "- eine Datenbank\n"
            "- ein Netzwerk\n\n"
            "Problem: Wie hat er das gemacht? Keiner weiß es genau.\n"
            "Nächstes Mal: alles nochmal manuell – aber ein bisschen anders.\n\n"
            "<b>Infrastructure as Code (IaC)</b> löst das:\n\n"
            "Du schreibst deine Infrastruktur als <b>Code-Datei</b>.\n"
            "Der Code beschreibt: \"Ich will 3 Server, eine Datenbank, so konfiguriert.\"\n\n"
            "Vorteile:\n"
            "✅ <b>Reproduzierbar</b>: gleiche Infrastruktur jedes Mal\n"
            "✅ <b>Versionierbar</b>: in Git gespeichert → Änderungen nachvollziehbar\n"
            "✅ <b>Automatisierbar</b>: in CI/CD Pipeline eingebaut\n"
            "✅ <b>Dokumentiert</b>: der Code IS die Dokumentation\n\n"
            "Wichtigste Tools: <b>Terraform</b>, Pulumi, AWS CloudFormation\n\n"
            "💡 <i>Merksatz: IaC = deine Infrastruktur ist kein Geheimnis mehr. Sie steht als Code da.</i>"
        ),
    },
    {
        "id": "terraform_02",
        "thema": "Terraform",
        "titel": "Terraform Grundlagen 🟣",
        "inhalt": (
            "🟣 <b>Terraform – Die Universalfernbedienung der Cloud</b>\n\n"
            "Terraform ist das beliebteste IaC-Tool.\n"
            "Das Besondere: Es funktioniert mit <b>allen Cloud-Anbietern</b>.\n"
            "AWS, Azure, Google Cloud, GitHub, DigitalOcean – alles mit dem gleichen Tool.\n\n"
            "Ein Terraform-File sieht so aus:\n\n"
            "<code>provider \"aws\" {\n"
            "  region = \"eu-central-1\"\n"
            "}\n\n"
            "resource \"aws_instance\" \"mein_server\" {\n"
            "  ami           = \"ami-12345\"\n"
            "  instance_type = \"t3.micro\"\n"
            "  tags = {\n"
            "    Name = \"JensServer\"\n"
            "  }\n"
            "}</code>\n\n"
            "Das bedeutet: \"Erstelle mir einen kleinen AWS-Server in Frankfurt.\"\n\n"
            "🛠️ <b>Die 3 Haupt-Befehle:</b>\n"
            "• <code>terraform init</code> – Plugins laden\n"
            "• <code>terraform plan</code> – Was würde passieren? (Vorschau)\n"
            "• <code>terraform apply</code> – Ausführen!\n"
            "• <code>terraform destroy</code> – Alles wieder löschen\n\n"
            "💡 <i>Merksatz: terraform plan = Vorschau. terraform apply = Los. terraform destroy = Weg damit.</i>"
        ),
    },
    {
        "id": "terraform_03",
        "thema": "Terraform",
        "titel": "Terraform State & Module 📂",
        "inhalt": (
            "📂 <b>Terraform State – Das Gedächtnis von Terraform</b>\n\n"
            "Terraform merkt sich was es gebaut hat – in einer Datei namens <code>terraform.tfstate</code>.\n\n"
            "Warum? Stell dir vor, du sagst Terraform:\n"
            "\"Ich will 3 Server.\"\n"
            "Terraform baut 3 Server.\n\n"
            "Jetzt sagst du:\n"
            "\"Ich will 5 Server.\"\n\n"
            "Terraform weiß dank State: \"Ich habe schon 3, ich muss nur 2 neue bauen.\"\n"
            "Ohne State: Terraform würde 5 neue bauen → 8 Server statt 5.\n\n"
            "⚠️ <b>Wichtig:</b> State-Datei im Team → in Remote Backend speichern (S3, Azure Blob)\n"
            "Nie in Git committen – sie enthält Passwörter!\n\n"
            "📦 <b>Module – Wiederverwendbare Bausteine</b>\n\n"
            "Statt alles immer neu zu schreiben:\n"
            "<code>module \"webserver\" {\n"
            "  source = \"./modules/webserver\"\n"
            "  count  = 3\n"
            "  size   = \"small\"\n"
            "}</code>\n\n"
            "Module sind wie Funktionen – einmal schreiben, überall nutzen.\n\n"
            "💡 <i>Merksatz: State = Terraforms Erinnerung. Module = Terraform-Bausteine zum Wiederverwenden.</i>"
        ),
    },

    # ══════════════════════════════════════════════
    #  GIT / GITHUB
    # ══════════════════════════════════════════════
    {
        "id": "git_01",
        "thema": "Git",
        "titel": "Was ist Git? 🌿",
        "inhalt": (
            "🌿 <b>Git – Die Zeitmaschine für deinen Code</b>\n\n"
            "Kennst du das? Du änderst eine Datei, etwas geht kaputt, du willst zurück.\n"
            "Ohne Git: Pech gehabt.\n"
            "Mit Git: Ein Befehl – und du bist an dem Punkt von vor 3 Wochen.\n\n"
            "Git ist ein <b>Versionsverwaltungssystem</b>.\n"
            "Es speichert jeden Stand deines Codes – wie Speicherpunkte in einem Videospiel.\n\n"
            "🔑 <b>Grundbegriffe:</b>\n\n"
            "• <b>Repository (Repo)</b> = der Ordner den Git überwacht\n"
            "• <b>Commit</b> = ein Speicherpunkt (\"Stand von heute 14:00\")\n"
            "• <b>Branch</b> = eine Abzweigung (\"Ich teste etwas Neues, ohne den Hauptcode zu gefährden\")\n"
            "• <b>Merge</b> = zwei Branches zusammenführen\n"
            "• <b>Push/Pull</b> = Code hochladen / herunterladen\n\n"
            "🛠️ <b>Die häufigsten Befehle:</b>\n"
            "<code>git init</code> – Repo starten\n"
            "<code>git add .</code> – Änderungen vormerken\n"
            "<code>git commit -m \"Mein Kommentar\"</code> – Speicherpunkt setzen\n"
            "<code>git push</code> – zu GitHub hochladen\n"
            "<code>git pull</code> – neuesten Stand holen\n\n"
            "💡 <i>Merksatz: Git = Videospiel-Speicherstände für deinen Code.</i>"
        ),
    },
    {
        "id": "git_02",
        "thema": "Git",
        "titel": "Branches & Pull Requests 🌿",
        "inhalt": (
            "🌿 <b>Branches – Parallele Welten für deinen Code</b>\n\n"
            "Stell dir vor du arbeitest an einer App.\n"
            "Du willst ein neues Feature bauen – aber nicht den laufenden Code kaputtmachen.\n\n"
            "→ Du erstellst einen <b>Branch</b>:\n"
            "<code>git checkout -b neues-feature</code>\n\n"
            "Jetzt arbeitest du in einer Parallelwelt.\n"
            "Der Hauptcode (<code>main</code>) bleibt unberührt.\n\n"
            "Wenn dein Feature fertig ist:\n"
            "→ <b>Pull Request (PR)</b> öffnen auf GitHub\n"
            "→ Kollegen schauen drüber (Code Review)\n"
            "→ Alles okay? → <b>Merge</b> in main\n\n"
            "📋 <b>Typischer Workflow im Team:</b>\n"
            "1. <code>git checkout -b feature/login</code>\n"
            "2. Code schreiben & committen\n"
            "3. <code>git push origin feature/login</code>\n"
            "4. Pull Request auf GitHub öffnen\n"
            "5. Review abwarten\n"
            "6. Merge → CI/CD startet automatisch\n\n"
            "💡 <i>Merksatz: Branch = eigene Spielwiese. PR = \"Schaut mal drüber bevor ich's reinschiebe.\"</i>"
        ),
    },

    # ══════════════════════════════════════════════
    #  NETZWERK-GRUNDLAGEN
    # ══════════════════════════════════════════════
    {
        "id": "netz_01",
        "thema": "Netzwerk",
        "titel": "IP-Adressen & Subnetting 🌐",
        "inhalt": (
            "🌐 <b>IP-Adressen – Hausnummern im Internet</b>\n\n"
            "Jedes Gerät im Netzwerk hat eine <b>IP-Adresse</b>.\n"
            "Wie eine Hausnummer – damit Pakete wissen wohin sie sollen.\n\n"
            "Beispiel: <code>192.168.178.47</code>\n"
            "Das ist dein RasPi – nur erreichbar in deinem Heimnetz.\n\n"
            "📦 <b>IPv4 vs IPv6:</b>\n"
            "• IPv4: <code>192.168.1.1</code> – 4 Zahlen, 0-255\n"
            "• IPv6: <code>2001:0db8::1</code> – viel länger, viel mehr Adressen\n\n"
            "🏘️ <b>Subnetting – Netzwerke aufteilen:</b>\n\n"
            "Ein Subnetz ist wie ein Wohnblock.\n"
            "<code>192.168.178.0/24</code> bedeutet:\n"
            "• Die ersten 24 Bits sind die Straße (192.168.178)\n"
            "• Die letzten 8 Bits sind die Hausnummern (.1 bis .254)\n"
            "• = 254 mögliche Geräte in diesem Netz\n\n"
            "Typische Subnetzmasken:\n"
            "• /24 = 254 Hosts (kleines Büro)\n"
            "• /16 = 65.534 Hosts (großes Unternehmen)\n"
            "• /32 = 1 Host (einzelner Server)\n\n"
            "💡 <i>Merksatz: IP = Hausnummer. Subnetz = welcher Wohnblock. /24 = 254 Wohnungen.</i>"
        ),
    },
    {
        "id": "netz_02",
        "thema": "Netzwerk",
        "titel": "DNS – Das Telefonbuch des Internets 📖",
        "inhalt": (
            "📖 <b>DNS – Warum du google.com tippen kannst statt 142.250.185.46</b>\n\n"
            "Stell dir vor: Jedes Mal wenn du jemanden anrufen willst, musst du die Telefonnummer wissen.\n"
            "Kein Mensch merkt sich tausende Nummern – darum gibt es Telefonbücher.\n\n"
            "Im Internet ist <b>DNS (Domain Name System)</b> das Telefonbuch:\n"
            "Du tippst <code>google.com</code>\n"
            "DNS übersetzt das zu <code>142.250.185.46</code>\n"
            "Dein Browser verbindet sich zur IP.\n\n"
            "🔄 <b>Was passiert wirklich beim Aufruf einer Website?</b>\n\n"
            "1️⃣ Du tippst <code>claude.ai</code>\n"
            "2️⃣ Dein PC fragt den DNS-Server: \"Was ist die IP von claude.ai?\"\n"
            "3️⃣ DNS antwortet: \"104.22.x.x\"\n"
            "4️⃣ Dein Browser verbindet sich zur IP\n"
            "5️⃣ Website erscheint\n\n"
            "🔑 <b>Wichtige DNS-Begriffe:</b>\n"
            "• <b>A-Record</b>: Domain → IPv4\n"
            "• <b>AAAA-Record</b>: Domain → IPv6\n"
            "• <b>CNAME</b>: Alias (www.jens.de → jens.de)\n"
            "• <b>MX-Record</b>: E-Mail-Server\n"
            "• <b>TTL</b>: Wie lange der Eintrag gecacht wird\n\n"
            "💡 <i>Merksatz: DNS = Telefonbuch. A-Record = die Telefonnummer.</i>"
        ),
    },
    {
        "id": "netz_03",
        "thema": "Netzwerk",
        "titel": "TCP/IP, HTTP & Ports 🔌",
        "inhalt": (
            "🔌 <b>Ports – Türen in deinem Server</b>\n\n"
            "Dein Server hat eine IP-Adresse – aber viele Services laufen drauf.\n"
            "Wie weiß ein Paket ob es zur Website oder zur Datenbank soll?\n\n"
            "→ <b>Ports!</b> Jeder Service lauscht auf einem anderen Port.\n\n"
            "Wichtige Standard-Ports:\n"
            "• <b>80</b> = HTTP (Websites unverschlüsselt)\n"
            "• <b>443</b> = HTTPS (Websites verschlüsselt) ✅\n"
            "• <b>22</b> = SSH (Remotezugriff auf Server)\n"
            "• <b>3389</b> = RDP (Windows Remote Desktop)\n"
            "• <b>5432</b> = PostgreSQL\n"
            "• <b>3306</b> = MySQL\n"
            "• <b>6379</b> = Redis\n\n"
            "🌐 <b>HTTP vs HTTPS:</b>\n"
            "HTTP: Daten werden im Klartext übertragen. Jeder kann mitlesen.\n"
            "HTTPS: Daten werden verschlüsselt (TLS). Sicher.\n\n"
            "🔄 <b>TCP vs UDP:</b>\n"
            "• TCP: sicher, mit Bestätigung (\"Hast du's?\" – \"Ja, hab's!\")\n"
            "  → Websites, E-Mail, SSH\n"
            "• UDP: schnell, ohne Bestätigung (\"Ich schick's einfach.\")\n"
            "  → Videocalls, Online-Gaming, DNS\n\n"
            "💡 <i>Merksatz: Port = Tür. 443 = Haustür (HTTPS). 22 = Hintereingang (SSH).</i>"
        ),
    },

    # ══════════════════════════════════════════════
    #  LINUX / SHELL
    # ══════════════════════════════════════════════
    {
        "id": "linux_01",
        "thema": "Linux",
        "titel": "Linux Grundbefehle 🐧",
        "inhalt": (
            "🐧 <b>Linux im Alltag – Die wichtigsten Befehle</b>\n\n"
            "Du arbeitest täglich auf dem RasPi – also kennst du einige bereits.\n"
            "Hier die wichtigsten nochmal gesammelt:\n\n"
            "📁 <b>Navigation:</b>\n"
            "<code>pwd</code> – Wo bin ich gerade?\n"
            "<code>ls -la</code> – Was ist hier?\n"
            "<code>cd /home/jens</code> – Woanders hingehen\n"
            "<code>cd ..</code> – Einen Ordner zurück\n\n"
            "📄 <b>Dateien:</b>\n"
            "<code>cat datei.txt</code> – Inhalt anzeigen\n"
            "<code>nano datei.txt</code> – Bearbeiten\n"
            "<code>cp quelle ziel</code> – Kopieren\n"
            "<code>mv alt neu</code> – Verschieben/Umbenennen\n"
            "<code>rm datei.txt</code> – Löschen\n"
            "<code>chmod +x script.sh</code> – Ausführbar machen\n\n"
            "🔍 <b>Suchen & Finden:</b>\n"
            "<code>grep 'suchbegriff' datei</code> – In Datei suchen\n"
            "<code>grep -r 'suchbegriff' /ordner</code> – In Ordner suchen\n"
            "<code>find / -name 'datei.txt'</code> – Datei finden\n\n"
            "⚙️ <b>System:</b>\n"
            "<code>top</code> oder <code>htop</code> – CPU/RAM Auslastung\n"
            "<code>df -h</code> – Festplattenplatz\n"
            "<code>sudo systemctl restart service</code> – Service neustarten\n\n"
            "💡 <i>Merksatz: grep = Suchmaschine für Dateien. find = Suchmaschine für Dateipfade.</i>"
        ),
    },
    {
        "id": "linux_02",
        "thema": "Linux",
        "titel": "systemd & Services 🔧",
        "inhalt": (
            "🔧 <b>systemd – Der Chef der Linux-Services</b>\n\n"
            "Du kennst das bereits vom RasPi: deine Bots laufen als systemd-Services.\n"
            "Lass uns genau verstehen was systemd macht.\n\n"
            "<b>systemd</b> ist das erste Programm das startet wenn Linux bootet.\n"
            "Es startet und überwacht alle anderen Programme.\n\n"
            "🛠️ <b>Die wichtigsten systemctl-Befehle:</b>\n"
            "<code>sudo systemctl start service</code> – starten\n"
            "<code>sudo systemctl stop service</code> – stoppen\n"
            "<code>sudo systemctl restart service</code> – neustarten\n"
            "<code>sudo systemctl status service</code> – Status prüfen\n"
            "<code>sudo systemctl enable service</code> – automatisch beim Boot starten\n"
            "<code>sudo systemctl disable service</code> – nicht mehr automatisch starten\n\n"
            "📋 <b>Eine Service-Datei schreiben:</b>\n"
            "<code>[Unit]\n"
            "Description=Mein Bot\n"
            "After=network.target\n\n"
            "[Service]\n"
            "User=jens\n"
            "WorkingDirectory=/home/jens/JobAgent\n"
            "ExecStart=/usr/bin/python3 bot.py\n"
            "Restart=always\n\n"
            "[Install]\n"
            "WantedBy=multi-user.target</code>\n\n"
            "Speichern unter: <code>/etc/systemd/system/meinbot.service</code>\n"
            "Dann: <code>sudo systemctl daemon-reload && sudo systemctl enable meinbot</code>\n\n"
            "💡 <i>Merksatz: systemd = Babysitter für Services. Restart=always = \"Wenn er stirbt, starte ihn neu.\"</i>"
        ),
    },

    # ══════════════════════════════════════════════
    #  CLOUD / AZURE
    # ══════════════════════════════════════════════
    {
        "id": "cloud_01",
        "thema": "Cloud",
        "titel": "Cloud-Modelle: IaaS, PaaS, SaaS ☁️",
        "inhalt": (
            "☁️ <b>IaaS, PaaS, SaaS – Pizza als Erklärung</b>\n\n"
            "Das beste Erklärungs-Modell der IT-Welt: Pizza!\n\n"
            "🏠 <b>Selbst gemacht (On-Premise):</b>\n"
            "Du kaufst Mehl, Tomaten, Käse.\n"
            "Du backst die Pizza selbst.\n"
            "Du kümmerst dich um alles.\n"
            "→ Server, Netzwerk, OS, Software – alles deine Verantwortung.\n\n"
            "🏗️ <b>IaaS (Infrastructure as a Service):</b>\n"
            "Du bekommst Backofen, Teig und Soße geliefert.\n"
            "Den Belag machst du selbst.\n"
            "→ Azure VM: Microsoft gibt dir den Server. OS und Software: du.\n\n"
            "🛠️ <b>PaaS (Platform as a Service):</b>\n"
            "Du bekommst eine fertige Pizza – du fügst nur noch den Belag drauf.\n"
            "→ Azure App Service: Microsoft kümmert sich um OS und Runtime. Du deployst nur deinen Code.\n\n"
            "📱 <b>SaaS (Software as a Service):</b>\n"
            "Du bestellst eine fertige Pizza und isst sie.\n"
            "→ Microsoft 365, Gmail: Du nutzt es. Fertig.\n\n"
            "💡 <i>Merksatz: IaaS = mehr Kontrolle, mehr Arbeit. SaaS = wenig Kontrolle, null Arbeit.</i>"
        ),
    },
    {
        "id": "cloud_02",
        "thema": "Cloud",
        "titel": "Azure Grundlagen ☁️",
        "inhalt": (
            "☁️ <b>Azure – Microsofts Cloud</b>\n\n"
            "Azure ist Microsofts Cloud-Plattform – und für dich als M365/Intune-Spezialist besonders relevant.\n\n"
            "🗺️ <b>Azure-Struktur (von oben nach unten):</b>\n\n"
            "🏢 <b>Tenant</b> = deine Firma\n"
            "Alles in Azure gehört zu einem Tenant. Deine Microsoft-365-Umgebung = ein Tenant.\n\n"
            "📁 <b>Subscription</b> = Abrechnungseinheit\n"
            "Eine Subscription = ein Konto bei Azure mit eigener Abrechnung.\n\n"
            "📂 <b>Resource Group</b> = Ordner\n"
            "Alle zusammengehörigen Ressourcen in einem Ordner.\n"
            "z.B. alle Server + Datenbanken + Netzwerke für ein Projekt.\n\n"
            "⚙️ <b>Resources</b> = einzelne Dienste\n"
            "VMs, Datenbanken, Storage Accounts, etc.\n\n"
            "🔑 <b>Wichtige Azure-Dienste:</b>\n"
            "• <b>Azure AD / Entra ID</b>: Benutzer & Gruppen (du kennst das!)\n"
            "• <b>Intune</b>: Geräteverwaltung (du kennst das!)\n"
            "• <b>Azure VM</b>: virtuelle Server\n"
            "• <b>Azure Storage</b>: Dateispeicher\n"
            "• <b>Azure Functions</b>: Code ohne Server ausführen\n\n"
            "💡 <i>Merksatz: Tenant → Subscription → Resource Group → Resource. Wie Firma → Abteilung → Projekt → Tool.</i>"
        ),
    },
    # ══════════════════════════════════════════════
    #  TERRAGRUNT
    # ══════════════════════════════════════════════
    {
        "id": "terragrunt_01",
        "thema": "Terragrunt",
        "titel": "Was ist Terragrunt? 🌿",
        "inhalt": (
            "🌿 <b>Terragrunt – Terraform aber besser organisiert</b>\n\n"
            "Du kennst Terraform: Infrastruktur als Code.\n"
            "Aber stell dir vor, du hast 10 Umgebungen: dev, staging, prod, und 5 Regionen.\n\n"
            "Ohne Terragrunt: Du kopierst deinen Terraform-Code 10 Mal. Änderst du was, musst du es 10 Mal ändern. 😱\n\n"
            "Mit <b>Terragrunt</b>: Du schreibst den Code einmal.\n"
            "Terragrunt kümmert sich darum, dass er für jede Umgebung mit den richtigen Variablen läuft.\n\n"
            "🔑 <b>Was Terragrunt macht:</b>\n"
            "• <b>DRY</b> (Don't Repeat Yourself): Ein Terraform-Modul, viele Umgebungen\n"
            "• <b>Remote State</b> automatisch konfigurieren\n"
            "• <b>Abhängigkeiten</b> zwischen Modulen verwalten\n"
            "• <b>Hooks</b>: Code vor/nach terraform ausführen\n\n"
            "📁 <b>Typische Ordnerstruktur:</b>\n"
            "<code>infra/\n"
            "  dev/\n"
            "    terragrunt.hcl\n"
            "  prod/\n"
            "    terragrunt.hcl\n"
            "  modules/\n"
            "    vpc/\n"
            "    ec2/</code>\n\n"
            "💡 <i>Merksatz: Terraform = Bauplan. Terragrunt = der Architekt der viele Baupläne koordiniert.</i>"
        ),
    },
    {
        "id": "terragrunt_02",
        "thema": "Terragrunt",
        "titel": "Terragrunt in der Praxis 🛠️",
        "inhalt": (
            "🛠️ <b>Terragrunt – So sieht es aus</b>\n\n"
            "Eine <code>terragrunt.hcl</code> Datei sieht so aus:\n\n"
            "<code>terraform {\n"
            "  source = '../modules/vpc'\n"
            "}\n\n"
            "inputs = {\n"
            "  env    = 'dev'\n"
            "  region = 'eu-central-1'\n"
            "  cidr   = '10.0.0.0/16'\n"
            "}</code>\n\n"
            "Und für prod einfach:\n"
            "<code>inputs = {\n"
            "  env    = 'prod'\n"
            "  cidr   = '10.1.0.0/16'\n"
            "}</code>\n\n"
            "🔄 <b>Wichtige Befehle:</b>\n"
            "<code>terragrunt init</code> – initialisieren\n"
            "<code>terragrunt plan</code> – was wird sich ändern?\n"
            "<code>terragrunt apply</code> – Änderungen ausführen\n"
            "<code>terragrunt run-all apply</code> – ALLE Module auf einmal\n\n"
            "🏢 <b>Warum Transfermarkt Terragrunt nutzt:</b>\n"
            "Große Plattform = viele Services = viele Umgebungen.\n"
            "Terragrunt hält das alles wartbar ohne Code-Duplizierung.\n\n"
            "💡 <i>Merksatz: terragrunt run-all = alle Umgebungen auf einmal deployen.</i>"
        ),
    },

    # ══════════════════════════════════════════════
    #  HASHICORP NOMAD
    # ══════════════════════════════════════════════
    {
        "id": "nomad_01",
        "thema": "HashiCorp Nomad",
        "titel": "Was ist Nomad? 🏕️",
        "inhalt": (
            "🏕️ <b>HashiCorp Nomad – Kubernetes light</b>\n\n"
            "Du kennst Kubernetes: Container orchestrieren.\n"
            "Nomad macht das gleiche – aber simpler und flexibler.\n\n"
            "📊 <b>Nomad vs. Kubernetes:</b>\n"
            "• K8s: mächtig, komplex, viel Overhead\n"
            "• Nomad: einfach, schnell, auch für Nicht-Container\n\n"
            "🎯 <b>Was Nomad besonders macht:</b>\n"
            "Nomad kann nicht nur Docker-Container orchestrieren, sondern auch:\n"
            "• Normale Programme (Java, Python, Go)\n"
            "• VM-Images\n"
            "• Batch-Jobs\n"
            "• Systemdienste\n\n"
            "🏗️ <b>Nomad-Begriffe:</b>\n"
            "• <b>Job</b> = was soll laufen? (wie K8s Deployment)\n"
            "• <b>Task Group</b> = Gruppe zusammengehöriger Tasks\n"
            "• <b>Task</b> = ein einzelner Prozess (Container, Skript, etc.)\n"
            "• <b>Allocation</b> = konkrete Zuweisung auf einem Node\n"
            "• <b>Client</b> = Server der Jobs ausführt (wie K8s Node)\n"
            "• <b>Server</b> = koordiniert alles (wie K8s Control Plane)\n\n"
            "💡 <i>Merksatz: Nomad = leichtgewichtiges Kubernetes das auch Nicht-Container kann.</i>"
        ),
    },
    {
        "id": "nomad_02",
        "thema": "HashiCorp Nomad",
        "titel": "Nomad Jobs & HCL 📝",
        "inhalt": (
            "📝 <b>Nomad Jobs in HCL-Syntax</b>\n\n"
            "Nomad-Jobs werden in <b>HCL</b> (HashiCorp Configuration Language) geschrieben – "
            "dieselbe Sprache wie Terraform.\n\n"
            "<code>job 'meine-app' {\n"
            "  datacenters = ['dc1']\n"
            "  type = 'service'\n\n"
            "  group 'web' {\n"
            "    count = 3\n\n"
            "    task 'server' {\n"
            "      driver = 'docker'\n\n"
            "      config {\n"
            "        image = 'nginx:latest'\n"
            "        ports = ['http']\n"
            "      }\n\n"
            "      resources {\n"
            "        cpu    = 200\n"
            "        memory = 256\n"
            "      }\n"
            "    }\n"
            "  }\n"
            "}</code>\n\n"
            "🔄 <b>Wichtige Befehle:</b>\n"
            "<code>nomad job run job.hcl</code> – Job starten\n"
            "<code>nomad job status meine-app</code> – Status prüfen\n"
            "<code>nomad job stop meine-app</code> – Job stoppen\n"
            "<code>nomad alloc logs [id]</code> – Logs ansehen\n\n"
            "💡 <i>Merksatz: count = 3 bedeutet Nomad startet automatisch 3 Instanzen und hält sie am Leben.</i>"
        ),
    },

    # ══════════════════════════════════════════════
    #  HASHICORP CONSUL
    # ══════════════════════════════════════════════
    {
        "id": "consul_01",
        "thema": "HashiCorp Consul",
        "titel": "Was ist Consul? 🔍",
        "inhalt": (
            "🔍 <b>HashiCorp Consul – Das Telefonbuch der Services</b>\n\n"
            "Stell dir vor, deine App hat 50 Microservices.\n"
            "Service A muss Service B finden. Aber B läuft auf wechselnden IPs.\n\n"
            "Wie findet A den B? → <b>Consul!</b>\n\n"
            "Consul ist ein <b>Service Discovery</b> Tool.\n"
            "Jeder Service meldet sich bei Consul an: 'Hallo, ich bin B, ich laufe auf 10.0.0.5:8080'\n"
            "Service A fragt Consul: 'Wo ist B?' → Consul antwortet mit der aktuellen Adresse.\n\n"
            "🔑 <b>Was Consul alles kann:</b>\n"
            "• <b>Service Discovery</b>: Services finden sich gegenseitig\n"
            "• <b>Health Checks</b>: Consul prüft ob Services noch leben\n"
            "• <b>Key-Value Store</b>: Konfiguration zentral speichern\n"
            "• <b>Service Mesh</b>: verschlüsselte Kommunikation zwischen Services\n\n"
            "🏗️ <b>Wie es zusammenpasst:</b>\n"
            "Nomad + Consul = Dream Team:\n"
            "Nomad startet Container → Consul registriert sie automatisch\n"
            "→ Services finden sich ohne hardcodierte IPs\n\n"
            "💡 <i>Merksatz: Consul = DNS für Microservices. Kein hardcodiertes IP, immer die richtige Adresse.</i>"
        ),
    },
    {
        "id": "consul_02",
        "thema": "HashiCorp Consul",
        "titel": "Consul Health Checks & KV 🏥",
        "inhalt": (
            "🏥 <b>Consul – Health Checks und Key-Value Store</b>\n\n"
            "📋 <b>Health Checks:</b>\n"
            "Consul pingt deine Services regelmäßig an.\n"
            "Antwortet ein Service nicht → Consul markiert ihn als unhealthy.\n"
            "→ Kein Traffic mehr zu diesem Service. Automatisch.\n\n"
            "Beispiel Health Check:\n"
            "<code>{\n"
            "  'check': {\n"
            "    'http': 'http://localhost:8080/health',\n"
            "    'interval': '10s',\n"
            "    'timeout': '2s'\n"
            "  }\n"
            "}</code>\n\n"
            "🗂️ <b>Key-Value Store:</b>\n"
            "Consul kann auch Konfiguration speichern:\n"
            "<code>consul kv put config/db-host 10.0.0.5\n"
            "consul kv get config/db-host</code>\n\n"
            "Deine App liest die Konfig aus Consul → keine hardcodierten Werte mehr.\n\n"
            "🔄 <b>Wichtige Befehle:</b>\n"
            "<code>consul members</code> – alle Nodes im Cluster\n"
            "<code>consul catalog services</code> – alle registrierten Services\n"
            "<code>consul health service [name]</code> – Health-Status eines Service\n\n"
            "💡 <i>Merksatz: Consul KV = zentrales Konfigurationslager. Alle Services lesen von dort.</i>"
        ),
    },

    # ══════════════════════════════════════════════
    #  HASHICORP VAULT
    # ══════════════════════════════════════════════
    {
        "id": "vault_01",
        "thema": "HashiCorp Vault",
        "titel": "Was ist Vault? 🔐",
        "inhalt": (
            "🔐 <b>HashiCorp Vault – Der Tresor für Secrets</b>\n\n"
            "Jede App hat Geheimnisse: Passwörter, API-Keys, Zertifikate.\n\n"
            "❌ <b>Das falsche Vorgehen (passiert ständig):</b>\n"
            "• Passwörter hardcoded im Code\n"
            "• API-Keys in .env Dateien auf dem Server\n"
            "• DB-Passwort in der config.yaml – im Git-Repo 😱\n\n"
            "✅ <b>Das richtige Vorgehen mit Vault:</b>\n"
            "Alle Secrets leben in Vault – einem verschlüsselten Tresor.\n"
            "Apps holen sich ihre Secrets zur Laufzeit aus Vault.\n"
            "Niemand sieht Klartext-Passwörter im Code oder auf Servern.\n\n"
            "🔑 <b>Was Vault kann:</b>\n"
            "• <b>Static Secrets</b>: Passwörter sicher speichern\n"
            "• <b>Dynamic Secrets</b>: temporäre DB-Passwörter generieren (nach 1h ungültig!)\n"
            "• <b>Encryption as a Service</b>: Daten ver-/entschlüsseln ohne Key-Management\n"
            "• <b>PKI</b>: Zertifikate automatisch ausstellen\n\n"
            "💡 <i>Merksatz: Vault = niemand kennt die Passwörter. Nur Vault kennt sie, und gibt sie nur wem sie gehören.</i>"
        ),
    },
    {
        "id": "vault_02",
        "thema": "HashiCorp Vault",
        "titel": "Vault in der Praxis 🛠️",
        "inhalt": (
            "🛠️ <b>Vault – So funktioniert es in der Praxis</b>\n\n"
            "🔓 <b>Vault starten und entsperren:</b>\n"
            "Vault startet 'sealed' (versiegelt) – niemand kann rein.\n"
            "Du entsperrst ihn mit Unseal Keys:\n"
            "<code>vault operator unseal [key1]\n"
            "vault operator unseal [key2]\n"
            "vault operator unseal [key3]</code>\n\n"
            "📥 <b>Secrets speichern und lesen:</b>\n"
            "<code># Secret speichern\n"
            "vault kv put secret/myapp db_password=\'geheim123\'\n\n"
            "# Secret lesen\n"
            "vault kv get secret/myapp</code>\n\n"
            "🤖 <b>Dynamic Secrets (das Coolste!):</b>\n"
            "Vault kann temporäre DB-Credentials generieren:\n"
            "<code>vault read database/creds/my-role</code>\n"
            "→ Vault erstellt einen DB-User mit zufälligem Passwort.\n"
            "→ Nach 1 Stunde wird der User automatisch gelöscht.\n"
            "→ Kein dauerhaftes Passwort = kein Sicherheitsrisiko!\n\n"
            "🔗 <b>Vault + Nomad + Consul = HashiCorp Stack</b>\n"
            "Diese drei arbeiten perfekt zusammen – genau wie bei Transfermarkt.\n\n"
            "💡 <i>Merksatz: Dynamic Secrets = Passwörter die sich selbst zerstören. Wie Mission Impossible.</i>"
        ),
    },

    # ══════════════════════════════════════════════
    #  PROMETHEUS & GRAFANA
    # ══════════════════════════════════════════════
    {
        "id": "monitoring_01",
        "thema": "Prometheus & Grafana",
        "titel": "Was ist Prometheus? 📊",
        "inhalt": (
            "📊 <b>Prometheus – Der Datenschreiber</b>\n\n"
            "Stell dir vor, du willst wissen:\n"
            "• Wie viel CPU nutzt mein Server gerade?\n"
            "• Wie viele Requests kommen pro Sekunde rein?\n"
            "• Wann war der letzte Ausfall?\n\n"
            "→ <b>Prometheus</b> sammelt diese Zahlen (Metriken) und speichert sie.\n\n"
            "🔄 <b>Wie Prometheus arbeitet:</b>\n"
            "Prometheus 'scrapt' (fragt ab) deine Services regelmäßig:\n"
            "'Hey Server, wie geht's dir?' → Server antwortet mit Zahlen\n"
            "Prometheus speichert: 'Um 14:32 war CPU bei 78%'\n\n"
            "📈 <b>Wichtige Konzepte:</b>\n"
            "• <b>Metrics</b>: Zahlen über Zeit (CPU, RAM, Requests, Errors)\n"
            "• <b>Exporter</b>: kleine Programme die Metriken bereitstellen\n"
            "• <b>Scrape Interval</b>: wie oft Prometheus abfragt (z.B. alle 15s)\n"
            "• <b>PromQL</b>: Abfragesprache für die gespeicherten Daten\n\n"
            "🔍 <b>Beispiel PromQL:</b>\n"
            "<code>rate(http_requests_total[5m])</code>\n"
            "→ Requests pro Sekunde der letzten 5 Minuten\n\n"
            "💡 <i>Merksatz: Prometheus = Tagebuch deiner Infrastruktur. Jede Zahl mit Timestamp gespeichert.</i>"
        ),
    },
    {
        "id": "monitoring_02",
        "thema": "Prometheus & Grafana",
        "titel": "Grafana & Loki – Sehen & Lesen 📈",
        "inhalt": (
            "📈 <b>Grafana – Das Dashboard für Prometheus</b>\n\n"
            "Prometheus sammelt Zahlen. Aber Zahlen sind langweilig.\n"
            "<b>Grafana</b> macht daraus schöne Graphen und Dashboards.\n\n"
            "📊 <b>Grafana kann:</b>\n"
            "• Graphen, Gauges, Heatmaps, Tabellen\n"
            "• Alerts: 'CPU über 90% für 5 Min → Telegram-Nachricht!'\n"
            "• Viele Datenquellen: Prometheus, MySQL, Loki, InfluxDB...\n"
            "• Fertige Dashboards importieren (community.grafana.com)\n\n"
            "📝 <b>Loki – Logs wie Prometheus</b>\n"
            "Prometheus = Metriken (Zahlen)\n"
            "Loki = Logs (Texte)\n\n"
            "Loki sammelt Log-Zeilen von deinen Services und macht sie durchsuchbar.\n"
            "In Grafana kannst du dann Logs und Metriken <i>zusammen</i> anschauen.\n\n"
            "🔍 <b>LogQL Beispiel (Loki):</b>\n"
            "<code>{app='meine-app'} |= 'ERROR'</code>\n"
            "→ Alle Logs von meine-app die ERROR enthalten\n\n"
            "🏗️ <b>Der Stack bei Transfermarkt:</b>\n"
            "Prometheus (Metriken) + Loki (Logs) + Grafana (Visualisierung)\n"
            "= vollständiges Observability-Setup\n\n"
            "💡 <i>Merksatz: Prometheus misst. Loki liest. Grafana zeigt. Zusammen siehst du alles.</i>"
        ),
    },

    # ══════════════════════════════════════════════
    #  GITHUB ACTIONS
    # ══════════════════════════════════════════════
    {
        "id": "ghactions_01",
        "thema": "GitHub Actions",
        "titel": "Was sind GitHub Actions? ⚙️",
        "inhalt": (
            "⚙️ <b>GitHub Actions – Automatisierung direkt in GitHub</b>\n\n"
            "Stell dir vor: Du pushst Code → automatisch wird getestet, gebaut, deployed.\n"
            "Das ist <b>CI/CD mit GitHub Actions</b>.\n\n"
            "🔄 <b>Wie es funktioniert:</b>\n"
            "Du schreibst eine YAML-Datei in <code>.github/workflows/</code>\n"
            "GitHub führt sie automatisch aus bei bestimmten Events.\n\n"
            "📋 <b>Beispiel Workflow:</b>\n"
            "<code>name: CI Pipeline\n\n"
            "on:\n"
            "  push:\n"
            "    branches: [main]\n\n"
            "jobs:\n"
            "  test:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v3\n"
            "      - name: Tests ausführen\n"
            "        run: python -m pytest\n"
            "      - name: Docker bauen\n"
            "        run: docker build -t meine-app .</code>\n\n"
            "🎯 <b>Wichtige Begriffe:</b>\n"
            "• <b>Workflow</b>: die ganze YAML-Datei\n"
            "• <b>Job</b>: ein Abschnitt (läuft auf einem Runner)\n"
            "• <b>Step</b>: ein einzelner Schritt im Job\n"
            "• <b>Runner</b>: der Server der den Job ausführt\n"
            "• <b>Action</b>: fertiger Baustein (z.B. actions/checkout)\n\n"
            "💡 <i>Merksatz: Push → GitHub Actions wacht auf → führt deinen Workflow aus. Vollautomatisch.</i>"
        ),
    },
    {
        "id": "ghactions_02",
        "thema": "GitHub Actions",
        "titel": "GitHub Actions – Deploy & Secrets 🚀",
        "inhalt": (
            "🚀 <b>GitHub Actions – Deployment und Secrets</b>\n\n"
            "📦 <b>Typischer CI/CD Workflow:</b>\n"
            "1️⃣ Code pushen → Tests laufen\n"
            "2️⃣ Tests grün → Docker Image bauen\n"
            "3️⃣ Image pushen → zu Registry (z.B. Docker Hub, GHCR)\n"
            "4️⃣ Deploy → Server pullt neues Image und startet es\n\n"
            "<code>- name: Docker Push\n"
            "  run: |\n"
            "    docker tag meine-app ghcr.io/user/meine-app:latest\n"
            "    docker push ghcr.io/user/meine-app:latest\n\n"
            "- name: Deploy via SSH\n"
            "  run: |\n"
            "    ssh user@server \'docker pull && docker restart app\'</code>\n\n"
            "🔐 <b>Secrets in GitHub Actions:</b>\n"
            "Passwörter NICHT in die YAML schreiben!\n"
            "Stattdessen: GitHub Secrets (Settings → Secrets)\n"
            "<code>env:\n"
            "  DB_PASS: ${{ secrets.DB_PASSWORD }}</code>\n\n"
            "🌿 <b>Verbindung zu Terragrunt:</b>\n"
            "GitHub Actions kann auch Terragrunt aufrufen:\n"
            "<code>- name: Terragrunt Apply\n"
            "  run: terragrunt run-all apply --auto-approve</code>\n\n"
            "💡 <i>Merksatz: GitHub Actions + Vault + Terragrunt = vollautomatisches, sicheres Deployment.</i>"
        ),
    },

    # ══════════════════════════════════════════════
    #  AMQP & REST APIs
    # ══════════════════════════════════════════════
    {
        "id": "messaging_01",
        "thema": "AMQP & REST-APIs",
        "titel": "REST APIs verstehen 🌐",
        "inhalt": (
            "🌐 <b>REST APIs – Wie Services miteinander reden</b>\n\n"
            "Services in einer Microservice-Architektur müssen kommunizieren.\n"
            "Die häufigste Methode: <b>REST API</b>\n\n"
            "📬 <b>REST = Anfrage → Antwort</b>\n"
            "Service A schickt eine HTTP-Anfrage an Service B.\n"
            "B antwortet. Fertig.\n\n"
            "🔑 <b>HTTP-Methoden:</b>\n"
            "• <b>GET</b>: Daten holen (<code>GET /users/42</code>)\n"
            "• <b>POST</b>: Neue Daten erstellen (<code>POST /users</code>)\n"
            "• <b>PUT/PATCH</b>: Daten aktualisieren\n"
            "• <b>DELETE</b>: Daten löschen\n\n"
            "📊 <b>HTTP Status Codes:</b>\n"
            "• <b>200</b> = OK\n"
            "• <b>201</b> = Created\n"
            "• <b>400</b> = Bad Request (dein Fehler)\n"
            "• <b>401</b> = Unauthorized\n"
            "• <b>404</b> = Not Found\n"
            "• <b>500</b> = Internal Server Error (Serverfehler)\n\n"
            "📋 <b>JSON – die Sprache der APIs:</b>\n"
            "<code>{\n"
            "  \"user_id\": 42,\n"
            "  \"name\": \"Jens\",\n"
            "  \"role\": \"admin\"\n"
            "}</code>\n\n"
            "💡 <i>Merksatz: REST = Briefpost. Du schickst eine Anfrage, wartest auf Antwort. Synchron.</i>"
        ),
    },
    {
        "id": "messaging_02",
        "thema": "AMQP & REST-APIs",
        "titel": "AMQP & Message Queues 📨",
        "inhalt": (
            "📨 <b>AMQP – Wenn REST nicht reicht</b>\n\n"
            "REST ist synchron: Anfrage → warte → Antwort.\n"
            "Aber was, wenn Service B gerade nicht erreichbar ist?\n"
            "→ Anfrage geht verloren. 😱\n\n"
            "Lösung: <b>Message Queue mit AMQP</b>\n"
            "(AMQP = Advanced Message Queuing Protocol)\n\n"
            "📬 <b>Wie eine Queue funktioniert:</b>\n"
            "Service A schickt eine Nachricht in eine Queue (wie einen Briefkasten).\n"
            "Service B holt die Nachricht ab – wenn er bereit ist.\n"
            "A wartet nicht. B kann pausieren. Nichts geht verloren.\n\n"
            "🐰 <b>RabbitMQ – die bekannteste AMQP-Implementierung:</b>\n"
            "• <b>Producer</b>: schickt Nachrichten (Service A)\n"
            "• <b>Queue</b>: der Briefkasten\n"
            "• <b>Consumer</b>: liest Nachrichten (Service B)\n"
            "• <b>Exchange</b>: verteilt Nachrichten an die richtigen Queues\n\n"
            "🎯 <b>Wann AMQP statt REST?</b>\n"
            "• Aufgaben die Zeit brauchen (Videos konvertieren, Mails senden)\n"
            "• Services die manchmal offline sind\n"
            "• Viele Empfänger für eine Nachricht\n"
            "• Lastspitzen abfedern\n\n"
            "💡 <i>Merksatz: REST = Telefon (synchron). AMQP = Briefkasten (asynchron). Beides hat seinen Platz.</i>"
        ),
    },

    # ══════════════════════════════════════════════
    #  MYSQL & REDIS & CACHING
    # ══════════════════════════════════════════════
    {
        "id": "datenbanken_01",
        "thema": "MySQL & Redis",
        "titel": "MySQL 8 im DevOps-Kontext 🗄️",
        "inhalt": (
            "🗄️ <b>MySQL 8 – Die Datenbank hinter Transfermarkt</b>\n\n"
            "MySQL ist eine <b>relationale Datenbank</b> – Daten in Tabellen, Zeilen, Spalten.\n"
            "Version 8 brachte viele Performance-Verbesserungen.\n\n"
            "🔑 <b>Als DevOps/Infra Engineer musst du wissen:</b>\n\n"
            "📊 <b>Performance-Monitoring:</b>\n"
            "<code>SHOW PROCESSLIST;</code> – laufende Queries\n"
            "<code>SHOW STATUS LIKE 'Slow_queries';</code> – langsame Queries\n"
            "<code>EXPLAIN SELECT * FROM users WHERE id=1;</code> – Query-Plan\n\n"
            "🔄 <b>Replication:</b>\n"
            "Primary (schreibt) → Replica (liest)\n"
            "Lese-Last wird auf Replicas verteilt → bessere Performance\n\n"
            "💾 <b>Backup-Strategie:</b>\n"
            "<code>mysqldump -u root -p mydb > backup.sql</code>\n"
            "Oder: Point-in-Time Recovery mit Binary Logs\n\n"
            "🐳 <b>MySQL in Docker (Transfermarkt-Style):</b>\n"
            "<code>docker run -d \\\n"
            "  -e MYSQL_ROOT_PASSWORD=geheim \\\n"
            "  -e MYSQL_DATABASE=transfermarkt \\\n"
            "  -v mysql_data:/var/lib/mysql \\\n"
            "  mysql:8</code>\n\n"
            "💡 <i>Merksatz: Primary schreibt, Replicas lesen. Volume mounten damit Daten überleben.</i>"
        ),
    },
    {
        "id": "datenbanken_02",
        "thema": "MySQL & Redis",
        "titel": "Redis & Memcache – Caching 🚀",
        "inhalt": (
            "🚀 <b>Redis & Memcache – Der Turbo für deine App</b>\n\n"
            "Problem: Jede Datenbankabfrage kostet Zeit.\n"
            "Lösung: Häufig genutzte Daten im <b>Arbeitsspeicher cachen</b>.\n\n"
            "🔴 <b>Redis:</b>\n"
            "• In-Memory Datenbank (blitzschnell, weil alles im RAM)\n"
            "• Kann Daten auf Disk speichern (persistent)\n"
            "• Unterstützt: Strings, Listen, Sets, Hashes, Sorted Sets\n"
            "• Auch nutzbar als: Message Queue, Session Store, Rate Limiter\n\n"
            "<code># Redis Beispiel\n"
            "redis-cli SET user:42:name \"Jens\"\n"
            "redis-cli GET user:42:name\n"
            "redis-cli SETEX session:abc123 3600 \"user_data\"  # 1h TTL</code>\n\n"
            "⚪ <b>Memcache:</b>\n"
            "• Simpler als Redis, nur Key-Value\n"
            "• Kein Persistence (Neustart = alles weg)\n"
            "• Sehr schnell für einfaches Caching\n"
            "• Gut für: HTML-Fragment-Cache, Session-Cache\n\n"
            "🔄 <b>Caching-Strategie (Cache-Aside):</b>\n"
            "1️⃣ App fragt Redis: 'Gibt es user:42?'\n"
            "2️⃣ Nein → App fragt MySQL\n"
            "3️⃣ Ergebnis in Redis speichern (mit TTL)\n"
            "4️⃣ Nächste Anfrage: Redis antwortet sofort\n\n"
            "💡 <i>Merksatz: Redis = schnelles Notizbuch im RAM. MySQL = das vollständige Archiv auf Disk.</i>"
        ),
    },
    {
        "id": "git_03",
        "thema": "Git",
        "titel": "Git Befehle Cheatsheet 📋",
        "inhalt": (
            "📋 <b>Git Befehle — Die wichtigsten auf einen Blick</b>\n\n"
            "Diese Befehle brauchst du täglich:\n\n"
            "<b>🆕 Repository starten:</b>\n"
            "<code>git init</code> — Neues Repo erstellen\n"
            "<code>git clone [url]</code> — Repo von GitHub holen\n\n"
            "<b>📸 Änderungen speichern:</b>\n"
            "<code>git status</code> — Was hat sich geändert?\n"
            "<code>git add .</code> — Alle Änderungen vorbereiten\n"
            "<code>git add [datei]</code> — Einzelne Datei vorbereiten\n"
            "<code>git commit -m 'Nachricht'</code> — Snapshot speichern\n\n"
            "<b>🌐 Mit GitHub synchronisieren:</b>\n"
            "<code>git push</code> — Änderungen hochladen\n"
            "<code>git pull</code> — Änderungen runterladen\n"
            "<code>git fetch</code> — Änderungen prüfen ohne merge\n\n"
            "<b>🌿 Branches:</b>\n"
            "<code>git branch</code> — Alle Branches anzeigen\n"
            "<code>git checkout -b feature/name</code> — Neuen Branch erstellen\n"
            "<code>git merge [branch]</code> — Branch zusammenführen\n\n"
            "<b>🔍 Historie:</b>\n"
            "<code>git log --oneline</code> — Kompakte Historie\n"
            "<code>git diff</code> — Änderungen anzeigen\n"
        ),
        "frage": "Welcher Befehl lädt deine lokalen Commits auf GitHub hoch?",
        "antworten": ["git pull", "git push", "git commit", "git fetch"],
        "richtig": 1,
        "erklaerung": "git push lädt deine lokalen Commits auf GitHub hoch. git pull macht das Gegenteil — es holt Änderungen von GitHub.",
    },
    {
        "id": "git_04",
        "thema": "Git",
        "titel": "Git Workflow — Von Code zu GitHub 🚀",
        "inhalt": (
            "🚀 <b>Git Workflow — So arbeitet ein Profi</b>\n\n"
            "Der Standard-Workflow für jedes Projekt:\n\n"
            "<b>1️⃣ Feature Branch erstellen</b>\n"
            "<code>git checkout -b feature/neue-funktion</code>\n"
            "→ Du arbeitest isoliert, main bleibt stabil\n\n"
            "<b>2️⃣ Änderungen machen & committen</b>\n"
            "<code>git add .</code>\n"
            "<code>git commit -m 'feat: neue Funktion hinzugefügt'</code>\n"
            "→ Gute Commit-Messages: was & warum, nicht wie\n\n"
            "<b>3️⃣ Auf GitHub pushen</b>\n"
            "<code>git push origin feature/neue-funktion</code>\n"
            "→ Branch ist jetzt auf GitHub sichtbar\n\n"
            "<b>4️⃣ Pull Request erstellen</b>\n"
            "→ Auf GitHub: 'Compare & Pull Request'\n"
            "→ Beschreibung schreiben, Review anfragen\n\n"
            "<b>5️⃣ Merge & aufräumen</b>\n"
            "<code>git checkout main</code>\n"
            "<code>git pull</code>\n"
            "<code>git branch -d feature/neue-funktion</code>\n\n"
            "<b>💡 Für JensHQ:</b>\n"
            "Jede neue James-Funktion = eigener Branch\n"
            "Bugfix = fix/beschreibung\n"
            "Feature = feature/beschreibung\n"
        ),
        "frage": "In welchem Schritt des Git-Workflows erstellst du einen neuen Branch?",
        "antworten": ["Schritt 3 — Push", "Schritt 1 — Branch erstellen", "Schritt 4 — Pull Request", "Schritt 5 — Merge"],
        "richtig": 1,
        "erklaerung": "Du erstellst den Branch als erstes mit 'git checkout -b feature/name' — so arbeitest du isoliert ohne den main-Branch zu gefährden.",
    },
]


# ══════════════════════════════════════════════
#  HILFSFUNKTIONEN
# ══════════════════════════════════════════════

THEMEN_LEKTIONEN = list(dict.fromkeys(l["thema"] for l in LEKTIONEN))

def get_lektion_by_id(lektion_id: str) -> dict | None:
    return next((l for l in LEKTIONEN if l["id"] == lektion_id), None)

def get_lektionen_by_thema(thema: str) -> list:
    return [l for l in LEKTIONEN if l["thema"] == thema]

def get_alle_ids() -> list:
    return [l["id"] for l in LEKTIONEN]

if __name__ == "__main__":
    print(f"Lektionen gesamt: {len(LEKTIONEN)}")
    print(f"Themen: {THEMEN_LEKTIONEN}")
    for t in THEMEN_LEKTIONEN:
        leks = get_lektionen_by_thema(t)
        print(f"  {t}: {len(leks)} Lektionen")

# ══════════════════════════════════════════════

THEMEN_LEKTIONEN = list(dict.fromkeys(l["thema"] for l in LEKTIONEN))

def get_lektion_by_id(lektion_id: str) -> dict | None:
    return next((l for l in LEKTIONEN if l["id"] == lektion_id), None)

def get_lektionen_by_thema(thema: str) -> list:
    return [l for l in LEKTIONEN if l["thema"] == thema]

def get_alle_ids() -> list:
    return [l["id"] for l in LEKTIONEN]

if __name__ == "__main__":
    print(f"Lektionen gesamt: {len(LEKTIONEN)}")
    print(f"Themen: {THEMEN_LEKTIONEN}")
    for t in THEMEN_LEKTIONEN:
        leks = get_lektionen_by_thema(t)
        print(f"  {t}: {len(leks)} Lektionen")