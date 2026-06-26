# Transcription Benchmark — Methodology and Results

## 1. Objective

This test measured how long it takes to transcribe audio of different lengths using the OpenAI Whisper model. A secondary objective was to observe how the model handles speakers with different accent backgrounds, comparing performance across American, Indian, Nigerian, Chinese, and Italian English speakers.

---

## 2. Hypotheses

- Videos with non-American accents would take longer to transcribe.
- Longer videos would take proportionally more time to transcribe.
- The `small` model would be more accurate than the `base` model, at the cost of increased transcription time.

---

## 3. Environment

| Component | Details |
|-----------|---------|
| Tool | OpenAI Whisper (via Hugging Face) |
| Install command | `pip install openai-whisper` |
| CPU | Intel Core i5 |
| RAM | 8 GB |
| OS | Windows 11 Pro |
| Shell | Git Bash / PowerShell |
| Precision | FP32 (CPU fallback — FP16 not supported on CPU) |

---

## 4. Methodology

### 4.1 Software Setup

1. **Installed ffmpeg** using Chocolatey (Command Prompt, run as Administrator):
   ```bash
   choco install ffmpeg
   ```
   ffmpeg is a free, open-source tool for working with audio and video files.

2. **Selected video samples** based on two criteria:
   - Duration (ranging from ~3 minutes to ~1 hour 42 minutes)
   - Accent type of the speaker(s)

3. **Created a Python virtual environment**, activated it, and installed Whisper:
   ```bash
   python -m venv venv
   source venv/Scripts/activate   # Git Bash
   pip install openai-whisper
   ```

### 4.2 Audio Extraction

Audio was extracted from each video file using ffmpeg before transcription. This step was performed to pass audio-only input to Whisper.

**Command used:**
```bash
ffmpeg -i video.mp4 -q:a 0 -map a audio.mp3
```

| Flag | Meaning |
|------|---------|
| `-i video.mp4` | Input video file |
| `-q:a 0` | Highest audio quality |
| `-map a` | Extract only the audio stream |
| `audio.mp3` | Output filename |

This command works in both Git Bash and PowerShell.

### 4.3 Transcription

Each audio file was transcribed using the following command:

```bash
whisper audio.mp3 --model base
```

For the Chinese accent sample, the model incorrectly identified the language. The `--language` flag was added to correct this:

```bash
whisper audio.mp3 --model base --language en
```

For the Nigerian accent comparison test, the same audio was also transcribed using the `small` model:

```bash
whisper audio.mp3 --model small
```

### 4.4 Metrics Recorded

For each sample, the following were recorded:

- Video length
- Audio extraction (conversion) time
- Speaker accent
- Transcription time
- Model used (`base` or `small`)

---

## 5. Results

### 5.1 Transcription Benchmark Data

| Video Length | Conversion Time | Accent | Transcription Time | Model |
|:-------------|:----------------|:-------|:-------------------|:------|
| 00:03:10 | 00:00:02.70 | American | 00:04:29.08 | base |
| 00:03:15 | 00:00:03.14 | Indian | 00:03:31.10 | base |
| 00:08:03 | 00:00:06.52 | Nigerian | 00:07:20.67 | base |
| 00:09:16 | 00:00:10.14 | American | 00:08:16.63 | base |
| 00:30:46 | 00:00:31.88 | American | 00:41:45.23 | base |
| 00:31:56 | 00:00:29.88 | Chinese | 00:42:18.76 | base |
| 00:53:52 | 00:00:48.02 | Italian | 00:26:06.23 | base |
| 01:42:02 | 00:01:46.04 | Indian-American & Arab | 01:54:33.67 | base |
| 00:13:02 | 00:00:16.17 | Nigerian | 00:24:15.25 | base |
| 00:13:02 | 00:00:16.17 | Nigerian | 00:42:30.42 | small |

### 5.2 Whisper Model Reference

| Model | Speed | Accuracy | RAM Required |
|-------|-------|----------|--------------|
| tiny | Fastest | Lowest | ~1 GB |
| base | Fast | Better | ~1.5 GB |
| small | Medium | Good | ~2 GB |
| medium | Slower | Very Good | ~5 GB |
| large | Slowest | Best | ~10 GB |

---

## 6. Analysis and Discussion

### 6.1 Accent vs. Transcription Time

Contrary to expectation, **accent type did not significantly affect transcription time**. The 3-minute 15-second video with an Indian-accented speaker actually transcribed *faster* than the 3-minute 10-second video with an American speaker. Transcription time appeared to correlate more strongly with video duration than with accent type.

### 6.2 Duration vs. Transcription Time

As expected, longer videos generally took more time. However, one notable outlier was the 53-minute 52-second Italian-accented video, which transcribed in just ~26 minutes — significantly faster than a proportional estimate would predict. A possible explanation is that this video contained extended periods of silence or low speech density ("less talking"), reducing the effective audio the model needed to process.

### 6.3 Language Misidentification (Chinese Accent Sample)

The model **failed to correctly identify the language** in the 31-minute 56-second video with Chinese-accented English speakers. It transcribed the audio in Malay instead of English. This was corrected by explicitly specifying the language:

```bash
whisper audio.mp3 --model base --language en
```

This is a known limitation of Whisper when accent characteristics cause it to misclassify the spoken language.

### 6.4 Transcription Failure (1hr 42min Sample)

The transcription of the 1-hour 42-minute video failed after approximately 53 minutes and had to be restarted. The likely cause is memory pressure given the 8 GB RAM constraint when processing long-duration audio with the `base` model in FP32 mode.

### 6.5 Base vs. Small Model Comparison (Nigerian Accent)

The same 13-minute 2-second Nigerian-accented audio was transcribed with both the `base` and `small` models:

| Model | Transcription Time |
|-------|--------------------|
| base | 00:24:15.25 |
| small | 00:42:30.42 |

The `small` model took approximately **18 minutes longer** to produce its output. In terms of accuracy, the `small` model performed slightly better overall, though the `base` model produced better results for certain individual words.

A notable issue observed with the `small` model: it **skipped approximately 30 seconds of content** during transcription even though speech was continuous during that period. This was detected by listening to the audio alongside the transcript. It is possible that additional gaps exist in other transcribed files that were not manually audited.

This behavior suggests that Whisper may skip over words or segments it cannot decode with sufficient confidence, rather than producing a low-confidence guess.

---

## 7. Conclusions

- Transcription time scales roughly with video length, not accent type.
- Speech density matters: videos with more silence or less active speech may transcribe faster than their duration implies.
- Whisper can misidentify languages when accents are strong — use `--language` to override.
- The `small` model is more accurate than `base` in most cases but is ~1.75× slower and can skip segments.
- On 8 GB RAM with CPU-only inference, very long audio (1.5+ hours) may cause failures and require restarts.
- It is worth auditing transcription logs for content gaps, especially when using the `small` model, to assess how much context may have been lost to inaccuracy or skipping.
