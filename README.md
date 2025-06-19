# 🎥 transvid

`transvid` is a Python library that allows you to download, transcribe, translate, and subtitle videos, using local Whisper models and OpenAI services to transform multimedia content automatically.

---

## 🚀 Features

- ✅ Download videos from YouTube.
- 🎙 Transcribe audio with local Whisper models.
- 🌍 Translate subtitles into multiple languages.
- 🗣 Generate voice from translated text (TTS).
- 🎞 Embed subtitles directly into videos.
- 🔁 Convert between audio and video formats.

---

## 📦 Installation

```bash
pip install
```

Or, if working from a local repository:

```bash
git clone https://github.com/your_user/transvid.git
cd transvid
pip install -r requirements.txt
```

---

## 🧠 Requirements

- Python 3.8 or higher
- `ffmpeg` and `moviepy` installed
- Local Whisper models available
- OpenAI API key (for optional TTS)

---

## 📚 Basic Usage
### Download a YouTube Video

```python
from transvid import DownloadYoutubeVideo

yt = DownloadYoutubeVideo(
    url="https://youtube.com/...",
    output_name="my_video",
    format_output="mp4", 
)
yt.download_video()
```

### Initialize the Video Translator

This block imports the main class and creates a translator instance using the original video file, the target language, and your OpenAI API key.


```python
from transvid import GenerateTranslation

translator = GenerateTranslation(
    file="my_video.mp4",
    target_lang="es",
    openai_api_key="your_api_key"
)
```

### ✅ Add Translated Subtitles to the Original Video — Free Feature
Generates translated subtitles and embeds them directly into the original video. This feature is completely free and does not incur any charges from OpenAI.

```python
translator.add_subtitles_to_video(output_video="video_with_subtitles.mp4")
```

### 💳 Create a New Translated Video with Synthetic Voices — Paid Feature
This function generates a new video with translated audio using synthetic voices. The resulting video includes subtitles in the language specified via target_lang.

📌 ***Estimated cost:** about **$1 USD per hour of video**, based on OpenAI’s token-based pricing.

```python
translator.create_video(output_video="translated_video.mp4")
```

### 💳 Export Translated Audio Only — Paid Feature
Exports only the translated audio (without video). Like the previous function, it uses OpenAI models and is subject to token-based billing.

📌 **Estimated cost:** about **$1 USD per hour of audio**, based on OpenAI’s token-based pricing.

```python
translator.create_audio(output_audio="translated_audio.wav")
```

---

## ℹ️ About Pricing
The voice synthesis and audio translation features rely on OpenAI services (such as Whisper and TTS), which are billed based on the number of tokens processed.

While costs may vary depending on audio quality and length, a general estimate is:

- **Hour of audio ≈ 60,000 tokens ≈ ~$1 USD**

Make sure your OpenAI account has a valid API key and sufficient credit balance before using these features.

Let me know if you’d like to include an installation guide or usage example with multiple languages.

---

## ⚙️ Custom Parameters


