import os
import tempfile
import io
import base64

from dotenv import load_dotenv
from fasthtml.common import *
from PIL import Image
from gradio_client import Client, handle_file

# Load environment variables
load_dotenv()
hf_token = os.getenv("HF_TOKEN")
port = os.getenv("PORT", "3000")

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

if port is not None:
    port = int(port)

app, rt = fast_app()


def create_styles():
    return Style("""
    :root {
        /* Everforest Palette */
        --bg0: #2D353B;
        --bg1: #343F44;
        --fg0: #D3C6AA;
        
        --red: #E67E80;
        --orange: #E69875;
        --yellow: #DBBC7F;
        --green: #A7C080;
        --aqua: #83C092;
        --blue: #7FBBB3;
        --purple: #D699B6;
        
        /* Application-specific colors */
        --primary-color: var(--fg0);
        --secondary-color: var(--aqua);
        --background-color: var(--bg0);
        --card-bg: var(--bg1);
        --title-color: var(--green);
        --put-color: var(--red);
        --button-color: var(--blue);
        --button-hover: var(--aqua);
    }
    html, body {
      margin: 0;
      padding: 0;
      height: 100%;
        background-color: var(--background-color);
    }
    h1 {
        color: var(--green)
    }
    #upload-audio-title {
        color: var(--orange)
    }
    #audio-preview-title {
        color: var(--aqua)
    }
    #results-title {
        color: var(--purple)
    }
    #analyze-btn {
        background-color: var(--blue)
    }
    #app-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        height: 100vh;
        box-sizing: border-box;
        overflow: hidden;
    }
    #left-column {
        overflow-y: auto;
    }
    #right-column {
        overflow-y: auto;
    }
    #note {
        font-weight: bold;
    }
    body {
        font-family: 'Inter', system-ui, sans-serif;
        color: var(--fg0);
        line-height: 1.6;
    }
    p {
        color: var(--fg0);
    }
    audio {
        width: 100%;
        margin-bottom: 10px;
    }
    .basic-container {
        margin: 20px 0;
        padding: 15px;
        border: 1px solid #ddd;
        border-radius: 4px;
        background-color: var(--card-bg);
    }
    .data-containers {
        margin: 10px
    }
    .data-headings {
        color: var(--yellow)
    }
    .error-message {
        color: var(--red);
        border-radies: 4px;
        margin: 10px 0;
    }
    .spectrogram-img {
        max-width: 100%;
        max-height: 400px;
        object-fit: contain;
        width: auto;
        height: auto;
        border-radius: 4px;
        display: block;
        margin: 0 auto;
    }
    @media (max-width: 768px) {
        .spectrogram-img {
            max-height: 300px;
        }
        #app-container {
            grid-template-columns: 1fr;
            height: auto;
            overflow: visible;
        }
    }
    @media (max-width: 480px) {
        .spectrogram-img {
            max-height: 200px;
        }
    }
    """)


def create_ui():
    return Div(
        Div(create_upload_form(), create_preview_section(), id="left-column"),
        Div(create_results_section(), id="right-column"),
        id="app-container",
    )


def create_upload_form():
    return Form(
        H3("Upload an Audio File", id="upload-audio-title"),
        P("Select a .wav or .mp3 file to classify. You can play it before processing."),
        P("Note: We are currently only able to classify cat 🐱 vs dog 🐶 sounds.", id="note"),
        Input(
            hx_post="/upload",
            hx_target="#audio-player-container",
            hx_swap="innerHTML",
            type="file",
            id="audio-file",
            name="audio",
            accept="audio/*",
        ),
        Button(
            "Analyze Audio",
            id="analyze-btn",
            type="submit",
            hx_post="/analyze",
        ),
        hx_encoding="multipart/form-data",
        hx_target="#results-container",
        hx_swap="innerHTML",
        cls="basic-container",
    )


def create_preview_section():
    return Div(
        H3("Audio Preview", id="audio-preview-title"),
        P("Your audio will appear here after uploading", id="no-audio"),
        Div(id="audio-player-container"),
        cls="basic-container",
    )


def create_results_section():
    return Div(
        H3("Analysis Results", id="results-title"),
        Div(id="audio-player-container"),
        Div(id="results-container"),
        cls="basic-container",
    )


async def process_audio_file(file):
    # Save to temporary file
    # Doing this because `handle_file` from Gradio expects a filepath or a URL as input
    file_extension = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        temp_file.write(await file.read())
        temp_path = temp_file.name

    try:
        # Call the Gradio API
        client = Client("khoaHyh/cat-meow-vs-dog-bork", hf_token=hf_token)
        result = client.predict(file=handle_file(temp_path), api_name="/predict_audio")

        (
            _,
            prediction,
            confidence,
            spectrogram_base64,
        ) = result

        spectrogram_url = f"data:image/png;base64,{spectrogram_base64}"

        return {"spectrogram": spectrogram_url, "prediction": prediction, "confidence": confidence}
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@rt("/")
def get():
    return Titled("SonicSight - Audio Classifier", PicoBusy(), create_ui(), create_styles())


@rt("/upload")
async def upload(request):
    try:
        form = await request.form()
        audio_file = form.get("audio")

        if audio_file is None or not audio_file.filename:
            return "No file selected"

        mime_type = audio_file.content_type
        if not mime_type.startswith("audio/"):
            return Div("Error: Please upload an audio file (.mp3, .wav, etc.)", cls="error-message")

        if audio_file.size > MAX_FILE_SIZE:
            return Div("Error: File size exceeds the maximum allowed size (10MB)", cls="error-message")

        # TODO: check audio file signatures

        audio_element = Audio(
            controls=True,
            autoplay=False,
        )

        # If file sizes get larger, we might not be able to base64 encode
        content = await audio_file.read()
        b64_content = base64.b64encode(content).decode("utf-8")
        data_url = f"data:{mime_type};base64,{b64_content}"

        audio_element.src = data_url

        return Div(P(f"{audio_file.filename}"), audio_element)
    except Exception as e:
        return f"Error: {str(e)}"


@dataclass
class AudioAnalysisResult:
    spectrogram: str
    prediction: str
    confidence: float
    error: str | None

    def __ft__(self):
        if self.error is not None:
            return Div(self.error)

        container = Div(id="audio-player-container")
        results = Div(
            Div(
                H4("Spectrogram:", cls="data-headings"),
                Img(src=self.spectrogram, cls="spectrogram-img", alt="Audio Spectrogram"),
                cls="data-containers",
            ),
            Div(H4("Prediction:", cls="data-headings"), P(f"{self.prediction}"), cls="data-containers"),
            Div(H4("Confidence:", cls="data-headings"), P(f"{self.confidence}"), cls="data-containers"),
        )
        return container(results)


@rt("/analyze")
async def analyze(request):
    try:
        # Get uploaded file
        form = await request.form()
        file = form.get("audio")

        if file is None:
            raise FileNotFoundError("Audio file not found")

        results = await process_audio_file(file)
        container = Div(id="results-container")

        return container(
            AudioAnalysisResult(
                spectrogram=results["spectrogram"],
                prediction=results["prediction"],
                confidence=results["confidence"],
                error=None,
            )
        )

    except Exception as e:
        # Handle errors
        return {"error": f"Failed to process audio: {str(e)}"}


if __name__ == "__main__":
    serve(port=port, host="0.0.0.0", reload=False)
