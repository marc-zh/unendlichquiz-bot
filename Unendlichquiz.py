import pyautogui
from PIL import Image, ImageEnhance, ImageOps
from paddleocr import PaddleOCR
import requests

API_KEY = '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'

# Screenshot eines bestimmten Bereichs erstellen (Koordinaten und Größe definieren)
def take_screenshot(x, y, width, height, save_path='screenshot.png'):
    # Screenshot erstellen
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    # Screenshot speichern
    screenshot.save(save_path)
    print(f"Screenshot gespeichert unter {save_path}")

# Text aus dem Screenshot extrahieren mit PaddleOCR (deutsche Sprache)
def extract_text_from_image(image_path):
    # Bild in Schwarz-Weiß konvertieren und Farben umkehren
    convert_image_to_grayscale_and_invert(image_path)

    # PaddleOCR Leser initialisieren (mit deutscher Sprache)
    ocr = PaddleOCR(use_angle_cls=True, lang='de')  # Setzt die Sprache auf Deutsch

    # OCR ausführen
    result = ocr.ocr(image_path, cls=True)

    # Extrahierten Text zusammenführen
    extracted_text = ' '.join([line[1][0] for line in result[0]])

    print(f"Extrahierter Text: {extracted_text}")
    return extracted_text

# Bild in Schwarz-Weiß konvertieren und Farben umkehren
def convert_image_to_grayscale_and_invert(image_path):
    tolerance = 190
    # Bild öffnen
    image = Image.open(image_path)

    # In Schwarz-Weiß umwandeln
    grayscale_image = image.convert('L')

    # Toleranzschwellenwert definieren: alles über dem Toleranzwert wird weiß
    binary_image = grayscale_image.point(lambda p: 255 if p >= tolerance else 0)

    # Farben invertieren
    inverted_image = ImageOps.invert(binary_image)

    # Neues Bild speichern
    inverted_image.save(image_path)
    print(f"Bild mit umgekehrten Farben und Toleranz gespeichert unter {image_path}")

# Den extrahierten Text in der API suchen
def search_in_groq_ai(query):
    url = 'https://api.groq.com/openai/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    # Anweisung geändert: "Gib mir nur eine Richtige Antwort der Antwortmöglichkeiten aus, nicht mehr Text."
    query_with_instruction = query + "\nEs ist eine Frage mit meistens 4 Antwortmöglichkeiten. Immer ist nur eine Antwortmöglichkeit Richtig. Gib mir immer die Richtige Antwortmöglichkeit aus."

    data = {
        'model': 'gemma2-9b-it',
        'messages': [{'role': 'user', 'content': query_with_instruction}]
    }

    # Anfrage an Groq AI senden
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        # Gib die volle API-Antwort aus
        answer = result['choices'][0]['message']['content']
        print("Volle Antwort der API: \n", answer)
    else:
        print(f"Fehler bei der Anfrage: {response.status_code} - {response.text}")

# Hauptprogramm
if __name__ == "__main__":
    # Definiere die Position und Größe des Bereichs, den du scannen möchtest
    x = 2400  # x-Position des Screenshots
    y = 400  # y-Position des Screenshots
    width = 950  # Breite des Screenshot-Bereichs
    height = 2050  # Höhe des Screenshot-Bereichs

    # Pfad zum Speichern des Screenshots
    screenshot_path = 'screenshot.png'

    # Screenshot erstellen
    take_screenshot(x, y, width, height, screenshot_path)

    # Text aus dem Screenshot extrahieren
    extracted_text = extract_text_from_image(screenshot_path)

    # Den extrahierten Text bei der API suchen (leere Suchanfragen ignorieren)
    if extracted_text.strip():
        search_in_groq_ai(extracted_text)
    else:
        print("Kein Text erkannt.")
