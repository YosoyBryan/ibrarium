# HOWTO\_TELEGRAM.md

*en Français plus bas*

---

## 📄 TABLE OF CONTENTS

1. Introduction
2. Requirements
3. Step-by-step: Create or Use a Telegram Bot
4. Configuration (with or without GitHub)
5. Launch the Bot
6. Understanding the Syntax (like `*`)
7. Useful Commands
8. Troubleshooting
9. FAQ
10. Credits

---

## 1. Introduction

This guide explains how to configure and use a Telegram bot that automatically executes any `ibrarium_*.py` script.

---

## 2. Requirements

- A Telegram account
- Python 3.10+
- Access to run scripts (on your computer or server)

---

## 3. Step-by-step: Create or Use a Telegram Bot

### Option A: I don't have a bot yet

1. Open Telegram and search for **@BotFather**
2. Type `/start` then `/newbot`
3. Choose a name (e.g., `MyCoffeeBot`)
4. Choose a username (must end in `bot`, like `coffeetime_bot`)
5. Copy the **token** given (looks like `12345678:ABCDefGhIjKlMnOpQRstUvWxYZ`)

### Option B: I already have a bot

1. Go to **@BotFather**
2. Type `/mybots` then select your bot
3. Tap on `API Token` to retrieve it

---

## 4. Configuration (with or without GitHub)

### If you want to use GitHub

1. Go to [https://github.com/librariums/ibrarium](https://github.com/librariums/ibrarium)
2. Fork the repository (top-right corner)
3. Edit files directly from the GitHub web interface

### Without GitHub

1. Download the project as ZIP
2. Extract the folder on your computer
3. Open the file `telegram_bot_general.py` in any text editor

> Find the line that says:
>
> ```python
> TELEGRAM_BOT_TOKEN = "YOUR_TOKEN_HERE"
> ```
>
> Replace `YOUR_TOKEN_HERE` with the token you got from BotFather

---

## 5. Launch the Bot

Run the following command in your terminal:

```bash
python telegram_bot_general.py
```

If everything is correct, your bot is now online and listening.

---

## 6. Understanding the Syntax

### What does `ibrarium_*.py` mean?

It means: any script that starts with `ibrarium_` and ends with `.py`. Examples:

- `ibrarium_coffee.py`
- `ibrarium_lights.py`

The `*` is a wildcard — it replaces "anything" in the name.

You don’t need to understand or change these filenames. Just type the command (like `coffee`) in Telegram to run the script `ibrarium_coffee.py`.

---

## 7. Useful Commands

Once your bot is running:

- Type `coffee` to run the coffee machine immediately
- Type `coffee 5` to run it in 5 minutes
- Type `coffee at 7:45` to schedule it

Replace `coffee` with the name of any other script prefix after `ibrarium_`.

---

## 8. Troubleshooting

- **Nothing happens when I type a command**

  - Make sure your script name follows `ibrarium_*.py`
  - Check that the script is in the same folder
  - Verify your bot token is correct

- **I see a Python error**

  - Share the error with a developer or via the Telegram group

---

## 9. FAQ

**Q: Can I use the bot without coding?**

> Yes! Just follow this tutorial step-by-step and use copy-paste when needed.

**Q: What if I have several bots?**

> You can run several bots, but each one must have its own token and script.

---

## 10. Credits

- Inspired by [librariums/ibrarium](https://github.com/librariums/ibrarium)
- Built for no-code/low-code automation

---

# 🇫🇷 Français

## 1. Introduction

Ce guide explique comment configurer et utiliser un bot Telegram qui exécute automatiquement n'importe quel script `ibrarium_*.py`.

---

## 2. Prérequis

- Un compte Telegram
- Python 3.10+
- Accès à un ordinateur ou serveur pour lancer les scripts

---

## 3. Créer ou Utiliser un Bot Telegram

### Option A : Vous n'avez pas encore de bot

1. Ouvrez Telegram et cherchez **@BotFather**
2. Tapez `/start` puis `/newbot`
3. Choisissez un nom (ex : `MonBotCafe`)
4. Choisissez un nom d'utilisateur (doit se terminer par `bot`, ex : `cafetime_bot`)
5. Copiez le **token** donné (ressemble à `12345678:ABCDefGhIjKlMnOpQRstUvWxYZ`)

### Option B : Vous avez déjà un bot

1. Allez sur **@BotFather**
2. Tapez `/mybots` et sélectionnez votre bot
3. Cliquez sur `API Token` pour le récupérer

---

## 4. Configuration (avec ou sans GitHub)

### Si vous utilisez GitHub

1. Allez sur [https://github.com/librariums/ibrarium](https://github.com/librariums/ibrarium)
2. Cliquez sur "Fork" (en haut à droite)
3. Modifiez les fichiers directement depuis le site GitHub

### Sans GitHub

1. Téléchargez le projet en ZIP
2. Décompressez-le sur votre ordinateur
3. Ouvrez le fichier `telegram_bot_general.py`

> Cherchez la ligne :
>
> ```python
> TELEGRAM_BOT_TOKEN = "YOUR_TOKEN_HERE"
> ```
>
> Remplacez `YOUR_TOKEN_HERE` par le token obtenu via BotFather

---

## 5. Lancer le Bot

Dans un terminal, tapez :

```bash
python telegram_bot_general.py
```

Si tout est correct, votre bot est actif et à l'écoute.

---

## 6. Comprendre la Syntaxe

### Que signifie `ibrarium_*.py` ?

Cela veut dire : tout script dont le nom commence par `ibrarium_` et finit par `.py`. Exemples :

- `ibrarium_coffee.py`
- `ibrarium_lights.py`

Le symbole `*` est un **joker** — il remplace n'importe quel mot.

Vous n'avez pas besoin de comprendre ou modifier ces noms. Il suffit de taper (ex : `coffee`) dans Telegram pour exécuter le script `ibrarium_coffee.py`.

---

## 7. Commandes utiles

Une fois votre bot actif :

- Tapez `coffee` pour lancer la machine à café
- Tapez `coffee 5` pour lancer dans 5 minutes
- Tapez `coffee at 7:45` pour le programmer à une heure

Remplacez `coffee` par le nom d'un autre script si besoin.

---

## 8. Résolutions d'erreurs

- **Rien ne se passe quand je tape une commande**

  - Vérifiez que le nom du script suit `ibrarium_*.py`
  - Le script doit être dans le même dossier
  - Vérifiez que le token du bot est correct

- **J'ai une erreur Python**

  - Copiez l'erreur et demandez de l'aide au développeur \
    \
    9\. FAQ

**Q : Puis-je utiliser le bot sans coder ?**

> Oui ! Suivez simplement ce tutoriel étape par étape, en copiant-collant les commandes.

**Q : Et si j'ai plusieurs bots ?**

> Chaque bot doit avoir son propre token et son propre script à lancer.

---

## 10. Crédits

- Inspiré par [librariums/ibrarium](https://github.com/librariums/ibrarium) 
- Conçu pour les utilisateurs no-code / low-code

