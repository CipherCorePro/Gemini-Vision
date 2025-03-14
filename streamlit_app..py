import streamlit as st
from google import genai
from google.genai import types
from PIL import Image, UnidentifiedImageError, ImageFile
from io import BytesIO
import json
import re  # Für die Validierung des API-Key-Formats
import time  # Für Exponential Backoff bei Wiederholungsversuchen
import os  # Für den Zugriff auf Umgebungsvariablen

# Theming: Konfiguriere das Layout der Streamlit-App
st.set_page_config(layout="wide")

# Konfigurationsverzeichnis und -dateien
CONFIG_DIR = "config"
MODEL_CONFIG_FILE = os.path.join(CONFIG_DIR, "models.json")
PROMPT_CONFIG_FILE = os.path.join(CONFIG_DIR, "prompts.json")
API_CONFIG_FILE = os.path.join(CONFIG_DIR, "api_config.json")
THEME_CONFIG_FILE = os.path.join(CONFIG_DIR, "themes.json")

# Beispiel-Prompts als Fallback, falls keine Konfigurationsdatei gefunden wird
EXAMPLE_PROMPTS_FALLBACK = [
    "Kombiniere beide Bilder zu einem futuristischen Stadtbild.",
    "Erstelle ein Gemälde im Stil von Van Gogh, inspiriert von den beiden Bildern.",
    "Generiere ein Logo, das die Essenz beider Bilder einfängt.",
    "Schreibe eine kurze Geschichte über die beiden Bilder."
]

# Standardwerte für Wiederholungsversuche und Cache TTL
DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_WAIT_TIME = 1
DEFAULT_CACHE_TTL = 3600  # in Sekunden

# Schwellwert für die Anzeige des Spinners (in Sekunden)
SPINNER_THRESHOLD = 0.5

def load_models_from_config(config_file: str) -> list[str]:
    """
    Lädt die Liste der Modelle aus einer JSON-Datei.
    Falls die Datei nicht gefunden wird oder ein JSON-Fehler auftritt, 
    werden Standardmodelle zurückgegeben.
    """
    try:
        with open(config_file, 'r') as f:
            data = json.load(f)
            return data.get('models', [])
    except FileNotFoundError:
        st.warning(f"Konfigurationsdatei {config_file} nicht gefunden. Verwende Standardmodelle.")
        return ["gemini-2.0-flash-exp", "gemini-1.5-pro-001"]
    except json.JSONDecodeError:
        st.error(f"Fehler beim Lesen der JSON-Datei {config_file}. Bitte überprüfe das Format.")
        return ["gemini-2.0-flash-exp", "gemini-1.5-pro-001"]

def load_prompts_from_config(config_file: str) -> list[str]:
    """
    Lädt die Liste der Prompts aus einer JSON-Datei.
    Im Fehlerfall werden Fallback-Prompts genutzt.
    """
    try:
        with open(config_file, 'r') as f:
            data = json.load(f)
            return data.get('prompts', [])
    except FileNotFoundError:
        st.warning(f"Konfigurationsdatei {config_file} nicht gefunden. Verwende Standardprompts.")
        return EXAMPLE_PROMPTS_FALLBACK
    except json.JSONDecodeError:
        st.error(f"Fehler beim Lesen der JSON-Datei {config_file}. Bitte überprüfe das Format.")
        return EXAMPLE_PROMPTS_FALLBACK

def load_api_config(config_file: str) -> dict:
    """
    Lädt die API-Konfiguration aus einer JSON-Datei.
    Gibt im Fehlerfall Standardwerte zurück.
    """
    try:
        with open(config_file, 'r') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        st.warning(f"Konfigurationsdatei {config_file} nicht gefunden. Verwende Standardwerte.")
        return {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,
            "max_retries": DEFAULT_MAX_RETRIES,
            "base_wait_time": DEFAULT_BASE_WAIT_TIME,
            "cache_ttl": DEFAULT_CACHE_TTL
        }
    except json.JSONDecodeError:
        st.error(f"Fehler beim Lesen der JSON-Datei {config_file}. Bitte überprüfe das Format.")
        return {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,
            "max_retries": DEFAULT_MAX_RETRIES,
            "base_wait_time": DEFAULT_BASE_WAIT_TIME,
            "cache_ttl": DEFAULT_CACHE_TTL
        }

def load_themes_from_config(config_file: str) -> dict:
    """
    Lädt die Themes aus einer JSON-Datei.
    Im Fehlerfall wird ein leeres Dictionary zurückgegeben.
    """
    try:
        with open(config_file, 'r') as f:
            data = json.load(f)
            return data.get('themes', {})
    except FileNotFoundError:
        st.warning(f"Konfigurationsdatei {config_file} nicht gefunden. Verwende Standard-Themes.")
        return {}
    except json.JSONDecodeError:
        st.error(f"Fehler beim Lesen der JSON-Datei {config_file}. Bitte überprüfe das Format.")
        return {}

@st.cache_resource(ttl=load_api_config(API_CONFIG_FILE).get("cache_ttl", DEFAULT_CACHE_TTL))
def get_genai_client(api_key: str) -> genai.Client:
    """
    Initialisiert und cached den Google GenAI-Client.
    Hierbei wird der Client direkt mit dem API-Key initialisiert. Es wird
    ein kleiner Testaufruf durchgeführt, um sicherzustellen, dass der Client funktioniert.
    """
    client = genai.Client(api_key=api_key)
    client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=["Erstelle eine futuristische Stadt."],
        config=types.GenerateContentConfig(response_modalities=['Text', 'Image'])
    )
    return client

def validate_api_key(api_key: str) -> bool:
    """
    Validiert den API-Key durch einen minimalen API-Aufruf.
    Nutzt strukturelles Pattern Matching (PEP 634) zur Auswertung der Fehlermeldung.
    
    Rückgabe:
      True, wenn der API-Key gültig ist, ansonsten False.
    """
    try:
        client = get_genai_client(api_key)
        client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=["Test API Key"],
            config=types.GenerateContentConfig(response_modalities=['Text', 'Image'])
        )
        return True
    except Exception as e:
        error_message = str(e)
        match error_message:
            case msg if "401" in msg:
                st.error("API Key ist ungültig: Autorisierung fehlgeschlagen (401). Bitte überprüfe deinen API Key.")
            case msg if "403" in msg:
                st.error("API Key ist ungültig: Zugriff verboten (403). Dein API Key hat möglicherweise keine Berechtigung für diese Ressource.")
            case _:
                st.error(f"API Key ist ungültig: {error_message}")
        return False

def generate_content_with_retry(client: genai.Client, model_name: str, contents: list, config: types.GenerateContentConfig,
                                max_retries: int, base_wait_time: int) -> types.GenerateContentResponse | None:
    """
    Generiert Inhalte unter Verwendung von Wiederholungsversuchen (Exponential Backoff).
    
    Parameter:
      client: Der initialisierte GenAI-Client.
      model_name: Der Name des zu verwendenden Modells.
      contents: Liste der Inhalte (Text und ggf. Bilder).
      config: Konfigurationseinstellungen für die API-Anfrage.
      max_retries: Maximale Anzahl der Wiederholungsversuche bei einem Fehler.
      base_wait_time: Basiswartezeit vor dem nächsten Versuch.
    
    Rückgabe:
      Die API-Antwort, oder None, wenn alle Versuche fehlschlagen.
    """
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config
            )
            return response  # Erfolgreiche Antwort
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = base_wait_time * (2 ** attempt)
                st.warning(f"API-Aufruf fehlgeschlagen (Versuch {attempt + 1}/{max_retries}). Wiederhole in {wait_time:.2f} Sekunden...")
                time.sleep(wait_time)
            else:
                st.error(f"API-Aufruf ist nach {max_retries} Versuchen fehlgeschlagen: {str(e)}")
                return None
    return None

def display_image_metadata(uploaded_file, image_number: int) -> None:
    """
    Zeigt die Metadaten eines hochgeladenen Bildes an.
    
    Parameter:
      uploaded_file: Das hochgeladene Bild (Dateiobjekt).
      image_number: Die Bildnummer zur Kennzeichnung.
    """
    if uploaded_file:
        try:
            image = Image.open(uploaded_file)
            st.write(f"Bild {image_number}:")
            st.write(f"- Größe: {image.size}")
            st.write(f"- Format: {image.format}")
        except FileNotFoundError:
            st.error("Datei nicht gefunden.")
        except UnidentifiedImageError as e:
            st.error(f"Ungültiges Bildformat: {e}")
        except ImageFile.DecompressionBombError:
            st.error("Das Bild ist zu groß und kann nicht verarbeitet werden.")
        except Exception as e:
            st.exception(e)
            st.error(f"Fehler beim Anzeigen der Metadaten von Bild {image_number}: {str(e)}")
    else:
        st.write(f"Bild {image_number}: Kein Bild hochgeladen.")

def apply_theme() -> None:
    available_themes = load_themes_from_config(THEME_CONFIG_FILE)
    selected_theme = st.session_state.get("selected_theme", "")
    if selected_theme and selected_theme in available_themes:
        theme = available_themes[selected_theme]
        # Verwende den .stApp-Selektor und !important, um die Standard-Styles zu überschreiben
        css = f"""
        <style>
            /* Hintergrund- und Textfarbe für den Hauptcontainer */
            .stApp {{
                background-color: {theme['background_color']} !important;
                color: {theme['text_color']} !important;
            }}
            /* Button-Styling */
            .stButton > button {{
                background-color: {theme['button_color']} !important;
                color: {theme['button_text_color']} !important;
            }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    else:
        st.markdown("<style></style>", unsafe_allow_html=True)



def main() -> None:
    """
    Hauptfunktion der Streamlit-App.
    
    Steuert den Ablauf der Anwendung:
      - Laden der Konfigurationsdateien
      - Auswahl von Themes, Modellen und Prompts
      - Upload von Bildern und Texteingabe
      - Validierung des API-Keys und Aufruf der API zur Generierung von Inhalten
      - Anzeige der Ergebnisse und Downloadoption für generierte Bilder
    """
    # Theme-Auswahl: Überprüfe, ob bereits ein Theme im Session State existiert
    if "selected_theme" not in st.session_state:
        st.session_state["selected_theme"] = ""

    # Lade Themes und erzeuge eine Selectbox zur Auswahl
    available_themes = load_themes_from_config(THEME_CONFIG_FILE)
    theme_options = [""] + list(available_themes.keys())
    new_theme = st.selectbox(
        "Theme auswählen:",
        options=theme_options,
        index=theme_options.index(st.session_state.get("selected_theme", "")) if st.session_state.get("selected_theme", "") in theme_options else 0,
        help="Wähle ein Theme aus, um das Erscheinungsbild der App zu ändern."
    )
    if new_theme != st.session_state.get("selected_theme", ""):
        st.session_state["selected_theme"] = new_theme
        st.rerun()  # Seite neu laden, damit das CSS wirksam wird
    apply_theme()

    st.title("Google GenAI Streamlit App")
    st.write("Erstelle Inhalte basierend auf einem Textprompt und optional zwei Bildern.")

    # Initialisiere die Prompt-Historie im Session State
    if 'prompt_history' not in st.session_state:
        st.session_state.prompt_history = []

    # API-Key-Verwaltung: Möglichkeit, den API-Key aus Streamlit Secrets zu verwenden
    use_secrets = st.checkbox("API Key aus Streamlit Secrets verwenden", value=False,
                              help="Verwende den API Key, der sicher in Streamlit Secrets gespeichert ist.")
    if use_secrets:
        try:
            api_key = st.secrets["GENAI_API_KEY"]
        except KeyError:
            st.error("API Key nicht in Streamlit Secrets gefunden. Bitte konfiguriere den API Key in der Streamlit Cloud.")
            return
    else:
        api_key = st.text_input("API Key eingeben:", type="password",
                                help="Bitte gib deinen Google GenAI API Key ein.")

    # Debug-Modus für detaillierte Fehlerausgabe
    debug_mode = st.checkbox("Debug-Modus aktivieren", help="Aktiviere den Debug-Modus, um zusätzliche Informationen für die Fehleranalyse anzuzeigen.")

    with st.expander("Konfiguration"):
        # Lade verfügbare Modelle aus der Konfigurationsdatei
        available_models = load_models_from_config(MODEL_CONFIG_FILE)
        model_name = st.selectbox(
            "Modell auswählen:",
            available_models,
            index=0 if available_models else 0,
            help="Wähle das Gemini-Modell aus, das für die Generierung verwendet werden soll."
        )
        
        # Lade API-Parameter aus der Konfigurationsdatei
        api_config = load_api_config(API_CONFIG_FILE)
        temperature = api_config.get("temperature", 0.7)
        top_p = api_config.get("top_p", 0.95)
        top_k = api_config.get("top_k", 40)
        max_output_tokens = api_config.get("max_output_tokens", 1024)
        max_retries = api_config.get("max_retries", DEFAULT_MAX_RETRIES)
        base_wait_time = api_config.get("base_wait_time", DEFAULT_BASE_WAIT_TIME)

    # Layout mit zwei Spalten für Schieberegler und Bild-Uploads
    col1, col2 = st.columns(2)
    with col1:
        temperature = st.slider("Temperatur:", min_value=0.0, max_value=1.0, value=temperature, step=0.01,
                                  help="Die Temperatur beeinflusst die Zufälligkeit der Ausgabe. Höhere Werte führen zu zufälligeren Ergebnissen.")
        top_p = st.slider("Top P:", min_value=0.0, max_value=1.0, value=top_p, step=0.01,
                          help="Top P ist ein weiteres Steuerungselement für die Zufälligkeit. Niedrigere Werte führen zu fokussierteren Ergebnissen.")
        top_k = st.slider("Top K:", min_value=1, max_value=40, value=top_k, step=1,
                          help="Top K begrenzt die Anzahl der Token, die bei der Generierung berücksichtigt werden.")
        max_output_tokens = st.slider("Maximale Output-Tokens:", min_value=1, max_value=2048, value=max_output_tokens, step=1,
                                      help="Die maximale Anzahl der Token, die in der generierten Ausgabe enthalten sein dürfen.")
    with col2:
        uploaded_file1 = st.file_uploader("Bild 1 hochladen", type=["png", "jpg", "jpeg"],
                                          help="Lade das erste Bild hoch.")
        uploaded_file2 = st.file_uploader("Bild 2 hochladen", type=["png", "jpg", "jpeg"],
                                          help="Lade das zweite Bild hoch.")

    # Auswahl eines Beispiel-Prompts oder Verwendung der Prompt-Historie
    available_prompts = load_prompts_from_config(PROMPT_CONFIG_FILE)
    # Auswahl eines Beispiel-Prompts aus der JSON oder Prompt-Historie
    selected_prompt = st.selectbox("Oder wähle einen Beispiel-Prompt:", [""] + available_prompts,
                                   help="Wähle einen Beispiel-Prompt aus, um schnell loszulegen.")
    if st.session_state.prompt_history:
        st.write("Prompt-Historie:")
        selected_history_prompt = st.selectbox("Wähle einen Prompt aus der Historie:", [""] + st.session_state.prompt_history,
                                               help="Wähle einen zuvor verwendeten Prompt aus.")
        if selected_history_prompt:
            selected_prompt = selected_history_prompt

    # Verwende den ausgewählten Prompt als Default-Wert, falls vorhanden
    text_prompt = st.text_area(
        "Textprompt eingeben:",
        value=selected_prompt or "Kombiniere beide Bilder kreativ.",
        help="Gib hier deinen Textprompt ein."
    )


    # Anzeige der Bild-Metadaten
    st.subheader("Bild-Metadaten")
    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        display_image_metadata(uploaded_file1, 1)
    with col_meta2:
        display_image_metadata(uploaded_file2, 2)

    generated_image = None  # Speichert das generierte Bild
    generated_image_bytes = None  # Speichert die Bilddaten als Bytes

    if st.button("Generieren", help="Starte die Bildgenerierung."):
        if not api_key:
            st.error("Bitte gib einen gültigen API Key ein!")
            return

        # Validierung des API-Keys
        if not validate_api_key(api_key):
            return

        try:
            # Initialisiere den GenAI-Client
            client = get_genai_client(api_key)

            # Verarbeite den Textprompt und ggf. hochgeladene Bilder
            contents = [text_prompt]
            # Vor der Verarbeitung des Bildes in der Generierung:
            for uploaded_file in [uploaded_file1, uploaded_file2]:
                if uploaded_file is not None:
                    try:
                        # Stelle sicher, dass der Dateizeiger am Anfang steht
                        uploaded_file.seek(0)
                        image_bytes = uploaded_file.read()
                        image_input = Image.open(BytesIO(image_bytes))
                        contents.append(image_input)
                    except UnidentifiedImageError as e:
                        st.exception(e)
                        st.error(f"Fehler beim Verarbeiten des Bildes: {uploaded_file.name}")
                        continue


            # Debug-Ausgabe der Eingabedaten
            if debug_mode:
                st.markdown("### DEBUG: Eingabeinhalte")
                st.write("Contents:", contents)

            # API-Anfrage mit Wiederholungsversuchen
            with st.spinner("Generierung läuft..."):
                response = generate_content_with_retry(
                    client=client,
                    model_name=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_modalities=['Text', 'Image'],
                        temperature=temperature,
                        top_p=top_p,
                        top_k=top_k,
                        max_output_tokens=max_output_tokens
                    ),
                    max_retries=max_retries,
                    base_wait_time=base_wait_time
                )

            if response is None:
                st.error("Die Bildgenerierung ist fehlgeschlagen. Bitte versuche es später noch einmal.")
                return

            # Debug-Ausgabe der rohen API-Antwort
            if debug_mode:
                st.markdown("### DEBUG: API-Antwort")
                st.write(response)

            # Ergebnisse anzeigen
            st.subheader("Ergebnisse:")
            if not response or not response.candidates:
                st.error("Keine gültige Antwort von der API erhalten.")
                return

            for part in response.candidates[0].content.parts:
                if hasattr(part, 'text') and part.text:
                    st.write(part.text)
                elif hasattr(part, 'inline_data') and part.inline_data:
                    try:
                        image_output = Image.open(BytesIO(part.inline_data.data))
                        st.image(image_output, caption="Generiertes Bild", use_container_width=True)
                        generated_image = image_output
                        generated_image_bytes = part.inline_data.data
                        # Aktualisiere die Prompt-Historie
                        if text_prompt not in st.session_state.prompt_history:
                            st.session_state.prompt_history.append(text_prompt)
                            st.session_state.prompt_history = st.session_state.prompt_history[-5:]
                    except UnidentifiedImageError as e:
                        st.exception(e)
                        st.error("Fehlerhafte Bilddaten in der API-Antwort.")
                else:
                    st.error("Unbekannter Inhaltstyp in der Antwort.")

        except Exception as e:
            st.exception(e)
            st.error(f"Ein Fehler ist aufgetreten: {str(e)}")

    # Download-Button für das generierte Bild, falls vorhanden
    if generated_image and generated_image_bytes:
        st.download_button(
            label="Generiertes Bild herunterladen",
            data=generated_image_bytes,
            file_name="generated_image.png",
            mime="image/png",
            help="Lade das generierte Bild herunter."
        )

if __name__ == "__main__":
    # Erstelle den Konfigurationsordner, falls er nicht existiert
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    main()
