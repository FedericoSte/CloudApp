# CloudApp

<img width="1024" height="1024" alt="icon - Copia" src="https://github.com/user-attachments/assets/b0907fa0-ddb9-4e24-91a5-8a73ea2d13a5" />



**CloudApp for Windows: File Management Using the SSH Protocol.**
**CloudApp** was originally created as a personal project to meet specific needs, but I decided to release it because I found it valuable in various contexts. Written in Python as a single file, CloudApp is designed to simplify conversion to an .exe file using the [PyInstaller Module](https://pyinstaller.org/en/stable/installation.html).  
**The application leverages [SSH](https://www.ssh.com/academy/ssh/protocol) and [SFTP](https://www.ssh.com/academy/ssh/sftp-ssh-file-transfer-protocol) protocols to communicate with the server (a Linux server is required) and provides traditional file manager functionalities such as upload, download, copy, and paste...**  
It also employs multithreading to handle multiple execution flows concurrently.  




<img width="394" height="385" alt="immagine" src="https://github.com/user-attachments/assets/eb5d9942-af82-4e2b-a0df-ca9b45c82a26" /> <img width="336" height="171" alt="immagine" src="https://github.com/user-attachments/assets/ae3c7e12-a04b-4f53-a969-73a88a5ae660" />

<img width="991" height="838" alt="immagine" src="https://github.com/user-attachments/assets/331af5e9-6459-40b3-9536-20e536c3fe95" />



# Uses
**CloudApp can be used to exchange and manage files on ANY Linux Computer**, including devices like Raspberry Pi, as well as virtual machines.  
**CloudApp is particularly useful for repurposing an old computer and transforming it into a cloud server, which can potentially be accessed from anywhere in the world.  
While the server is initially exposed only within the local network**, there are several solutions you can implement to access your server remotely. Personally, I have found that the most secure and stable method is using a VPN. You can set up a VPN through your preferred provider, connect your server to that VPN, and you're good to go. I personally use  [TailScale VPN](https://tailscale.com/).  
Below is a short tutorial on how to install TailScale on your Linux server and any other device.  

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




