import sys
import os
import paramiko
import mimetypes
import tempfile
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QMessageBox,
    QInputDialog, QLineEdit, QFileDialog, QDialog, QTextEdit, QLabel, QMenu, QProgressBar, QListWidgetItem, QDesktopWidget, QComboBox
)
import sys
import os
import paramiko
import mimetypes
import tempfile
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QMessageBox,
    QInputDialog, QLineEdit, QFileDialog, QDialog, QTextEdit, QLabel, QMenu, QProgressBar, QListWidgetItem
)
from PyQt5.QtGui import QPixmap, QColor, QIcon, QImage, QMouseEvent
from PyQt5.QtCore import Qt, QTimer, QSize, QThread, pyqtSignal
from stat import S_ISDIR as stat_is_dir

import cv2
import socket
import time
import subprocess
import platform






# 🔧 Configurazione del server
SSH_HOST = ""   #<----- put your server ip
SSH_PORT = 22   #<----- put your server port (type=int) usualy port 22
SSH_USER = ""   #<----- put the name of the server user 
REMOTE_DIR = "" #<----- put server remote dir 

class SSHFileManager(QWidget):
    def __init__(self):
        super().__init__()
        self.image_download_thread = None
        self.setWindowTitle("Cloud File Manager")
        self.resize(1000, 800)


        self.ping_thread = None  # Inizialmente nessun thread
        self.ping_timer = QTimer(self)  # Timer per avviare il ping ogni 60 secondi
        self.ping_timer.timeout.connect(self.start_ping_thread)  # Connessione del timeout del timer


        self.layout = QVBoxLayout()

        self.breadcrumb_bar = QLineEdit()
        self.breadcrumb_bar.setReadOnly(True)
        self.layout.addWidget(self.breadcrumb_bar)

        nav_layout = QHBoxLayout()

        self.ping_result_label = QLabel("Ping: N/A", self)
        nav_layout.addWidget(self.ping_result_label)

        self.refresh_button = QPushButton("🔄")   
        self.refresh_button.clicked.connect(self.load_remote_files)
        nav_layout.addWidget(self.refresh_button, stretch=1)

        self.back_button = QPushButton("⬅️ Torna su")
        self.back_button.clicked.connect(self.go_up_directory)
        nav_layout.addWidget(self.back_button, stretch=2)

        self.home_button = QPushButton("🏠 Casa")
        self.home_button.clicked.connect(self.go_home_directory)
        nav_layout.addWidget(self.home_button, stretch=2)
        
        self.layout.addLayout(nav_layout)


        # Crea una combo box per l'ordinamento
        self.sort_combo = QComboBox()
        self.sort_combo.addItem("Ordina per nome Crescente")
        self.sort_combo.addItem("Ordina per nome Decrescente")
        self.sort_combo.addItem("Ordina per Dimensione Crescente")
        self.sort_combo.addItem("Ordina per Dimensione Decrescente")
        self.sort_combo.addItem("Ordina per Ultima Modifica")


        # Collegala a una funzione di ordinamento
        self.sort_combo.currentIndexChanged.connect(self.load_remote_files)








        self.file_list = QListWidget()
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.open_context_menu)
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)


        # Aggiungila al layout prima della lista
        self.layout.addWidget(self.sort_combo)

        self.layout.addWidget(self.file_list)




        self.download_button = QPushButton("⬇️ Download")
        self.upload_button = QPushButton("⬆️ Upload File")
        self.upload_folder_button = QPushButton("⬆️📁 Upload Folder")
        self.shutdown_button = QPushButton("🛑 Arresta Server")
        self.shutdown_button.clicked.connect(self.shutdown_server)




        self.progress_layout = QHBoxLayout()


        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)


        self.progress_layout.addWidget(self.progress_bar)

        self.layout.addLayout(self.progress_layout)





        
        self.layout.addWidget(self.download_button)
        self.layout.addWidget(self.upload_button)
        self.layout.addWidget(self.upload_folder_button)
        self.layout.addWidget(self.shutdown_button)

        self.setLayout(self.layout)
        self.center_window()

        self.current_dir = REMOTE_DIR
        self.clipboard = None
        self.cut_mode = False

        self.connect_ssh()
        
        self.download_button.clicked.connect(self.download)
        self.upload_button.clicked.connect(self.upload_file)
        self.file_list.itemDoubleClicked.connect(self.on_item_double_click)

        self.upload_folder_button.clicked.connect(self.upload_folder)


        self.load_remote_files()

        # Avvia il timer per il ping
        self.ping_timer.start(30000)  # Ogni 30 secondi


    def center_window(self):
        """Centra la finestra sullo schermo"""
        qr = self.frameGeometry()  # geometria della finestra
        cp = QDesktopWidget().availableGeometry().center()  # centro dello schermo disponibile
        qr.moveCenter(cp)  # sposta il rettangolo al centro
        self.move(qr.topLeft())  # muovi la finestra in quella posizione


    def shutdown_server(self):
        reply = QMessageBox.question(
            self,
            "Conferma Spegnimento",
            "Sei sicuro di voler arrestare il server remoto?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                # Esegue lo shutdown remoto
                stdin, stdout, stderr = self.ssh.exec_command("sudo shutdown now")

                # Mostra messaggio e chiude l'app dopo 2 secondi
                QMessageBox.information(self, "Shutdown", "Il server è in fase di spegnimento...")
                QTimer.singleShot(2000, self.close)  # chiude l'app dopo 2 secondi
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore durante l'arresto del server: {e}")




    def connect_ssh(self):
        password, ok = QInputDialog.getText(self, "Connessione SSH", "Inserisci la password:", echo=QLineEdit.Password)
        if not ok:
            QMessageBox.warning(self, "Operazione Annullata", "Connessione SSH annullata.")
            sys.exit(0)

        loading_dialog = LoadingDialog(self)
        loading_dialog.show()

        try:
            for i in range(1, 6):
                loading_dialog.update_message(f"Tentativo di connessione al server... [N.{i}]")
                if self.ping1(SSH_HOST):
                    break

                elif i == 5:
                    QMessageBox.warning(self, "Operazione Annullata", "Impossibile raggiungere il server, potrebbe essere spento o non raggiungibile.")
                    sys.exit(0)
            
            loading_dialog.update_message("Server Trovato, tentativo di connessione SSH...")

            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER, password=password)
            self.sftp = self.ssh.open_sftp()

            loading_dialog.update_message("Connessione riuscita!")

            time.sleep(1)
            loading_dialog.close()

        except paramiko.SSHException as e:
            QMessageBox.critical(self, "Errore di connesione SSH [paramiko]", str(e))
            sys.exit(1)

        except socket.timeout as e:
            QMessageBox.critical(self, "Timeout SSH [soket]", str(e))
            sys.exit(1)

        except Exception as e:
            QMessageBox.critical(self, "Errore SSH", str(e))         
            sys.exit(1)

   

    def start_ping_thread(self):
        """Avvia il thread per eseguire il ping e calcolare la media."""
        # Avvia il thread solo quando necessario
        self.ping_thread = ThreadPingSteve("8.8.8.8")
        self.ping_thread.ping_result_signal.connect(self.print_ping_result)
        self.ping_thread.start()  # Avvia il thread

    def print_ping_result(self, media):
        """Aggiorna il risultato del ping nell'interfaccia."""
        print(f"Tempo medio di ping: {media} secondi")
        
        # Aggiorna il testo della QLabel con il tempo medio di ping
        self.ping_result_label.setText(f"Ping: {media} secondi")
        self.ping_result_label.update()  # Forza il ridisegno del layout
        QApplication.processEvents()  # Assicura che l'interfaccia si aggiorni
    


    def ping1(self, host):
        """Invia un pacchetto ping per verificare la connessione"""
        try:
            # Verifica il sistema operativo per adattare il comando di ping
            if platform.system().lower() == "windows":
                result = subprocess.run(['ping', '-n', '1', host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                result = subprocess.run(['ping', '-c', '1', host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            if result.returncode == 0:
                return True  # Server raggiungibile
            else:
                print(f"Errore durante il ping: {result.stderr.decode()}")
                return False  # Server non raggiungibile
        except Exception as e:
            print(f"Errore durante il ping: {e}")
            return False




    def ordina_nome_crescente(self, list_file):
        return sorted(list_file, key=lambda x: x[0].lower())
    
    def ordina_nome_decrescente(self, list_file):
        return sorted(list_file, key=lambda x: x[0].lower(), reverse=True)


    def ordina_dimensione_crescente(self, nome_dim):
        return [el[0] for el in sorted(nome_dim, key=lambda x: x[1])]
    
    def ordina_dimensione_decrescente(self, nome_dim):
        return [el[0] for el in sorted(nome_dim, key=lambda x: x[1], reverse=True)]

    def ordina_ultima_modifica(self, nome_mod):
        return [el[0] for el in sorted(nome_mod, key=lambda x: x[1], reverse=True)]   








    def update_image_icon(self, filename, icon):
        # Trova l'elemento nella lista che corrisponde al filename
        for index in range(self.file_list.count()):
            item = self.file_list.item(index)
            if item.text() == filename:
                item.setIcon(icon)  # Aggiorna l'icona per l'elemento
                break
        QApplication.processEvents()  # Forza il ridisegno immediato dell'interfaccia




    def stop_image_thread(self):
        if self.image_download_thread and self.image_download_thread.isRunning():
            self.image_download_thread.stop()       # imposta _is_running = False
            self.image_download_thread.wait()       # aspetta che finisca
            self.image_download_thread = None





    def calcola_dimensione(self, remote_path):
        attr = self.sftp.stat(remote_path)

        def recursive_folder_info(path):
            total_size = 0
            total_files = 0
            try:
                for item in self.sftp.listdir(path):
                    full_path = f"{path}/{item}"
                    try:
                        stat = self.sftp.stat(full_path)
                        if stat_is_dir(stat.st_mode):
                            sub_size, sub_files = recursive_folder_info(full_path)
                            total_size += sub_size
                            total_files += sub_files
                        else:
                            total_size += stat.st_size
                            total_files += 1
                    except Exception as e:
                        print(f"Errore leggendo {full_path}: {e}")
            except Exception as e:
                print(f"Errore leggendo cartella {path}: {e}")
            return total_size, total_files

        try:
            if stat_is_dir(attr.st_mode):
                byte, file_count = recursive_folder_info(remote_path)
            else:
                byte = attr.st_size
                file_count = 1

            if byte >= 1024**3:
                size_str = f"{round(byte / (1024**3), 2)} GB"
            elif byte >= 1024**2:
                size_str = f"{round(byte / (1024**2), 2)} MB"
            elif byte >= 1024:
                size_str = f"{round(byte / 1024, 2)} kB"
            else:
                size_str = f"{byte} byte"

            return byte, f"{size_str} — {file_count} file"
        except Exception as e:
            return f"Errore nel calcolo: {e}"


    def load_remote_files(self):
        self.stop_image_thread()  # ✅ interruzione sicura

        self.file_list.clear()
        self.breadcrumb_bar.setText(self.current_dir)

        try:
            self.sftp.chdir(self.current_dir)  # solo dopo aver fermato il thread!
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nel cambio directory: {e}")
            return

        def resource_path(relative_path):
            """Restituisce il percorso corretto sia durante l'esecuzione da script che da .exe"""
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            return os.path.join(base_path, relative_path)


        image_list = []



        index = self.sort_combo.currentIndex()
        
        
        if index == 0:  # Ordina per nome crescente
            sorted_list_file = self.ordina_nome_crescente(self.sftp.listdir())

        elif index == 1:  # Ordina per nome decrescente
            sorted_list_file = self.ordina_nome_decrescente(self.sftp.listdir())

        elif index == 2:  # Ordina per dimensione crescente

            nome_dim = [(nome_file, self.calcola_dimensione(f"{self.current_dir}/{nome_file}")[0]) for nome_file in self.sftp.listdir()]
            sorted_list_file = self.ordina_dimensione_crescente(nome_dim)


        elif index == 3:  # Ordina per dimensione crescente
            nome_dim = [(nome_file, self.calcola_dimensione(f"{self.current_dir}/{nome_file}")[0]) for nome_file in self.sftp.listdir()]
            sorted_list_file = self.ordina_dimensione_decrescente(nome_dim)


        elif index == 4:  # Ordina ultima modifica
            nome_mod = [(el.filename, el.st_mtime) for el in self.sftp.listdir_attr()]
            sorted_list_file = self.ordina_ultima_modifica(nome_mod)


        else:
            sorted_list_file = self.sftp.listdir()



       

        self.file_list.clear()
        for filename in sorted_list_file:
            remote_path = f"{self.current_dir}/{filename}"
            icon = QIcon(resource_path("immagini/icon_unknow.jpg")) # fallback predefinito
            user_role = "other"

            try:
                attr = self.sftp.stat(remote_path)
                is_dir = stat_is_dir(attr.st_mode)

                if is_dir:
                    icon = QIcon(resource_path("immagini/icon_folder.jpg"))
                    user_role = "folder"
                else:
                    file_type, _ = mimetypes.guess_type(filename)

                    if file_type:
                        if file_type.startswith("image"):
                            image_list.append(filename)
                            icon = QIcon(resource_path("immagini/icon_image.jpg"))
                            user_role = "image"                            


                            """
                            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
                                self.sftp.get(remote_path, tmp.name)

                                pixmap = QPixmap(tmp.name).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                                icon = QIcon(pixmap)
                                user_role = "image"
                            """
                       
                        elif file_type.startswith("video"):
                            icon = QIcon("immagini/icon_video.png")
                            user_role = "video"
                           
                           
                               
                        elif file_type.startswith("audio"):
                            icon = QIcon(resource_path("immagini/icon_audio.jpg"))
                            user_role = "audio"
                        else:
                            icon = QIcon(resource_path("immagini/icon_file.jpg"))
                            user_role = "text"

            except Exception as e:
                print(f"Errore nel caricare {filename}: {e}")

            item = QListWidgetItem(icon, filename)
            item.setData(Qt.UserRole, user_role)
            item.setSizeHint(QSize(60, 60))  # 👈 Imposta dimensione uniforme per ogni item
            self.file_list.addItem(item)


        self.file_list.setIconSize(QSize(48, 48))
        self.file_list.setSpacing(8)

        self.file_list.setStyleSheet("""
            QListWidget::item {
                border: 1px solid #aaa;
                padding: 6px 12px;
                margin: 1px;
                border-radius: 0px;
                height: 5px; /* altezza uniforme */
                font-size: 14px;
                background-color: white;
                color: black;
            }

            QListWidget::item:selected {
                background-color: #e6f7ff;
                color: black;
            }

            /* Colori specifici per tipo — se vuoi usare questi, servirebbe QSS dinamico, quindi meglio gestirli via codice */
            """)
        # Ferma thread precedente se ancora attivo
        self.stop_image_thread()

        # Crea e salva il nuovo thread
        self.image_download_thread = ImageDownloadThread(self.sftp, self.current_dir, image_list)
        self.image_download_thread.icon_updated.connect(self.update_image_icon)
        self.image_download_thread.start()



    def go_up_directory(self):
        parent = os.path.dirname(self.current_dir.rstrip("/"))
        if parent:
            self.current_dir = parent
            self.load_remote_files()

    def go_home_directory(self):
        self.current_dir = REMOTE_DIR
        self.load_remote_files()



    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_operation_finished(self, message):
        self.progress_bar.setVisible(False)
        QMessageBox.information(self, "Upload cartella", message)


    
    def on_operation_finished(self, message):
        self.progress_bar.setVisible(False)
        QMessageBox.information(self, "Upload", message)
        self.load_remote_files()




    
    def download(self):
        selected_item = self.file_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Attenzione", "Seleziona un file da scaricare.")
            return

        filename = selected_item.text()
        remote_path = f"{self.current_dir}/{filename}"
        attr = self.sftp.stat(remote_path)
        is_dir = stat_is_dir(attr.st_mode)

        # Scegli la destinazione
        local_folder = QFileDialog.getExistingDirectory(self, "Seleziona cartella di destinazione")
        if not local_folder:
            return

        local_path = os.path.join(local_folder, filename)

        # Mostra la barra
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)

        if is_dir:
            self.download_thread = FolderBatchDownloadThread(self.sftp, remote_path, local_path)
        else:
            self.download_thread = FileBatchDownloadThread(self.sftp, remote_path, local_path)


        self.current_thread = self.download_thread

        self.download_thread.progress_updated.connect(self.update_progress)
        self.download_thread.download_finished.connect(self.on_operation_finished)
        self.download_thread.start()




    def upload_file(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Seleziona uno o più file da caricare")
        if file_paths:
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)
  

            # Crea il thread e lo salva come riferimento attivo
            self.upload_thread = FileBatchUploadThread(self.sftp, self.current_dir, file_paths)
            self.current_thread = self.upload_thread

            self.upload_thread.progress_updated.connect(self.update_progress)
            self.upload_thread.upload_finished.connect(self.on_operation_finished)
            self.upload_thread.start()









    def upload_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Seleziona una cartella da caricare")
        if not folder_path:
            return

        folder_name = os.path.basename(folder_path)
        remote_path = f"{self.current_dir}/{folder_name}"

        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)

        
 
        # Avvia il thread per l'upload della cartella
        self.upload_thread = FolderBatchUploadThread(self.sftp, folder_path, remote_path)

        self.current_thread = self.upload_thread

        self.upload_thread.progress_updated.connect(self.update_progress)
        self.upload_thread.upload_finished.connect(self.on_operation_finished)
        self.upload_thread.start()


    def open_context_menu(self, position):
        menu = QMenu()
        copy_action = menu.addAction("Copia")
        paste_action = menu.addAction("Incolla")
        cut_action = menu.addAction("Taglia")
        rename_action = menu.addAction("Rinomina")
        mkdir_action = menu.addAction("Crea Cartella")
        properties_action = menu.addAction("Proprietà")
        delete_action = menu.addAction("Elimina")

        action = menu.exec_(self.file_list.viewport().mapToGlobal(position))
        selected_item = self.file_list.currentItem()

        


        
        if action == copy_action and selected_item:
            self.clipboard = f"{self.current_dir}/{selected_item.text()}"
            self.cut_mode = False

        elif action == cut_action and selected_item:
            self.clipboard = f"{self.current_dir}/{selected_item.text()}"
            self.cut_mode = True

        elif action == paste_action and self.clipboard:
            src = self.clipboard
            base_name = os.path.basename(src)
            dst = f"{self.current_dir}/{base_name}"

            try:
                if self.cut_mode:
                    # TAGLIA → rename (mv)
                    self.sftp.rename(src, dst)
                else:
                    # COPIA → duplicazione
                    with self.sftp.open(src, 'rb') as f_src:
                        with self.sftp.open(dst, 'wb') as f_dst:
                            while True:
                                data = f_src.read(32768)
                                if not data:
                                    break
                                f_dst.write(data)

                self.load_remote_files()
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Incolla fallita: {e}")
            finally:
                self.clipboard = None
                self.cut_mode = False
        
        elif action == mkdir_action:
            folder_name, ok = QInputDialog.getText(self, "Nuova Cartella", "Nome cartella:")
            if ok and folder_name:
                self.sftp.mkdir(f"{self.current_dir}/{folder_name}")
                self.load_remote_files()
        elif action == rename_action and selected_item:
            old_name = selected_item.text()
            new_name, ok = QInputDialog.getText(self, "Rinomina", "Nuovo nome:", text=old_name)
            if ok and new_name and new_name != old_name:
                self.sftp.rename(f"{self.current_dir}/{old_name}", f"{self.current_dir}/{new_name}")
                self.load_remote_files()
        elif action == properties_action and selected_item:
            filename = selected_item.text()
            remote_path = f"{self.current_dir}/{filename}"
            try:
                
                attr = self.sftp.stat(remote_path) 
                mtime = datetime.fromtimestamp(attr.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                file_type = "Cartella" if stat_is_dir(attr.st_mode) else "File"
                msg = QDialog(self)
                msg.setWindowTitle("Proprietà")
                layout = QVBoxLayout()
                layout.addWidget(QLabel(f"Nome: {filename}"))
                layout.addWidget(QLabel(f"Tipo: {file_type}"))




                
                layout.addWidget(QLabel(f"Dimensione: {self.calcola_dimensione(remote_path)[1]}"))
                layout.addWidget(QLabel(f"Ultima modifica: {mtime}"))
                layout.addWidget(QLabel(f"Percorso: {remote_path}"))
                msg.setLayout(layout)
                msg.exec_()
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore durante il recupero delle proprietà: {e}")
        elif action == delete_action and selected_item:
            filename = selected_item.text()
            remote_path = f"{self.current_dir}/{filename}"
            reply = QMessageBox.question(self, "Conferma Eliminazione", f"Vuoi eliminare '{filename}'?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    attr = self.sftp.stat(remote_path)
                    if stat_is_dir(attr.st_mode):
                        self._remove_directory_recursive(remote_path)
                    else:
                        self.sftp.remove(remote_path)
                    self.load_remote_files()
                except Exception as e:
                    QMessageBox.critical(self, "Errore", f"Errore durante l'eliminazione: {e}")

    def _remove_directory_recursive(self, path):
        for item in self.sftp.listdir(path):
            full_path = f"{path}/{item}"
            if stat_is_dir(self.sftp.stat(full_path).st_mode):
                self._remove_directory_recursive(full_path)
            else:
                self.sftp.remove(full_path)
        self.sftp.rmdir(path)

    def on_item_double_click(self, item):
        filename = item.text()
        remote_path = f"{self.current_dir}/{filename}"
        try:
            attr = self.sftp.stat(remote_path)
            if stat_is_dir(attr.st_mode):
                self.sftp.chdir(remote_path)
                self.current_dir = remote_path
                self.load_remote_files()
            else:
                file_type, _ = mimetypes.guess_type(filename)
                if file_type and file_type.startswith("text"):
                    with self.sftp.open(remote_path, "r") as f:
                        content = f.read().decode("utf-8")
                    self.show_text_content(filename, content)
                elif file_type and file_type.startswith("image"):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
                        self.sftp.get(remote_path, tmp.name)
                        self.show_image_content(filename, tmp.name)
                elif file_type and file_type.startswith("video"):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
                        self.sftp.get(remote_path, tmp.name)
                        self.show_video_preview(filename, tmp.name)

                else:
                    QMessageBox.information(self, "Non supportato", "Tipo di file non supportato per l'apertura.")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il doppio clic: {e}")

    def show_text_content(self, title, content):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Contenuto di {title}")
        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setText(content)
        layout.addWidget(text_edit)
        dialog.setLayout(layout)
        dialog.resize(600, 400)
        dialog.exec_()

    def show_image_content(self, title, filepath):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Anteprima Immagine - {title}")
        layout = QVBoxLayout()
        label = QLabel()
        pixmap = QPixmap(filepath)
        label.setPixmap(pixmap.scaledToWidth(600))
        layout.addWidget(label)
        dialog.setLayout(layout)
        dialog.exec_()

    def show_video_preview(self, title, filepath):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Anteprima Video - {title}")
        layout = QVBoxLayout()

        label = QLabel()
        layout.addWidget(label)
        dialog.setLayout(layout)
        dialog.resize(640, 480)

        cap = cv2.VideoCapture(filepath)

        def update_frame():
            ret, frame = cap.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(image)
                label.setPixmap(pixmap.scaled(label.size(), Qt.KeepAspectRatio))
            else:
                cap.release()
                timer.stop()

        timer = QTimer(self)
        timer.timeout.connect(update_frame)
        timer.start(33)  # ~30 fps

        dialog.exec_()
        cap.release()



    def closeEvent(self, event):
        self.sftp.close()
        self.ssh.close()
        event.accept()





class ImageDownloadThread(QThread):
    # Segnale per aggiornare l'icona di un singolo file
    icon_updated = pyqtSignal(str, QIcon)

    def __init__(self, sftp, remote_dir, image_list):
        super().__init__()
        self.sftp = sftp
        self.remote_dir = remote_dir
        self.image_list = image_list  # Lista di file da caricare

    def run(self):
        # Processa le immagini una alla volta
        for filename in self.image_list:
            if not self._is_running:
                break  # Interrompe pulitamente

            remote_path = f"{self.remote_dir}/{filename}"

            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
                    self.sftp.get(remote_path, tmp.name)

                    # Crea una pixmap per l'icona
                    pixmap = QPixmap(tmp.name).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    icon = QIcon(pixmap)

                    # Invia un segnale per aggiornare l'icona dell'elemento corrispondente
                    self.icon_updated.emit(filename, icon)

            except Exception as e:
                print(f"Errore nel download dell'immagine {filename}: {e}")









class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Caricamento in corso...")
        self.setModal(True)  # Rende la finestra modale (bloccante)
        self.setFixedSize(400, 200)

        # Layout per la finestra di caricamento
        layout = QVBoxLayout(self)

        self.label = QLabel("Attendere prego...", self)

        layout.addWidget(self.label)


    def update_message(self, message):
        """Aggiorna il messaggio mostrato nella finestra di caricamento"""
        self.label.setText(message)
        QApplication.processEvents()  # Assicura che l'interfaccia si aggiorni

    def mousePressEvent(self, event: QMouseEvent):
        """Ignora qualsiasi clic del mouse per evitare l'interazione durante il caricamento"""
        event.ignore()  # Ignora tutti i clic

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Ignora il rilascio del mouse"""
        event.ignore()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Ignora il movimento del mouse"""
        event.ignore()







class ImageDownloadThread(QThread):
    icon_updated = pyqtSignal(str, QIcon)

    def __init__(self, sftp, remote_dir, image_list):
        super().__init__()
        self.sftp = sftp
        self.remote_dir = remote_dir
        self.image_list = image_list
        self._is_running = True  # ✅ flag per interrompere

    def stop(self):
        self._is_running = False  # ✅ metodo per segnalare stop

    def run(self):
        for filename in self.image_list:
            if not self._is_running:
                break  # ✅ interrompe il thread se richiesto

            remote_path = f"{self.remote_dir}/{filename}"

            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
                    self.sftp.get(remote_path, tmp.name)

                    pixmap = QPixmap(tmp.name).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    icon = QIcon(pixmap)

                    self.icon_updated.emit(filename, icon)
            except Exception as e:
                print(f"Errore nel download dell'immagine {filename}: {e}")


#-- file upload
class FileBatchUploadThread(QThread):
    progress_updated = pyqtSignal(int)
    upload_finished = pyqtSignal(str)

    def __init__(self, sftp, remote_dir, local_file_paths):
        super().__init__()
        self.sftp = sftp
        self.remote_dir = remote_dir
        self.local_file_paths = local_file_paths
        self._is_running = True
        self.total_size = 0
        self.uploaded_size = 0

    def stop(self):
        self._is_running = False

    def run(self):
        try:
            self.total_size = sum(os.path.getsize(path) for path in self.local_file_paths)

            for path in self.local_file_paths:
                if not self._is_running:
                    break  # interrompe in sicurezza

                filename = os.path.basename(path)
                remote_path = f"{self.remote_dir}/{filename}"

                last_transferred = 0  # serve per sapere quanto aggiornare

                def callback(transferred, total, path=path):
                    if not self._is_running:
                        return  # evita crash, ma non blocca subito il trasferimento

                    percent = int((self.uploaded_size + transferred) / self.total_size * 100)
                    self.progress_updated.emit(percent)

                self.sftp.put(path, remote_path, callback=callback)
                self.uploaded_size += os.path.getsize(path)

            if self._is_running:
                self.upload_finished.emit("Upload file completato.")
            else:
                self.upload_finished.emit("Upload interrotto.")
        except Exception as e:
            self.upload_finished.emit(f"Errore durante l'upload: {e}")



#-- folder upload --
class FolderBatchUploadThread(QThread):
    progress_updated = pyqtSignal(int)  # percentuale
    upload_finished = pyqtSignal(str)

    def __init__(self, sftp, local_dir, remote_dir):
        super().__init__()
        self.sftp = sftp
        self.local_dir = local_dir
        self.remote_dir = remote_dir
        self._is_running = True

        self.local_files = []
        self.total_size = 0
        self.uploaded_size = 0

    def stop(self):
        self._is_running = False

    def scan_files(self):
        """Scandisce ricorsivamente i file e calcola la dimensione totale"""
        for root, dirs, files in os.walk(self.local_dir):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, self.local_dir)
                remote_path = os.path.join(self.remote_dir, relative_path).replace("\\", "/")
                self.local_files.append((local_path, remote_path))
                self.total_size += os.path.getsize(local_path)

    def run(self):
        try:
            self.scan_files()

            for local_path, remote_path in self.local_files:
                if not self._is_running:
                    break

                # Crea le directory intermedie se non esistono
                remote_folder = os.path.dirname(remote_path)
                self.ensure_remote_dirs(remote_folder)

                def callback(transferred, total, local_path=local_path):
                    if not self._is_running:
                        raise Exception("Upload interrotto manualmente")
                    progress = int((self.uploaded_size + transferred) / self.total_size * 100)
                    self.progress_updated.emit(progress)

                self.sftp.put(local_path, remote_path, callback=callback)
                self.uploaded_size += os.path.getsize(local_path)

            self.upload_finished.emit("Cartella caricata con successo.")
        except Exception as e:
            self.upload_finished.emit(f"Errore durante l'upload: {e}")

    def ensure_remote_dirs(self, remote_path):
        """Crea directory remote se mancano"""
        folders = remote_path.strip("/").split("/")
        path = ""
        for folder in folders:
            path += "/" + folder
            try:
                self.sftp.stat(path)
            except IOError:
                try:
                    self.sftp.mkdir(path)
                except Exception as e:
                    print(f"Errore nella creazione di {path}: {e}")





# --- file download ---
class FileBatchDownloadThread(QThread):
    progress_updated = pyqtSignal(int)
    download_finished = pyqtSignal(str)

    def __init__(self, sftp, remote_path, local_path):
        super().__init__()
        self.sftp = sftp
        self.remote_path = remote_path
        self.local_path = local_path



    def run(self):
        try:
  
            file_size = self.sftp.stat(self.remote_path).st_size
            with open(self.local_path, 'wb') as f:
                def callback(transferred, total):
                    percent = int((transferred / total) * 100)
                    self.progress_updated.emit(percent)
                self.sftp.get(self.remote_path, self.local_path, callback=callback)
            self.download_finished.emit(f"Download completato: {self.local_path}")
        except Exception as e:
            self.download_finished.emit(f"Errore durante il download: {e}")


# --- folder download  ---
class FolderBatchDownloadThread(QThread):
    progress_updated = pyqtSignal(int)
    download_finished = pyqtSignal(str)

    def __init__(self, sftp, remote_dir, local_dir):
        super().__init__()
        self.sftp = sftp
        self.remote_dir = remote_dir
        self.local_dir = local_dir
        self._is_running = True
        self.remote_files = []
        self.total_size = 0
        self.downloaded_size = 0


    def stop(self):
        self._is_running = False

    def scan_files(self):
        for entry in self.sftp.listdir_attr(self.remote_dir):
            remote_path = f"{self.remote_dir}/{entry.filename}"
            local_path = os.path.join(self.local_dir, entry.filename)
            if stat_is_dir(entry.st_mode):
                thread = FolderBatchDownloadThread(self.sftp, remote_path, local_path)
                thread.run()  # ricorsivo
            else:
                self.remote_files.append((remote_path, local_path))
                self.total_size += entry.st_size

    def run(self):
        try:
            if not os.path.exists(self.local_dir):
                os.makedirs(self.local_dir)

            self.scan_files()
            for remote_path, local_path in self.remote_files:

                with open(local_path, 'wb') as f:
                    def callback(transferred, total):
                        percent = int((self.downloaded_size + transferred) / self.total_size * 100)
                        self.progress_updated.emit(percent)
                    self.sftp.get(remote_path, local_path, callback=callback)
                    self.downloaded_size += os.path.getsize(local_path)

            self.download_finished.emit(f"Download completato: {self.local_dir}")
        except Exception as e:
            self.download_finished.emit(f"Errore durante il download della cartella: {e}")





import subprocess
import time
import platform
import sys
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox

class ThreadPingSteve(QThread):
    ping_result_signal = pyqtSignal(float)

    def __init__(self, host, n=4, parent=None):
        super().__init__(parent)
        self.host = host
        self.n = n

    def run(self):
        """Esegui il ping una sola volta."""
        media = self.ping()
        self.ping_result_signal.emit(media)

    def ping(self):
        """Invia un pacchetto ping e calcola la media dei tempi di risposta."""
        times = []
        ricevuti = 0
        error = 0

        # Esegui il ping per il numero di pacchetti specificato
        for i in range(self.n + 1):
            try:
                if error >= 3:
                    print("3 pacchetti consecutivi persi!")
                    QMessageBox.warning(self, "Connessione Interrotta", "3 Pacchetti ping persi.")
                    sys.exit(0)
                
                time_start = time.time()

                if platform.system().lower() == "windows":
                    result = subprocess.Popen(
                        ['ping', '-n', '1', self.host],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW  # Nasconde la finestra del terminale su Windows
                    )
                else:
                    result = subprocess.Popen(
                        ['ping', '-c', '1', self.host],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )

                # Leggi l'output e gli errori
                stdout, stderr = result.communicate()

                # Verifica che il codice di ritorno sia 0 (successo)
                if result.returncode == 0:
                    # Misura il tempo e aggiungi alla lista
                    times.append(round(time.time() - time_start, 3))
                    ricevuti += 1
                    error = 0
                else:
                    print(f"Errore durante il ping del pacchetto {i+1}: {stderr.decode()}")
                    error += 1

            except Exception as e:
                print(f"Errore durante il ping: {e}")
                return False

        # Salta il primo pacchetto (quello che di solito è utilizzato per inizializzare)
        if len(times) > 1:
            return round(sum(times[1:]) / len(times[1:]), 3)
        return 0







if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = SSHFileManager()

    window.show()

    sys.exit(app.exec_())