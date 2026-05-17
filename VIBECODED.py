import time
#from PIL import Image
#import serial

# Konfiguration
#import serial.tools.list_ports

# Automatische oder manuelle Port-Auswahl (Passe den Port an deinen Teensy an!)
SERIAL_PORT = "COM3"  # Unter Linux/Mac z.B. '/dev/ttyACM0'
BAUDRATE = 115200
IMAGE_PATH = "C:/Users/julia/Downloads/christmas_tree.bmp"
TARGET_WIDTH = 80  # Breite der ASCII-Art (anpassen je nach Ziel)

# ASCII-Zeichenrampe von dunkel nach hell
ASCII_CHARS = "@%#*+=-:. "


def bild_zu_ascii(bild_pfad, neue_breite=100):
    try:
        # 1. Bild öffnen
        img = Image.open(bild_pfad)
    except Exception as e:
        print(f"Fehler beim Öffnen des Bildes: {e}")
        return None

    # 2. In Graustufen konvertieren ('L' Modus)
    img_gray = img.convert("L")

    # Proportionen beibehalten (ASCII-Zeichen sind höher als breit, daher Faktor 0.55)
    breite, hoehe = img_gray.size
    proportional_hoehe = int((hoehe / breite) * neue_breite * 0.55)
    img_resized = img_gray.resize((neue_breite, proportional_hoehe))

    # 3. Pixel in ASCII umrechnen
    pixel = img_resized.getdata()
    ascii_str = ""

    for i, pixel_wert in enumerate(pixel):
        # Pixelwert (0-255) auf die Länge der ASCII-Rampe abbilden
        char_index = pixel_wert * (len(ASCII_CHARS) - 1) // 255
        ascii_str += ASCII_CHARS[char_index]

        # Zeilenumbruch einfügen
        if (i + 1) % neue_breite == 0:
            ascii_str += "\n"

    return ascii_str


def sende_an_teensy(ascii_art, port, baud):
    try:
        print(f"Öffne seriellen Port {port}...")
        ser = serial.Serial(port, baud, timeout=1)
        time.sleep(2)  # Warten auf Teensy-Reset

        print("Sende ASCII-Art...")
        # Zeilenweise senden
        for zeile in ascii_art.splitlines():
            ser.write((zeile + "\n").encode("utf-8"))
            time.sleep(0.01)  # Kleine Pause, um den Puffer nicht zu überlasten

        # Steuerzeichen für "Bild fertig" senden
        ser.write(b"\0")
        print("Übertragung abgeschlossen!")
        ser.close()

    except Exception as e:
        print(f"Serieller Fehler: {e}")


if __name__ == "__main__":
    # ASCII Art generieren
    ascii_bild = bild_zu_ascii(IMAGE_PATH, TARGET_WIDTH)

    if ascii_bild:
        # Optional: Vorschau in der PC-Konsole anzeigen
        print(ascii_bild)

        # An Teensy senden
        #sende_an_teensy(ascii_bild, SERIAL_PORT, BAUDRATE)