Ce guide est fait pour vous, même si vous n'avez jamais écrit une ligne de code. Nous allons installer IBRARIUM, votre système domotique capable de contrôler des appareils via Wi-Fi, Infrarouge (IR) et les ports GPIO de votre Raspberry Pi.
Un systeme pas chère, sans abonnement qui rends "intelligent" votre portail, votre garage, votre machine à café, votre climatiseur.


🚀 Étape 0 : Ce dont vous aurez besoin
 * Un ordinateur de contrôle : Idéalement, un Raspberry Pi (modèle 3B+, 4 ou 5 recommandé) avec une carte MicroSD de 16 Go minimum. Vous pouvez aussi utiliser un PC Linux.
 * Une alimentation pour votre Raspberry Pi.
 * Un accès à Internet.
 * Votre téléphone avec l'application Telegram installée.
 * Vos identifiants Telegram Bot : Obtenez votre "API Token" depuis BotFather dans Telegram. Trouvez aussi votre propre ID utilisateur Telegram avec @userinfobot.
 * Les appareils que vous voulez contrôler :
   * Appareils Wi-Fi : Prises connectées (Kasa/TP-Link, Tuya/Smart Life), ampoules Wi-Fi.
   * Appareils Infrarouges (IR) : Télévisions, climatiseurs, chaînes Hi-Fi contrôlables par télécommande IR. Vous aurez besoin d'un émetteur/récepteur IR branché à votre Raspberry Pi (souvent via les ports GPIO, avec un câblage simple).
   * Appareils GPIO : Relais pour lumières, moteurs, ventilateurs ; capteurs de mouvement, de porte/fenêtre. Vous aurez besoin de câbler ces composants à votre Raspberry Pi.
🛠️ Étape 1 : Préparer Votre Raspberry Pi (ou PC Linux)
Pour un nouveau Raspberry Pi
 * Téléchargez Raspberry Pi Imager : Allez sur raspberrypi.com/software.
 * Préparez la carte MicroSD : Insérez-la dans votre ordinateur.
 * Lancez Raspberry Pi Imager :
   * Choisissez Raspberry Pi OS (64-bit).
   * Sélectionnez votre carte MicroSD.
   * Cliquez sur l'icône ⚙️ (en bas à droite) :
     * Définissez un nom d'hôte (ex: ibrarium-pi).
     * Activez SSH (avec authentification par mot de passe). Notez le nom d'utilisateur (par défaut pi) et le mot de passe.
     * Configurez le Wi-Fi (nom du réseau et mot de passe).
     * Définissez les paramètres régionaux (fuseau horaire, clavier).
   * Cliquez sur "SAVE", puis "WRITE".
 * Démarrez le Raspberry Pi : Insérez la carte, branchez l'alimentation.
Pour un Raspberry Pi (ou PC Linux) existant
 * Ouvrez une fenêtre de "Terminal". C'est une application où vous pouvez taper des commandes. Sur la plupart des systèmes Linux, vous la trouverez dans le menu "Accessoires" ou en cherchant "Terminal".
 * Mettez à jour votre système : Dans cette fenêtre de Terminal, tapez les commandes suivantes une par une et appuyez sur Entrée après chaque ligne. Si on vous demande votre mot de passe, tapez-le (il ne s'affichera pas, c'est normal) et appuyez sur Entrée.
   sudo apt update
sudo apt upgrade -y

 * Installez Python 3 : Toujours dans la fenêtre de Terminal, tapez :
   sudo apt install python3 python3-venv -y

Accéder à votre Raspberry Pi à distance (via SSH - Recommandé)
Cette méthode vous permet de contrôler votre Raspberry Pi depuis votre ordinateur, sans avoir besoin d'un écran et d'un clavier branchés directement sur le Pi.
 * Trouvez l'adresse IP de votre Raspberry Pi. (Regardez sur l'interface de votre routeur internet, ou utilisez une application comme "Fing" sur votre téléphone).
 * Ouvrez une fenêtre de "Terminal" sur votre ordinateur (sur Linux/macOS) ou le logiciel PuTTY (sur Windows).
 * Connectez-vous via SSH : Dans cette fenêtre de Terminal (ou PuTTY), tapez :
   ssh pi@ADRESSE_IP_DU_PI

   (Remplacez ADRESSE_IP_DU_PI par l'adresse IP que vous avez trouvée). Appuyez sur Entrée.
   Si c'est la première fois, on vous demandera si vous êtes sûr de vouloir continuer, tapez yes et Entrée.
   On vous demandera ensuite le mot de passe que vous avez défini lors de la préparation de la carte SD. Tapez-le (il ne s'affichera pas) et appuyez sur Entrée.
   Vous êtes maintenant connecté à votre Raspberry Pi. Toutes les commandes suivantes seront à taper dans cette fenêtre.
📂 Étape 2 : Créer les Dossiers et Obtenir les Fichiers
Nous allons créer les dossiers nécessaires et y placer les fichiers d'IBRARIUM. Vous avez deux options pour obtenir ces fichiers :
Option A : Utiliser GitHub (Recommandé)
Pourquoi c'est utile :
 * Sauvegarde automatique : Vos fichiers sont en sécurité en ligne. Si votre Pi a un problème, vous ne perdez rien.
 * Mises à jour faciles : Si les scripts sont améliorés, vous pourrez les mettre à jour d'une seule commande.
 * Partage et aide : Plus facile de partager votre configuration ou de demander de l'aide si besoin.
Comment faire :
 * Créez un compte GitHub si vous n'en avez pas (github.com).
 * Clonez le dépôt IBRARIUM (ou votre propre copie) :
   Dans la fenêtre de Terminal (connectée à votre Pi), tapez les commandes suivantes :
   cd ~
git clone https://github.com/VOTRE_NOM_UTILISATEUR_GITHUB/IBRARIUM-BY-JAMES-AND-GMN.git
cd IBRARIUM-BY-JAMES-AND-GMN

   (Remplacez VOTRE_NOM_UTILISATEUR_GITHUB par le vrai nom du dépôt ou votre utilisateur si c'est une copie).
 * Les fichiers main_ibrarium.py et ibrarium_config.json seront à la racine du dossier IBRARIUM-BY-JAMES-AND-GMN. Le fichier ibrarium_wifi_plug_generic.py sera dans le dossier scripts/. D'autres scripts pour IR ou GPIO pourraient apparaître dans scripts/ à l'avenir.
Option B : Copier les Fichiers Manuellement (Sans GitHub)
Pourquoi c'est utile :
 * Plus simple au démarrage : Pas besoin de compte GitHub ni de comprendre la commande git.
Inconvénients :
 * Pas de sauvegarde automatique : Si votre Pi est endommagé, vous perdez tout.
 * Mises à jour manuelles : Si les scripts sont mis à jour, vous devrez copier chaque nouveau fichier un par un.
 * Moins pratique pour l'aide : Plus difficile de partager votre configuration ou de recevoir un diagnostic précis.
Comment faire :
 * Créez le dossier principal du projet :
   Dans la fenêtre de Terminal (connectée à votre Pi), tapez :
   mkdir ~/IBRARIUM
cd ~/IBRARIUM

 * Créez le dossier pour les scripts :
   mkdir scripts

 * Créez les fichiers un par un et collez le contenu :
   * Fichier 1 : main_ibrarium.py
     Assurez-vous d'être dans le dossier ~/IBRARIUM.
     Tapez : nano main_ibrarium.py et appuyez sur Entrée.
     Copiez le code complet de main_ibrarium.py (la dernière version que nous avons validée) et collez-le dans la fenêtre de nano.
     Pour sauvegarder : Appuyez sur Ctrl+X, puis Y (pour Yes), puis Entrée.
   * Fichier 2 : ibrarium_config.json
     Assurez-vous d'être dans le dossier ~/IBRARIUM.
     Tapez : nano ibrarium_config.json et appuyez sur Entrée.
     Copiez le code complet de ibrarium_config.json (la dernière version détaillée et commentée) et collez-le.
     Très important : Personnalisez le api_token Telegram, vos allowed_user_ids, et les détails de vos appareils (adresses IP pour le Wi-Fi, broches GPIO, etc.).
     Pour le chemin du fichier de log ("log_file" dans la section "system_info"), changez-le pour un dossier auquel l'utilisateur pi a accès, par exemple :
     "log_file": "/home/pi/IBRARIUM/ibrarium.log"
     Sauvegardez (Ctrl+X, Y, Entrée).
   * Fichier 3 : ibrarium_wifi_plug_generic.py (Pour le contrôle Wi-Fi)
     Allez dans le dossier scripts :
     cd scripts

     Tapez : nano ibrarium_wifi_plug_generic.py et appuyez sur Entrée.
     Copiez le code complet de ibrarium_wifi_plug_generic.py (la dernière version validée) et collez-le.
     Sauvegardez (Ctrl+X, Y, Entrée).
     Retournez au dossier principal du projet :
     cd ..

     Note : D'autres fichiers Python pour IR ou GPIO (par exemple, ibrarium_ir_control.py ou ibrarium_gpio_control.py) devraient être placés dans ce même dossier scripts/ si vous les obtenez.
🐍 Étape 3 : Installer les Bibliothèques Python
Que vous ayez choisi l'option A ou B, cette étape est la même.
 * Créez l'environnement virtuel :
   Assurez-vous d'être dans le dossier principal de votre projet (ex: ~/IBRARIUM ou ~/IBRARIUM-BY-JAMES-AND-GMN).
   Dans la fenêtre de Terminal, tapez :
   python3 -m venv venv

 * Activez l'environnement virtuel :
   Dans la fenêtre de Terminal, tapez :
   source venv/bin/activate

   Vous verrez (venv) apparaître devant votre ligne de commande, cela signifie que l'environnement est activé.
 * Installez les bibliothèques :
   Dans la fenêtre de Terminal, tapez :
   pip install pyTelegramBotAPI python-kasa tinytuya RPi.GPIO lirc

   * pyTelegramBotAPI : Pour le bot Telegram.
   * python-kasa : Pour les prises TP-Link Kasa (Wi-Fi).
   * tinytuya : Pour les prises Tuya/Smart Life (Wi-Fi).
   * RPi.GPIO : Pour le contrôle direct des broches GPIO du Raspberry Pi.
   * lirc : Pour le contrôle infrarouge (IR).
   * Note : N'hésitez pas à installer toutes ces bibliothèques même si vous n'utilisez pas toutes les fonctionnalités, cela évitera des problèmes plus tard.
▶️ Étape 4 : Lancer IBRARIUM !
 * Lancez le script principal :
   Assurez-vous que votre environnement virtuel est toujours activé ((venv) est visible).
   Dans la fenêtre de Terminal, tapez :
   python3 main_ibrarium.py

 * Le bot devrait démarrer et afficher des messages dans cette même fenêtre de Terminal.
✅ Étape 5 : Tester les Commandes Telegram
 * Ouvrez Telegram et allez à la conversation avec votre bot.
 * Commandes de base : Tapez et envoyez ces commandes à votre bot :
   * /start
   * /help
   * /ping (doit répondre "pong 🟢")
   * /status
   * /wifi_list (liste les appareils Wi-Fi configurés)
 * Commandes de contrôle (selon votre configuration) :
   * Pour le Wi-Fi (si configuré dans ibrarium_config.json) :
     * /wifi_on nom_de_votre_prise_wifi
     * /wifi_off nom_de_votre_prise_wifi
     * /wifi_toggle nom_de_votre_prise_wifi
     * /wifi_status nom_de_votre_prise_wifi
   * Pour les GPIO (si configuré et câblé) :
     * ibrarium_config.json contient une section hardware.gpio_control.pins avec des exemples comme relay_1, sensor_1.
     * Les commandes exactes dépendront du script GPIO (non encore développé ici, mais la structure est prête).
   * Pour l'Infrarouge (IR) (si configuré et hardware IR branché) :
     * ibrarium_config.json peut inclure une section protocols.ir avec des codes IR.
     * Les commandes exactes dépendront du script IR (non encore développé ici).
Résolution de Problèmes
 * Le bot ne démarre pas ou ne répond pas :
   * Vérifiez attentivement votre fichier ibrarium_config.json : une erreur de frappe, une virgule manquante, un ID Telegram ou un token invalide. La syntaxe JSON est très stricte.
   * Regardez les messages d'erreur qui s'affichent dans la fenêtre de Terminal où vous avez lancé le bot.
   * Vérifiez la connexion Internet de votre Raspberry Pi.
 * Les appareils ne répondent pas :
   * Wi-Fi : Vérifiez les adresses IP dans ibrarium_config.json. Sont-elles correctes et les prises sont-elles connectées au même Wi-Fi que votre Pi ? Pour Tuya, vérifiez device_id et local_key.
   * GPIO : Vérifiez le câblage. Les broches sont-elles correctement connectées ?
   * IR : Vérifiez le câblage de l'émetteur/récepteur IR. Le Pi est-il bien configuré pour LIRC (nécessite une configuration système en dehors de Python) ?
