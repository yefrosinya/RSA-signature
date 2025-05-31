import tkinter as tk
from .gui.rsa_signature_gui import RSASignatureGUI


def main():
    root = tk.Tk()
    app = RSASignatureGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
