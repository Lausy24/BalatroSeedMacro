import tkinter as tk
import tkinter.ttk as ttk
import time
import pyautogui
from pynput import keyboard
import threading

# --- Globale Kontrollvariablen ---
global_macro_running = False
keyboard_listener = None
main_window = None # Referenz zum Hauptfenster

# --- Globale Referenzen für die Widgets, die von Funktionen geändert werden müssen ---
# NEU: Diese Variablen werden hier deklariert
#      und später in create_gui() mit den tatsächlichen Widget-Objekten befüllt.
button0 = None
label0 = None
button_stop_gui = None
button_description = None
button1 = None


# --- Makro-Logik (läuft in einem separaten Thread) ---
def run_macro_loop():
    global global_macro_running
    print("Makro-Schleife gestartet...")
    while global_macro_running:
        print("Führe Makro-Aktion aus...")
        pyautogui.moveTo(100, 900, duration=0.1)
        pyautogui.click()
        pyautogui.moveTo(1000, 350, duration=0.1)
        pyautogui.click()
        pyautogui.moveTo(1000, 800, duration=0.1)
        pyautogui.click()
        time.sleep(3)

    print("Makro-Schleife beendet.")
    # Stelle sicher, dass der Button-Text auch zurückgesetzt wird, wenn das Makro sich selbst beendet
    if main_window: # Überprüfe, ob das Hauptfenster noch existiert
        main_window.after(0, lambda: button0.configure(text="Start Macro"))


# --- Keyboard Listener Callback (läuft im pynput-eigenen Thread) ---
def on_press(key):
    global global_macro_running, button0 # button0 muss hier auch global sein
    try:
        if hasattr(key, 'char') and key.char == 'm':
            if global_macro_running:
                print("Taste 'm' erkannt: Stoppe Makro.")
                global_macro_running = False
                if main_window: # Überprüfe, ob das Hauptfenster noch existiert
                    main_window.after(0, lambda: button0.configure(text="Start Macro"))
    except AttributeError:
        pass

# --- Tkinter Button-Befehle ---
def macro_start():
    global global_macro_running, keyboard_listener, button0 # button0 muss hier auch global sein
    if not global_macro_running:
        global_macro_running = True
        if button0: # Sicherstellen, dass button0 bereits initialisiert ist
            button0.configure(text="Start Macro (Aktiv)")
        print("Start-Signal für Makro gesendet.")

        macro_thread = threading.Thread(target=run_macro_loop)
        macro_thread.daemon = True
        macro_thread.start()

        if keyboard_listener is None or not keyboard_listener.is_alive():
            keyboard_listener = keyboard.Listener(on_press=on_press)
            keyboard_listener.daemon = True
            keyboard_listener.start()
            print("Keyboard-Listener gestartet.")
    else:
        print("Makro läuft bereits.")

def macro_stop_gui():
    global global_macro_running, button0 # button0 muss hier auch global sein
    if global_macro_running:
        global_macro_running = False
        if button0: # Sicherstellen, dass button0 bereits initialisiert ist
            button0.configure(text="Start Macro")
        print("Stopp-Signal für Makro gesendet (via GUI).")
    else:
        print("Makro war nicht aktiv.")

def open_description_window():
    """Öffnet ein neues Fenster für die Beschreibung oder Einstellungen."""
    global main_window # main_window ist schon global, aber gute Praxis es hier zu erwähnen

    if main_window is None:
        print("Hauptfenster nicht initialisiert. Kann kein Beschreibungsfenster öffnen.")
        return

    description_window = tk.Toplevel(main_window)
    description_window.title("Macro Description")
    description_window.geometry("450x300")
    description_window.transient(main_window)
    description_window.grab_set()

    label_desc = tk.Label(description_window, text="Infos about the Macro (Set Game Speed to 4!):\n\n"
                                                 "- Press 'Start Macro' to activate.\n"
                                                 "- Press 'Stop Macro (GUI)' or 'm' to stop.\n"
                                                 "- Macro = Rolling new Tags for a good Seed.",
                                                 justify=tk.LEFT, wraplength=400)
    label_desc.pack(padx=20, pady=20)

    close_desc_button = ttk.Button(description_window, text="Schließen", command=description_window.destroy)
    close_desc_button.pack(pady=10)

    description_window.lift()
    description_window.focus_force()
    description_window.wait_window(description_window)

# --- Tkinter GUI Setup ---
def create_gui():
    global main_window, button0, label0, button_stop_gui, button_description, button1 # WICHTIG: Widgets hier global machen!

    main_window = tk.Tk()
    main_window.geometry("350x350")
    main_window.resizable(False, False)
    main_window.title("Balatro Macro")

    label0 = tk.Label(main_window, text="Balatro Macro")
    label0.pack(pady=10)

    button0 = ttk.Button(main_window, text="Start Macro", command=macro_start)
    button0.pack(padx=5, pady=10)

    button_stop_gui = ttk.Button(main_window, text="Stop Macro (GUI)", command=macro_stop_gui)
    button_stop_gui.pack(padx=5, pady=5)

    button_description = ttk.Button(main_window, text="Macro-description", command=open_description_window)
    button_description.pack(padx=5, pady=15)

    button1 = ttk.Button(main_window, text="Exit", command=main_window.destroy)
    button1.pack(padx=5, pady=10)

    main_window.mainloop()

    if keyboard_listener is not None and keyboard_listener.is_alive():
        keyboard_listener.stop()
        print("Keyboard-Listener beendet.")

if __name__ == "__main__":
    create_gui()