# YO le Xav

# IBRARIUM BY JAMES AND GMN

Ultra-cost-effective home automation solution: transform any Raspberry Pi into a powerful, accessible command center.  
🇫🇷 [Version française plus bas](#ibrarium-en-français)

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

---

## Table of Contents

- [About](#about)
- [Features](#features)
- [How it works](#how-it-works)
- [Quick Start](#quick-start)
- [Key Components](#key-components)
- [Use Cases](#use-cases)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [IBRARIUM en français](#ibrarium-en-français)

---

## About

IBRARIUM is an ultra-affordable, open smart home solution for makers and hackers.
Control everything in your home via Telegram, with no cloud dependency or vendor lock-in.

Forget the command line CLI : IBRARIUM is made for everyone. No more complicated setup: just use Telegram to control your home.

## Features

- Control devices with natural language via Telegram
- Run on Raspberry Pi Zero W (or similar)
- Manage devices via IR, GPIO relays, or local Wi-Fi web interfaces
- No command line or technical setup required for users

## How it works

1. Send a message (e.g. "coffee ready in 5 min") to your IBRARIUM Telegram bot.
2. Your Pi receives and interprets the command.
3. IBRARIUM triggers a Python script to control IR, GPIO, or a local web interface.
4. Confirmation sent back via Telegram.

## Quick Start

```bash
git clone https://github.com/librariums/ibrarium.git
cd ibrarium
# Install dependencies
pip install -r requirements.txt
# Follow setup instructions in HOWTO.md
```

## Key Components

- Raspberry Pi (Zero W recommended)
- IR emitter module
- Relay modules (for GPIO)
- Wi-Fi plugs with local web interface
- Telegram Bot API
- Python 3, pyTelegramBotAPI, gpiozero, playwright, LIRC

## Use Cases

- Add smart capabilities to an old appliance
- Upgrade a traditional appliance to a smart one
- Smart coffee machine
- Remote washing machine control
- IR control for legacy devices
- Smart garden watering
- Garage door via Telegram
- "Dumb" lights made smart

## Contributing

Want to contribute? Feel free to submit issues or pull requests.  
See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## License

MIT License — see [LICENSE](./LICENSE) for details.

## Contact

Questions, ideas? Open an issue or contact the authors via Telegram!

---

# IBRARIUM EN FRANÇAIS

Solution domotique ultra-économique : transformez n’importe quel Raspberry Pi en un centre de commande puissant et accessible.  
🇬🇧 [English version above](#ibrarium-by-james-and-gmn)

[![Licence MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

---

## Table des matières

- [À propos](#à-propos)
- [Fonctionnalités](#fonctionnalités)
- [Comment ça marche](#comment-ça-marche)
- [Démarrage rapide](#démarrage-rapide)
- [Composants clés](#composants-clés)
- [Cas d’usage](#cas-dusage)
- [Contribuer](#contribuer)
- [Licence](#licence)
- [Contact](#contact)
- [IBRARIUM in English](#ibrarium-by-james-and-gmn)

---

## À propos

IBRARIUM est une solution domotique ouverte et ultra-abordable pour makers et bidouilleurs.
Contrôlez tout chez vous via Telegram, sans cloud ni verrouillage propriétaire.

Oubliez la ligne de commande  CLI : IBRARIUM est fait pour tous. Plus besoin de configurations compliquées, contrôlez tout simplement votre maison via Telegram.

## Fonctionnalités

- Contrôle des appareils en langage naturel via Telegram
- Fonctionne sur Raspberry Pi Zero W (ou équivalent)
- Pilote des appareils via IR, relais GPIO ou interfaces web Wi-Fi locales
- Aucun besoin de ligne de commande ou de configuration technique pour l’utilisateur

## Comment ça marche

1. Envoyez un message (ex. : "café prêt dans 5 min") à votre bot Telegram IBRARIUM.
2. Votre Pi reçoit et interprète la commande.
3. IBRARIUM déclenche un script Python pour piloter l’IR, les GPIO ou une interface web locale.
4. Confirmation envoyée par Telegram.

## Démarrage rapide

```bash
git clone https://github.com/librariums/ibrarium.git
cd ibrarium
# Installer les dépendances
pip install -r requirements.txt
# Suivez les instructions dans HOWTO.md
```

## Composants clés

- Raspberry Pi (Zero W recommandé)
- Module émetteur IR
- Modules relais (pour GPIO)
- Prises Wi-Fi avec interface web locale
- Telegram Bot API
- Python 3, pyTelegramBotAPI, gpiozero, playwright, LIRC

## Cas d’usage

- Donner une seconde vie numérique à un appareil classique
- Rendre un appareil traditionnel intelligent
- Machine à café intelligente ou la transformer en machine à café intelligent
- Contrôle de machine à laver à distance
- Contrôle IR pour appareils anciens
- Arrosage intelligent du jardin
- Porte de garage via Telegram
- Lampes classiques rendues intelligentes

## Contribuer

Envie de contribuer ? Proposez des issues ou des pull requests.  
Voir [CONTRIBUTING.md](./CONTRIBUTING.md) pour les règles de contribution.

## Licence

Licence MIT — voir [LICENSE](./LICENSE) pour les détails.

## Contact

Questions ou idées ? Ouvrez une issue.

---
