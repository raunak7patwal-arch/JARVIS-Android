JARVIS PERMANENT STORAGE
========================

1. Run:

   cd ~/JARVIS-Android
   python jarvis/installer/setup_persistence.py

2. Create your own master password.

3. Password is never printed by the setup script.

4. JARVIS persistent vault:
   jarvis/central/security/vault.bin

5. Master-password metadata:
   jarvis/central/security/master.json

6. Termux:Boot startup script:
   ~/.termux/boot/start-jarvis.sh

IMPORTANT
=========

Termux itself is an Android app.

If Termux is uninstalled, Android may remove its private application data.
JARVIS cannot prevent Android from doing that.

For uninstall protection, keep an encrypted backup/export of the JARVIS
persistent data outside Termux, for example on a Pendrive or another
user-controlled storage location.

A normal Android File Manager cannot be forced by this Python program to
ask the JARVIS password before deleting a file. The JARVIS application can
require its master password for JARVIS-managed unlock, export, restore and
destructive operations.

Never put API keys, passwords or private keys into Git.
