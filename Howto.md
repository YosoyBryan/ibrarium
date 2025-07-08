Certainly! Here is a clear, step-by-step English version of the IBRARIUM installation tutorial, designed specifically for non-coders, with simple language and no technical jargon:


---

IBRARIUM Tutorial: Install Your Home Automation System (No Coding Needed)


---

🚀 Before You Start: What You Will Need

A Raspberry Pi (models 3B+, 4, or 5 recommended) or any Linux computer

A MicroSD card of at least 16 GB (like a fast USB stick)

Power supply for your Raspberry Pi

Internet connection (Wi-Fi or Ethernet)

Your smartphone with Telegram installed (the messaging app)

A Telegram account, and a Telegram bot created (you will get a “token” from BotFather)

Devices you want to control:

Wi-Fi devices like smart plugs and bulbs (TP-Link Kasa, Tuya/Smart Life...)

Infrared-controlled devices (TV, air conditioner, Hi-Fi)

Devices connected to the Pi’s GPIO pins (relays, sensors, etc.)




---

🛠️ Step 1: Prepare Your Raspberry Pi

1.1 Download the Software to Prepare Your MicroSD Card

Go to raspberrypi.com/software

Download Raspberry Pi Imager for your computer


1.2 Install Raspberry Pi OS (Pi’s Operating System)

Insert your MicroSD card into your computer

Open Raspberry Pi Imager

Choose Raspberry Pi OS (64-bit)

Select your MicroSD card

Click the gear icon ⚙️ (bottom right) to configure:

Give your Pi a name (example: ibrarium-pi)

Enable SSH so you can control the Pi remotely

Set up your Wi-Fi network (name + password)

Choose your time zone and keyboard layout


Click Save, then Write to install the OS on the card


1.3 Start Your Raspberry Pi

Remove the MicroSD card from your computer

Insert it into your Raspberry Pi

Plug in the power supply

Wait for the Pi to boot (green light will blink)



---

🔑 Step 2: Access Your Raspberry Pi Remotely (via SSH)

This lets you control your Pi from your computer without needing a monitor or keyboard attached.

2.1 Find Your Pi’s IP Address

Check your internet router’s device list

Or use an app like Fing on your phone to scan your network


2.2 Connect to Your Pi

On your computer, open a Terminal (Linux/macOS) or use PuTTY on Windows

Type the command (replace PI_IP_ADDRESS with your Pi’s IP):

ssh pi@PI_IP_ADDRESS

If it’s your first time connecting, type yes

Enter the password you set earlier (default is “raspberry” if unchanged)


You are now connected to your Raspberry Pi and can enter commands.


---

📂 Step 3: Install IBRARIUM Files

Option A: Download Automatically from GitHub (Recommended)

Create a free GitHub account at github.com

In the Pi terminal, type:

cd ~
git clone https://github.com/YOUR_GITHUB_USERNAME/IBRARIUM-BY-JAMES-AND-GMN.git
cd IBRARIUM-BY-JAMES-AND-GMN

This downloads all necessary files to your Pi


Option B: Copy Files Manually (Simpler but Less Convenient)

In the terminal, create folders:

mkdir ~/IBRARIUM
cd ~/IBRARIUM
mkdir scripts

For each file (main_ibrarium.py, ibrarium_config.json, ibrarium_wifi_plug_generic.py), open it with the simple editor nano and paste the full code, then save:

nano main_ibrarium.py
# paste code
# save with Ctrl+X, then Y, then Enter

Repeat for each file, placing scripts in the scripts folder (cd scripts).



---

🐍 Step 4: Install Python Libraries

From the main project folder (~/IBRARIUM or similar), create a virtual environment:

python3 -m venv venv

Activate it:

source venv/bin/activate

Install the necessary packages:

pip install pyTelegramBotAPI python-kasa tinytuya RPi.GPIO lirc

These packages let IBRARIUM control your Wi-Fi devices, GPIO pins, and infrared devices.



---

▶️ Step 5: Launch IBRARIUM

While the virtual environment is active, start the bot:

python3 main_ibrarium.py

The system will start and show messages in the terminal. Your bot is now ready to accept commands via Telegram.



---

✅ Step 6: Test Telegram Commands

Open Telegram and open a chat with your bot

Send these commands to check if it responds:

/start

/help

/ping (should reply with pong 🟢)

/status

/wifi_list (shows configured Wi-Fi devices)


Control devices (if configured) with:

/wifi_on your_device_name

/wifi_off your_device_name

/wifi_toggle your_device_name

/wifi_status your_device_name




---

🔧 Troubleshooting Tips

Bot does not respond?

Double-check your ibrarium_config.json for typos or wrong tokens/IDs

Look for error messages in the terminal

Verify your Pi’s internet connection


Wi-Fi devices don’t respond?

Make sure IP addresses are correct in the config file

Confirm that devices and Pi are on the same Wi-Fi network


GPIO or IR devices don’t work?

Check your wiring carefully

For IR, make sure LIRC is installed and configured (this needs a bit more setup)




---

🔮 Future Enhancements & Innovative Ideas

Automate routines: Program IBRARIUM to perform tasks automatically, like turning lights on at sunset or when sensors detect motion.

Create a web dashboard: Manage all devices from a single web page.

Add voice control: Connect open-source voice assistants for hands-free operation.

Keep your system updated and backed up: Regularly push your configuration to GitHub to save your work and get the latest improvements.



---

If you want, I can also provide a ready-to-edit sample ibrarium_config.json file with detailed comments to help you customize it easily. Would you like me to do that?


---

Feel free to ask for any clarification, wiring guides, or step-by-step help!

