# Google GenAI Streamlit App – Bedienungsanleitung

Diese Anwendung nutzt die Leistungsfähigkeit der Google Generative AI (GenAI), um Inhalte basierend auf Texteingaben und optional hochgeladenen Bildern zu erstellen. Sie bietet eine intuitive Benutzeroberfläche und flexible Konfigurationsmöglichkeiten.

## Inhaltsverzeichnis

1.  [Überblick](#überblick)
2.  [Erste Schritte](#erste-schritte)
    *   [Voraussetzungen](#voraussetzungen)
    *   [Installation](#installation)
    *   [Konfiguration](#konfiguration)
3.  [Benutzung der App](#benutzung-der-app)
    *   [Theme-Auswahl](#theme-auswahl)
    *   [API-Schlüssel](#api-schlüssel)
    *   [Debug-Modus](#debug-modus)
    *   [Modellauswahl](#modellauswahl)
    *   [API-Parameter](#api-parameter)
    *   [Bild-Upload](#bild-upload)
    *   [Prompt-Eingabe](#prompt-eingabe)
    *   [Generierung](#generierung)
    *   [Ergebnisse](#ergebnisse)
    *   [Bild-Download](#bild-download)
4.  [Erweiterte Konfiguration](#erweiterte-konfiguration)
    *   [Konfigurationsdateien](#konfigurationsdateien)
        *   `models.json`
        *   `prompts.json`
        *   `api_config.json`
        *   `themes.json`
    *   [Streamlit Secrets](#streamlit-secrets)
5.  [Fehlerbehebung](#fehlerbehebung)
    *   [API-Schlüssel-Validierung](#api-schlüssel-validierung)
    *   [Wiederholungsversuche (Exponential Backoff)](#wiederholungsversuche-exponential-backoff)
    *   [Bildverarbeitungsprobleme](#bildverarbeitungsprobleme)
    *   [Debug-Modus](#debug-modus-1)
6.  [Funktionsweise (für Entwickler)](#funktionsweise-für-entwickler)
    *   [Modulare Struktur](#modulare-struktur)
    *   [Caching](#caching)
    *   [Fehlerbehandlung](#fehlerbehandlung-1)
    *   [Theme-Anpassung](#theme-anpassung)
7. [Code-Dokumentation](#code-dokumentation)
    *   [Funktionen](#funktionen)

## 1. Überblick <a name="überblick"></a>

Diese Streamlit-App ermöglicht es dir, mithilfe der Google GenAI Modelle (wie z.B. Gemini) Text und Bilder zu generieren. Du kannst:

*   Einen Textprompt eingeben, der beschreibt, was generiert werden soll.
*   Optional bis zu zwei Bilder hochladen, die als zusätzliche Eingabe dienen.
*   Verschiedene Parameter des Modells anpassen (Temperatur, Top-P, Top-K, maximale Token).
*   Aus vordefinierten Prompts auswählen oder eigene erstellen.
*   Die generierten Ergebnisse (Text und/oder Bild) anzeigen und herunterladen.
*   Das Aussehen der App durch Themes anpassen.

## 2. Erste Schritte <a name="erste-schritte"></a>

### 2.1 Voraussetzungen <a name="voraussetzungen"></a>

*   Python 3.7 oder höher
*   Ein Google Cloud-Konto mit Zugriff auf die Generative Language API
*   Ein API-Schlüssel für die Generative Language API

### 2.2 Installation <a name="installation"></a>

1.  **Abhängigkeiten installieren:**

    ```bash
    pip install streamlit google-generativeai Pillow
    ```
2.  **Code herunterladen:** Kopiere den Code der `streamlit_app.py` in eine Datei auf deinem Computer.
3. **Konfigurationsordner erstellen:** Erstelle einen Ordner "config" im selben Verzeichnis in dem sich die `streamlit_app.py` befindet.

### 2.3 Konfiguration <a name="konfiguration"></a>

*   **API-Schlüssel:**
    *   **Option A (Empfohlen):**  Speichere deinen API-Schlüssel sicher in den Streamlit Secrets.  Gehe dazu in den Einstellungen deiner Streamlit Cloud-App und füge unter "Secrets" einen Eintrag mit dem Namen `GENAI_API_KEY` und deinem API-Schlüssel als Wert hinzu.
    *   **Option B (Weniger sicher):**  Gib deinen API-Schlüssel direkt in das Eingabefeld der App ein.  Beachte, dass diese Methode weniger sicher ist, da der Schlüssel im Klartext eingegeben wird.
*  **(Optional) Konfigurationsdateien:** Passe die `models.json`, `prompts.json`, `api_config.json` und `themes.json` im `config`-Ordner an, um die App weiter zu personalisieren (siehe [Erweiterte Konfiguration](#erweiterte-konfiguration)).

## 3. Benutzung der App <a name="benutzung-der-app"></a>

### 3.1 Theme-Auswahl <a name="theme-auswahl"></a>

*   Wähle ein Theme aus der Dropdown-Liste "Theme auswählen:", um das Erscheinungsbild der App anzupassen.
*   Die verfügbaren Themes werden aus der `themes.json`-Datei geladen.
*   Wenn du kein Theme auswählst, wird das Standard-Streamlit-Theme verwendet.
* Wenn du ein Theme auswählst und dieses nicht mehr verfügbar ist, wird die Seite neu geladen um die Darstellung zu aktualisieren.

### 3.2 API-Schlüssel <a name="api-schlüssel"></a>

*   **Streamlit Secrets (Empfohlen):** Aktiviere das Kontrollkästchen "API Key aus Streamlit Secrets verwenden". Stelle sicher, dass du deinen API-Schlüssel korrekt in den Streamlit Secrets gespeichert hast.
*   **Manuelle Eingabe:** Gib deinen API-Schlüssel in das Textfeld "API Key eingeben:" ein.

### 3.3 Debug-Modus <a name="debug-modus"></a>

*   Aktiviere das Kontrollkästchen "Debug-Modus aktivieren", um detailliertere Informationen und Fehlermeldungen zu erhalten. Dies ist besonders nützlich bei der Fehlersuche.

### 3.4 Modellauswahl <a name="modellauswahl"></a>

*   Wähle das gewünschte GenAI-Modell aus der Dropdown-Liste "Modell auswählen:".
*   Die verfügbaren Modelle werden aus der `models.json`-Datei geladen.

### 3.5 API-Parameter <a name="api-parameter"></a>

Passe die folgenden Parameter mit den Schiebereglern an:

*   **Temperatur:** Steuert die Zufälligkeit der Ausgabe. Höhere Werte (näher an 1.0) führen zu kreativeren, aber möglicherweise weniger kohärenten Ergebnissen.
*   **Top P:** Eine alternative Methode zur Steuerung der Zufälligkeit. Niedrigere Werte (näher an 0.0) führen zu fokussierteren Ergebnissen.
*   **Top K:** Begrenzt die Anzahl der wahrscheinlichsten Token, die bei jedem Schritt berücksichtigt werden.
*   **Maximale Output-Tokens:** Legt die maximale Länge der generierten Ausgabe fest.

### 3.6 Bild-Upload <a name="bild-upload"></a>

*   Klicke auf "Bild 1 hochladen" und "Bild 2 hochladen", um optional Bilder auszuwählen.
*   Unterstützte Formate sind PNG, JPG und JPEG.
*   Die Metadaten der hochgeladenen Bilder (Größe, Format) werden angezeigt.

### 3.7 Prompt-Eingabe <a name="prompt-eingabe"></a>

*   **Textprompt eingeben:** Gib deinen Textprompt in das Textfeld "Textprompt eingeben:" ein. Dies ist die Hauptanweisung für das Modell.
*   **Beispiel-Prompt:** Wähle optional einen vordefinierten Prompt aus der Dropdown-Liste "Oder wähle einen Beispiel-Prompt:". Die verfügbaren Prompts werden aus der `prompts.json` datei geladen.
*   **Prompt-Historie:** Die App speichert die letzten 5 eingegebenen Prompts. Du kannst sie aus der Dropdown-Liste "Wähle einen Prompt aus der Historie:" auswählen.

### 3.8 Generierung <a name="generierung"></a>

*   Klicke auf den Button "Generieren", um die Inhaltserstellung zu starten.
*   Ein Spinner zeigt an, dass die Generierung läuft.
*   Die App verwendet Wiederholungsversuche (Exponential Backoff) bei API-Fehlern.

### 3.9 Ergebnisse <a name="ergebnisse"></a>

*   Die generierten Ergebnisse (Text und/oder Bild) werden unter "Ergebnisse:" angezeigt.
*   Wenn ein Bild generiert wurde, wird es direkt in der App angezeigt.

### 3.10 Bild-Download <a name="bild-download"></a>

*   Wenn ein Bild generiert wurde, wird ein Button "Generiertes Bild herunterladen" angezeigt.
*   Klicke darauf, um das Bild als PNG-Datei herunterzuladen.

## 4. Erweiterte Konfiguration <a name="erweiterte-konfiguration"></a>

### 4.1 Konfigurationsdateien <a name="konfigurationsdateien"></a>

Die App verwendet JSON-Dateien im `config`-Ordner zur Konfiguration. Du kannst diese Dateien bearbeiten, um die App anzupassen.  **Wichtig:**  Nach Änderungen an den Konfigurationsdateien musst du die Streamlit-App neu starten.

*   #### `models.json` <a name="models.json"></a>

    Definiert die verfügbaren GenAI-Modelle.  Beispiel:

    ```json
    {
      "models": [
        "gemini-2.0-flash-exp",
        "gemini-1.5-pro-001"
      ]
    }
    ```

*   #### `prompts.json` <a name="prompts.json"></a>

    Enthält vordefinierte Prompts.  Beispiel:

    ```json
    {
      "prompts": [
        "Kombiniere beide Bilder zu einem futuristischen Stadtbild.",
        "Erstelle ein Gemälde im Stil von Van Gogh, inspiriert von den beiden Bildern."
      ]
    }
    ```

*   #### `api_config.json` <a name="api_config.json"></a>

    Enthält Standardwerte für die API-Parameter und Einstellungen für Wiederholungsversuche und Caching.  Beispiel:

    ```json
    {
      "temperature": 0.7,
      "top_p": 0.95,
      "top_k": 40,
      "max_output_tokens": 1024,
      "max_retries": 3,
      "base_wait_time": 1,
      "cache_ttl": 3600
    }
    ```

    *   `max_retries`:  Maximale Anzahl der Wiederholungsversuche bei API-Fehlern.
    *   `base_wait_time`:  Basiswartezeit in Sekunden zwischen den Versuchen.  Die Wartezeit erhöht sich exponentiell.
    *   `cache_ttl`:  Zeit in Sekunden, für die der GenAI-Client im Cache gespeichert wird.

*   #### `themes.json` <a name="themes.json"></a>
    Ermöglicht die Anpassung des Farbschemas der App. Beispiel:

    ```json
    {
        "themes": {
            "dark": {
                "background_color": "#111827",
                "text_color": "#ffffff",
                "button_color": "#3b82f6",
                "button_text_color": "#ffffff"
            },
            "light": {
                "background_color": "#ffffff",
                "text_color": "#000000",
                "button_color": "#f0f2f6",
                "button_text_color": "#000000"
            }
        }
    }
    ```

### 4.2 Streamlit Secrets <a name="streamlit-secrets"></a>

Streamlit Secrets bieten eine sichere Möglichkeit, sensible Daten wie API-Schlüssel zu speichern.  **Dies ist die empfohlene Methode zur Verwaltung deines API-Schlüssels.**

1.  Öffne die Einstellungen deiner Streamlit Cloud-App.
2.  Gehe zu "Secrets".
3.  Füge einen Eintrag hinzu:
    *   **Name:**  `GENAI_API_KEY`
    *   **Wert:**  Dein Google GenAI API-Schlüssel

## 5. Fehlerbehebung <a name="fehlerbehebung"></a>

### 5.1 API-Schlüssel-Validierung <a name="api-schlüssel-validierung"></a>

Die App validiert deinen API-Schlüssel, bevor sie eine Anfrage an die API sendet.  Wenn der Schlüssel ungültig ist, wird eine Fehlermeldung angezeigt.  Typische Fehlermeldungen und ihre Bedeutung:

*   **401 Unauthorized:**  Der API-Schlüssel ist ungültig oder fehlt.
*   **403 Forbidden:**  Dein API-Schlüssel hat keine Berechtigung für die angeforderte Ressource (z.B. das angegebene Modell).
*   **Andere Fehlermeldungen:**  Deuten auf ein allgemeines Problem mit dem API-Schlüssel oder der API-Verbindung hin.

### 5.2 Wiederholungsversuche (Exponential Backoff) <a name="wiederholungsversuche-exponential-backoff"></a>

Die App verwendet Wiederholungsversuche mit exponentiell zunehmender Wartezeit, um vorübergehende API-Fehler abzufangen.  Wenn ein API-Aufruf fehlschlägt, wird er nach einer kurzen Wartezeit wiederholt.  Die Wartezeit wird bei jedem weiteren Versuch verdoppelt.  Die maximale Anzahl der Versuche und die Basiswartezeit sind in `api_config.json` konfigurierbar.

### 5.3 Bildverarbeitungsprobleme <a name="bildverarbeitungsprobleme"></a>

*   **Ungültiges Bildformat:**  Stelle sicher, dass du Bilder in einem unterstützten Format (PNG, JPG, JPEG) hochlädst.
*   **Bild zu groß:**  Sehr große Bilder können zu Fehlern führen (DecompressionBombError).  Versuche, die Bildgröße zu reduzieren.
*   **Datei nicht gefunden:** Stelle sicher, dass die Datei existiert und der Pfad korrekt ist.

### 5.4 Debug-Modus <a name="debug-modus-1"></a>

Der Debug-Modus zeigt zusätzliche Informationen an, die bei der Fehlersuche helfen können:

*   **Eingabeinhalte:**  Zeigt den Textprompt und die verarbeiteten Bilddaten an, die an die API gesendet werden.
*   **API-Antwort:** Zeigt die vollständige Antwort der API an.

## 6. Funktionsweise (für Entwickler) <a name="funktionsweise-für-entwickler"></a>

### 6.1 Modulare Struktur <a name="modulare-struktur"></a>

Die App ist in Funktionen unterteilt, die jeweils eine bestimmte Aufgabe erfüllen. Dies verbessert die Lesbarkeit, Wartbarkeit und Testbarkeit des Codes.  Die wichtigsten Funktionen sind:

*   `load_models_from_config`, `load_prompts_from_config`, `load_api_config`, `load_themes_from_config`: Laden Konfigurationsdaten aus JSON-Dateien.
*   `get_genai_client`: Initialisiert und cached den GenAI-Client.
*   `validate_api_key`: Überprüft die Gültigkeit des API-Schlüssels.
*   `generate_content_with_retry`: Führt API-Aufrufe mit Wiederholungsversuchen durch.
*   `display_image_metadata`: Zeigt Metadaten hochgeladener Bilder an.
*   `apply_theme`: Wendet das ausgewählte Theme an.
*   `main`: Die Hauptfunktion, die den Ablauf der App steuert.

### 6.2 Caching <a name="caching"></a>

Die `get_genai_client`-Funktion verwendet `@st.cache_resource`, um den GenAI-Client zu cachen.  Dies verbessert die Performance, da der Client nicht bei jeder Anfrage neu initialisiert werden muss.  Die Cache-Gültigkeitsdauer (TTL) ist in `api_config.json` konfigurierbar.

### 6.3 Fehlerbehandlung <a name="fehlerbehandlung-1"></a>

Die App verwendet `try-except`-Blöcke, um Fehler abzufangen und benutzerfreundliche Fehlermeldungen anzuzeigen.  Spezifische Fehler wie `UnidentifiedImageError` oder `FileNotFoundError` werden behandelt, um dem Benutzer präzise Informationen zu geben.

### 6.4 Theme-Anpassung <a name="theme-anpassung"></a>
Die `apply_theme`-Funktion lädt Theme-Definitionen aus der `themes.json`-Datei und wendet sie mithilfe von CSS-Regeln auf die Streamlit-App an. Die Standard-Streamlit-Styles werden mit `!important` überschrieben, um sicherzustellen, dass die benutzerdefinierten Styles Vorrang haben.

## 7. Code-Dokumentation <a name="code-dokumentation"></a>

### 7.1 Funktionen <a name="funktionen"></a>

Im Folgenden werden die wichtigsten Funktionen der `streamlit_app.py` und ihre Parameter/Rückgabewert kurz erläutert:

*   **`load_models_from_config(config_file: str) -> list[str]`**
    *   Lädt eine Liste von Modellnamen aus einer JSON-Konfigurationsdatei.
    *   `config_file`: Der Pfad zur JSON-Datei.
    *   Gibt eine Liste von Modellnamen zurück oder eine Standardliste, wenn die Datei nicht gefunden wird oder ein Fehler auftritt.

*   **`load_prompts_from_config(config_file: str) -> list[str]`**
    *   Lädt eine Liste von Prompts aus einer JSON-Konfigurationsdatei.
    *   `config_file`: Der Pfad zur JSON-Datei.
    *   Gibt eine Liste von Prompts oder eine Standardliste (EXAMPLE\_PROMPTS\_FALLBACK) zurück, wenn die Datei nicht gefunden wird oder ein Fehler auftritt.

*   **`load_api_config(config_file: str) -> dict`**
    *   Lädt API-Konfigurationsparameter aus einer JSON-Datei.
    *   `config_file`: Der Pfad zur JSON-Datei.
    *   Gibt ein Dictionary mit den Konfigurationsparametern oder Standardwerte zurück, wenn ein Fehler auftritt.

*   **`load_themes_from_config(config_file: str) -> dict`**
    *    Lädt Theme-Definitionen aus einer JSON-Konfigurationsdatei.
    *   `config_file`: Pfad zur JSON-Datei.
    *    Gibt ein Dictionary mit den Theme-Definitionen oder ein leeres Dictionary zurück, falls die Datei nicht gefunden wird oder ein Fehler auftritt.

*   **`get_genai_client(api_key: str) -> genai.Client`**
    *   Initialisiert und cached einen Google GenAI-Client.
    *   `api_key`: Der Google GenAI API-Schlüssel.
    *   Gibt den initialisierten `genai.Client` zurück.
    *   Verwendet `@st.cache_resource` für Caching.

*   **`validate_api_key(api_key: str) -> bool`**
    *   Validiert einen API-Schlüssel durch einen Testaufruf.
    *   `api_key`: Der zu validierende API-Schlüssel.
    *   Gibt `True` zurück, wenn der Schlüssel gültig ist, andernfalls `False`.

*   **`generate_content_with_retry(client: genai.Client, model_name: str, contents: list, config: types.GenerateContentConfig, max_retries: int, base_wait_time: int) -> types.GenerateContentResponse | None`**
    *   Generiert Inhalte mit Wiederholungsversuchen (Exponential Backoff).
    *   `client`: Der initialisierte GenAI-Client.
    *   `model_name`: Der Name des zu verwendenden Modells.
    *   `contents`: Eine Liste von Eingabeinhalten (Text und/oder Bilder).
    *   `config`: Die Konfiguration für die API-Anfrage (`types.GenerateContentConfig`).
    *   `max_retries`: Die maximale Anzahl der Wiederholungsversuche.
    *   `base_wait_time`: Die Basiswartezeit zwischen den Versuchen.
    *   Gibt die API-Antwort (`types.GenerateContentResponse`) zurück, oder `None`, wenn alle Versuche fehlschlagen.

*   **`display_image_metadata(uploaded_file, image_number: int) -> None`**
    *   Zeigt Metadaten eines hochgeladenen Bildes an.
    *   `uploaded_file`: Das hochgeladene Bild (Dateiobjekt).
    *   `image_number`: Die Nummer des Bildes (zur Anzeige).

*   **`apply_theme() -> None`**
    *   Wendet das ausgewählte Theme (aus `themes.json`) auf die Streamlit-App an.

*   **`main() -> None`**
    *   Die Hauptfunktion der Streamlit-App. Steuert den gesamten Ablauf.

