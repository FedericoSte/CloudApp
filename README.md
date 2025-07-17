# CloudApp
Cloud App for Windows based on ssh protocol.

Cloud App was born as a project for personal use and needs, but I decided to publish it because I found it useful in different contexts.
CloudApp is written in python in a single file, to facilitate its conversion to .exe via the PYInstaller module.
The application is based on the ssh and sftp protocols to communicate with the server (a Linux server is required) to provide the classic services of a File Manager such as upload, downlad, copy, paste ...
The application uses multithreding to manage different execution flows.

Since the project is not a project for personal use, the code is very vertical and not extremely clear, I will update it with new versions.


Installation and usage will come soon...



<img width="395" height="388" alt="immagine" src="https://github.com/user-attachments/assets/d850251d-3d64-448a-9ee1-c04cae08f5dc" /> <img width="336" height="171" alt="immagine" src="https://github.com/user-attachments/assets/1645439c-4a18-4def-ba29-2c627711a338" />

<img width="996" height="836" alt="immagine" src="https://github.com/user-attachments/assets/0e681f9f-4f88-4de8-a784-e132d125b261" />









# 🔐 How to Enable SSH Service on a New Linux Computer

This guide explains how to **install, enable, and verify the SSH service** on a Linux system. SSH (Secure Shell) allows you to access your computer remotely via the terminal.

---

## 📦 1. Install OpenSSH Server

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install openssh-server

Fedora

sudo dnf install openssh-server

Arch Linux / Manjaro

sudo pacman -S openssh

⚙️ 2. Enable and Start the SSH Service

To enable the service at startup and start it immediately:

sudo systemctl enable ssh
sudo systemctl start ssh

    ℹ️ On some systems, the service may be called sshd instead of ssh. If so, use:

    sudo systemctl enable sshd
    sudo systemctl start sshd

🔍 3. Check if SSH is Running

Verify that the service is active:

sudo systemctl status ssh

Expected output:

Active: active (running)

🧪 4. Test SSH Connection

From another computer on the same network (or remotely, if firewall/port forwarding is configured), connect using:

ssh username@ip_address

Example:

ssh mario@192.168.1.100

You may be asked to confirm the server's fingerprint the first time.
🔥 5. (Optional) Allow SSH Through the Firewall

If you're using ufw (default on Ubuntu), run:

sudo ufw allow ssh
sudo ufw reload

