en français c'est plus bas 🇫🇷🇺🇸
c'est pour toi Xav 
# IBRARIUM BY JAMES AND GMN
 Ultra-cost-effective home automation solution, designed to transform any Raspberry Pi into a powerful and accessible command center. Forget expensive and complex systems: control everything in your home with a simple Telegram message, directly from your phone, anywhere in the world!
Why IBRARIUM Is Revolutionary
Existing "smart home" solutions are often costly, proprietary, or incompatible with your favorite devices (old AC, non-connected blinds, vintage hi-fi system). IBRARIUM breaks these barriers by offering:
 * Total Control via Telegram: Send commands in natural language using the Telegram app you already use.
 * Minimal Cost: Based on a Raspberry Pi Zero W (or similar) and basic modules.
 * Maximum Versatility: Control devices via Infrared (IR), GPIO relays, and even interact with local web interfaces of Wi-Fi plugs or other devices to make them "smart."
 * Simplicity: Forget command-line interfaces (CLI) or technical setups. IBRARIUM translates your messages into concrete actions without you needing to worry about "how."
How It Works: The Magic Behind the Simplicity
 * You send a message (e.g., "coffee ready in 5 min") to your IBRARIUM Telegram bot from your phone.
 * The Raspberry Pi (hosting your IBRARIUM bot) receives and analyzes this command.
 * The IBRARIUM system triggers the appropriate Python script.
 * This script uses:
   * Infrared (IR) for "dumb" devices (AC, TV).
   * GPIO pins on the Pi for relays (blinds, direct lights).
   * Or Playwright to automate interaction with the local web interface of your Wi-Fi plug (or other locally connected device).
 * The Pi can confirm the action back to you via a Telegram message.
Revolutionary Use Cases (Concrete Examples)
 * Smart Coffee Machine:
   * Telegram Command: "coffee ready in 5 min"
   * IBRARIUM Action: The Raspberry Pi, via Playwright, connects to the web interface of your Wi-Fi plug (which must be connected to your local network) and turns on the plug, starting the coffee machine for fresh coffee when you wake up.
 * Remotely Manageable Washing Machine:
   * Telegram Command: "start washing machine"
   * IBRARIUM Action: The Pi uses Playwright to access the web interface of your washing machine's Wi-Fi plug and activates it. Perfect for starting a cycle when electricity rates are low or when you're about to arrive home.
 * IR Control for Legacy Devices: Turn on your old AC or TV with a simple Telegram message.
 * Smart Garden Watering: Trigger watering based on weather and soil moisture via Telegram.
 * Garage Door Management: Open/close your garage via a secure chat command.
 * "Dumb" Lights Made "Smart": Control your standard lamps via relays or IR plugs.
Key Components
 * Raspberry Pi (Zero W recommended for cost and versatility)
 * IR Emitter Module (for infrared control)
 * Relay Modules (for GPIO control: lights, pumps)
 * GPIO Sensors (optional: soil moisture, etc.)
 * Wi-Fi Plugs with Local Web Interface (for coffee machines, washing machines, etc. - crucial for not relying on the cloud)
 * Telegram Bot API (for message communication)
 * Python 3
 * Python Libraries: pyTelegramBotAPI, gpiozero, playwright
 * LIRC (for IR control)
 * 
## Révolutionnez Votre Quotidien avec IBRARIUM : La Télécommande Ultime par Message Telegram !

**IBRARIUM BY JAMES AND GMN** est une solution d'automatisation domestique innovante et **ultra-économique**, transformant un simple Raspberry Pi en un centre de commande puissant et accessible. Fini les systèmes coûteux et complexes : contrôlez une multitude d'appareils dans votre maison avec un simple message **Telegram**, directement depuis votre téléphone, n'importe où dans le monde !

### Pourquoi IBRARIUM est Révolutionnaire ?

Les solutions "smart home" existantes sont souvent coûteuses, propriétaires, ou incompatibles avec vos appareils existants. IBRARIUM brise ces barrières en offrant :

* **Contrôle Total par Telegram :** Envoyez des commandes en langage naturel via l'application Telegram que vous utilisez déjà.
* **Coût Minimal :** Basé sur un Raspberry Pi Zero W (ou similaire) et des modules basiques.
* **Polyvalence Maximale :** Contrôlez des appareils via Infrarouge (IR), des relais GPIO, et **interagissez même avec des interfaces web de prises Wi-Fi ou d'autres appareils pour les rendre "smart"**.
* **Simplicité :** Oubliez la complexité de la ligne de commande (CLI) ou des interfaces techniques. IBRARIUM traduit vos messages en actions concrètes sans que vous ayez à vous soucier du "comment".

### Comment Ça Marche ? La Magie Derrière la Simplicité

1.  **Vous envoyez un message** (ex: "café prêt dans 10 min") à votre bot Telegram IBRARIUM depuis votre téléphone.
2.  Le **Raspberry Pi** (hébergeant votre bot IBRARIUM) reçoit et analyse cette commande.
3.  Le système IBRARIUM déclenche le script Python approprié.
4.  Ce script utilise :
    * L'**Infrarouge (IR)** pour les appareils "bêtes" (clim, TV).
    * Les broches **GPIO** du Pi pour des relais (volets, lumières directes).
    * Ou **Playwright** pour automatiser l'interaction avec l'interface web locale de votre prise Wi-Fi (ou autre appareil connecté localement).
5.  Le Pi peut vous **confirmer l'action** par un message Telegram.

### Cas d'Usage Révolutionnaires (Quelques Exemples Concrets)

* **Machine à Café Intelligente :**
    * **Commande Telegram :** `"café prêt dans 5 min"`
    * **Action IBRARIUM :** Le Raspberry Pi, via Playwright, se connecte à l'interface web de votre prise Wi-Fi (qui doit être connectée à votre réseau local) et allume la prise, mettant en marche la cafetière pour un café frais à votre réveil.
* **Machine à Laver Gérable à Distance :**
    * **Commande Telegram :** `"lance machine a laver"`
    * **Action IBRARIUM :** Le Pi utilise Playwright pour accéder à l'interface web de la prise Wi-Fi de votre machine à laver, et l'active. Idéal pour lancer un cycle quand les tarifs d'électricité sont bas ou quand vous êtes sur le point de rentrer.
* **Contrôle IR pour Anciens Appareils :** Allumez votre vieille clim ou votre TV par simple message Telegram.
* **Arrosage Intelligent du Jardin :** Déclenchez l'arrosage en fonction de la météo et de l'humidité du sol via Telegram.
* **Gestion de Porte de Garage :** Ouvrez/fermez votre garage via une commande sécurisée par chat.
* **Lumières "Bêtes" en "Intelligentes" :** Contrôlez vos lampes standards via relais ou prises IR.

### Composants Clés

* **Raspberry Pi** (Zero W recommandé pour son coût et sa polyvalence)
* **Module Émetteur IR** (pour le contrôle infrarouge)
* **Modules Relais** (pour le contrôle GPIO : lumières, pompes)
* **Capteurs GPIO** (optionnel : humidité du sol, etc.)
* **Prises Wi-Fi avec Interface Web Locale** (pour les machines à café, à laver, etc. - crucial pour ne pas dépendre du cloud)
* **Telegram Bot API** (pour la communication par message)
* **Python 3**
* **Bibliothèques Python :** `pyTelegramBotAPI`, `gpiozero`, `playwright`
* **LIRC** (pour le contrôle IR)

### Démarrage Rapide

Ce dépôt contient toutes les instructions pour installer et configurer IBRARIUM sur votre Raspberry Pi et commencer à automatiser votre maison.

---

**IBRARIUM BY JAMES AND GMN : Votre Maison. Votre Contrôle. Votre Façon.**

-
