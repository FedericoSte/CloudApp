# CloudApp
**Cloud App for Windows based on ssh protocol.**

**Cloud App** was born as a project for personal use and needs, but I decided to publish it because I found it useful in different contexts.  
CloudApp is written in python in a single file, to facilitate its conversion to .exe via the [PyInstaller module](https://pyinstaller.org/en/stable/installation.html).  
**The application is based on the [ssh](https://www.ssh.com/academy/ssh/protocol) and [sftp](https://www.ssh.com/academy/ssh/sftp-ssh-file-transfer-protocol) protocols to communicate with the server (a Linux server is required) to provide the classic services of a File Manager such as upload, downlad, copy, paste...**  
The application uses multithreding to manage different execution flows.







<img width="395" height="388" alt="immagine" src="https://github.com/user-attachments/assets/d850251d-3d64-448a-9ee1-c04cae08f5dc" /> <img width="336" height="171" alt="immagine" src="https://github.com/user-attachments/assets/1645439c-4a18-4def-ba29-2c627711a338" />

<img width="996" height="837" alt="immagine" src="https://github.com/user-attachments/assets/fae955b3-7b87-4199-87a0-1495d849b743" />



# Uses
You can use **CloudApp to exchange and manage files on any Linux computer**, such as Raspberry Pi, but also virtual machines.  
**CloudApp is very useful for repurposing an old computer and turning it into a cloud server, potentially accessible from around the world.**  
**Obviously, the server is initially exposed only within the local network**, but you can implement various solutions to reach your server from anywhere.  
Personally, I found the most secure and stable solution to be using a VPN.  
Create your VPN through your preferred provider, connect your server to that VPN, and you're done.  
I personally use [TailScale VPN](https://tailscale.com/). Below is a short tutorial on how to install TailScale on your Linux server and any other device.

Tutorial TailScale coming soon...






# How to Enable SSH Service on a New Linux Computer.  
**To use cloudApp, the Linux server must have the SSH service enable.**  
This guide explains **how to install, enable, and verify the [SSH service](https://documentation.ubuntu.com/server/how-to/security/openssh-server/index.html)** on a Linux system (your Server).

---

## 1. Install OpenSSH Server.

### Ubuntu / Debian:
```bash
sudo apt update
sudo apt install openssh-server
```

### Fedora:
```bash
sudo dnf install openssh-server
```

### Arch Linux / Manjaro:
```bash
sudo pacman -S openssh
```

## 2. Enable and Start the SSH Service.
To enable the service at startup and start it immediately:
```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

### On some systems, the service may be called sshd instead of ssh. If so, use:
```bash
sudo systemctl enable sshd
sudo systemctl start sshd
```

## 3. Check if SSH is Running.
Verify that the service is active:

```bash
sudo systemctl status ssh
```
Expected output:
```
Active: active (running)
```

## 4. Test SSH Connection.
From another computer on the same network, connect using:
```
ssh username@ip_address
```

### Example:
```
ssh mario@192.168.1.100
```
You may be asked to confirm the server's fingerprint the first time.

## 5. (Optional) Allow SSH Through the Firewall.

If you're using ufw (default on Ubuntu), run:
```bash
sudo ufw allow ssh
sudo ufw reload
```

**Now simply with the ip address of your Linux computer you will be able to use CloudApp.exe.**



# manually create the executable file.
**If you want to create the executable file yourself, starting directly from the Python source file (main.py), follow these instructions.
Otherwise, download the .exe file directly from this project's releases.**  
On any computer (the instructions are for a Linux operating system):


## 1. Install PyInstaller:
```bash
sudo apt update
sudo apt install pyinstaller
```

## 2. Download CloudApp.zip:
**Download the .zip file for this project and unzip it.**
The main.py file must be in the same folder as the images folder.
**Navigate to the newly unzipped folder.**
```bash
cd CloudApp
```

## 3. install dependencies:
```bash
pip3 install -r requests.txt
```
**Be careful, use a virtual environment to avoid conflicts with apt packages.**


## 4. Create the executable file:
```bash
python -m PyInstaller --onefile --noconsole --icon=immagini/icon.ico --add-data "immagini/icon_audio.png;immagini" --add-data "immagini/icon_file.png;immagini" --add-data "immagini/icon_folder.png;immagini" --add-data "immagini/icon_image.png;immagini" --add-data "immagini/icon_unknow.png;immagini" --add-data "immagini/icon_video.png;immagini" CloudApp.py
```




