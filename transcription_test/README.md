# Whisper Transcription Benchmarking Tool

A local benchmarking setup for evaluating OpenAI's Whisper speech-to-text model across video samples of varying lengths and accent types. This project measures transcription speed and accuracy using Whisper's `base` and `small` models on CPU.

---

## Overview

This project uses the [Hugging Face OpenAI Whisper](https://huggingface.co/openai/whisper-base) model to transcribe audio extracted from video files. The goal is to benchmark transcription time and observe how the model handles different accent types and audio durations.

See [`METHODOLOGY_AND_RESULTS.md`](./METHODOLOGY_AND_RESULTS.md) for full methodology, test results, and analysis.

---

## Prerequisites

- Python 3.8+
- [ffmpeg](https://ffmpeg.org/): for audio extraction
- Git Bash or PowerShell (Windows)

---

## Setup

### 1. Install ffmpeg

Using Chocolatey (run Command Prompt as Administrator):

```bash
choco install ffmpeg
```

### 2. Clone or open the project folder in VSCode

Place your video files in the project directory.

### 3. Create and activate a virtual environment

```bash
python -m venv venv
```

**Git Bash:**
```bash
source venv/Scripts/activate
```

**PowerShell:**
```powershell
venv\Scripts\activate
```

### 4. Install Whisper

```bash
pip install openai-whisper
```

---

## Usage

### Step 1: Extract audio from a video file

```bash
ffmpeg -i video.mp4 -q:a 0 -map a audio.mp3
```

| Flag | Description |
|------|-------------|
| `-i video.mp4` | Input video file |
| `-q:a 0` | Best audio quality |
| `-map a` | Extract audio stream only |
| `audio.mp3` | Output audio filename |

This command works in both Git Bash and PowerShell.

### Step 2: Transcribe the audio

```bash
whisper audio.mp3 --model base
```

To specify a language (useful when the model misidentifies the language):

```bash
whisper audio.mp3 --model base --language en
```

Available models:

| Model | Speed | Accuracy | RAM Required |
|-------|-------|----------|--------------|
| `tiny` | Fastest | Lowest | ~1 GB |
| `base` | Fast | Better | ~1.5 GB |
| `small` | Medium | Good | ~2 GB |
| `medium` | Slower | Very Good | ~5 GB |
| `large` | Slowest | Best | ~10 GB |

### Output Files

After transcription, Whisper generates five output files per audio sample:

| Extension | Description |
|-----------|-------------|
| `.json` | Full transcription with timestamps and metadata |
| `.srt` | SubRip subtitle format |
| `.tsv` | Tab-separated values with timing data |
| `.txt` | Plain text transcript |
| `.vtt` | WebVTT subtitle format |

---

## Test Hardware

All tests were conducted on:

- **CPU:** Intel Core i5
- **RAM:** 8 GB
- **OS:** Windows 11 Pro

> Note: Whisper runs on CPU in this setup. FP16 is not supported on CPU, Whisper automatically falls back to FP32. GPU acceleration would significantly reduce transcription time.

---

## Project Structure

```
transcriber/
├── venv/                   # Python virtual environment
├── *.mp4                   # Source video files
├── *.mp3                   # Extracted audio files
├── *.json                  # Transcription output (JSON)
├── *.srt                   # Transcription output (SRT subtitles)
├── *.tsv                   # Transcription output (TSV)
├── *.txt                   # Transcription output (plain text)
├── *.vtt                   # Transcription output (WebVTT)
├── README.md               # This file
└── METHODOLOGY_AND_RESULTS.md  # Full test methodology and results
```
