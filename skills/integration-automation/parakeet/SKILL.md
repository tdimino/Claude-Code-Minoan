---
name: parakeet
description: >
  Local speech-to-text using NVIDIA Parakeet TDT 0.6B.
  Use for transcribing audio files or dictating voice input directly into Claude Code.
  Processes 100% locally with 3,386x realtime speed and 6% word error rate.
argument-hint: [audio-file | "dictate" | "check"]
tools: [Bash, Read, Write]
---

# Parakeet Dictation Skill

Local speech-to-text powered by NVIDIA Parakeet TDT 0.6B (~600MB model, 100% offline).

## Performance

- **Speed**: 3,386x realtime (1 hour audio → ~1 second)
- **Accuracy**: 6.05% WER (Word Error Rate)
- **Privacy**: 100% local processing, no cloud API
- **Acceleration**: Apple Silicon MPS, NVIDIA CUDA, or CPU fallback

## Commands

### Transcribe Audio File

```bash
/parakeet path/to/audio.wav
/parakeet ~/recordings/interview.mp3
/parakeet meeting.m4a
```

Supported formats: `.wav`, `.mp3`, `.m4a`, `.flac`, `.ogg`, `.aac`

### Live Dictation

```bash
/parakeet
/parakeet dictate
```

Records from microphone until Enter is pressed, then transcribes.

### Check Installation

```bash
/parakeet check
```

Verifies Parakeet is properly installed and the model can load.

## Setup

### Prerequisites

1. **Clone the Parakeet Dictate app**:
   ```bash
   git clone https://github.com/your-org/parakeet-dictate ~/Programming/parakeet-dictate
   cd ~/Programming/parakeet-dictate
   ```

2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **(Optional) Set custom install path**:
   ```bash
   export PARAKEET_HOME=/path/to/parakeet-dictate
   ```
   Default: `~/Programming/parakeet-dictate`

## Implementation

When this skill is invoked:

1. **For audio files**: Run the transcription script
   ```bash
   cd ~/.claude/skills/parakeet/scripts && \
   ${PARAKEET_HOME:-~/Programming/parakeet-dictate}/.venv/bin/python transcribe.py "<filepath>"
   ```

2. **For live dictation**: Run the dictation script
   ```bash
   cd ~/.claude/skills/parakeet/scripts && \
   ${PARAKEET_HOME:-~/Programming/parakeet-dictate}/.venv/bin/python dictate.py
   ```

3. **For checking setup**: Run the check script
   ```bash
   cd ~/.claude/skills/parakeet/scripts && \
   ${PARAKEET_HOME:-~/Programming/parakeet-dictate}/.venv/bin/python check_setup.py
   ```

## First Run

The first transcription takes ~10-30 seconds while the Parakeet model loads into memory.
Subsequent transcriptions are instant (sub-second for typical recordings).

## Troubleshooting

### "No module named nemo"
The Parakeet virtual environment needs to be used. Scripts automatically use the correct Python.

### "MPS not available"
Apple Silicon Metal acceleration requires PyTorch 2.0+. Falls back to CPU automatically.

### "Permission denied: microphone"
Grant microphone access to Terminal in System Preferences → Privacy & Security → Microphone.

### Model download slow
The 600MB Parakeet model downloads on first use. Subsequent runs use the cached model.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PARAKEET_HOME` | `~/Programming/parakeet-dictate` | Parakeet Dictate installation path |

## Dependencies

This skill requires:
- **Parakeet Dictate app** at `$PARAKEET_HOME` (default: `~/Programming/parakeet-dictate`)
- **Python virtual environment** at `$PARAKEET_HOME/.venv`
- **NeMo toolkit** with ASR support (`nemo_toolkit[asr]>=2.0.0`)
- **PyTorch 2.0+** (for MPS/CUDA acceleration)
- **soundfile** and **sounddevice** for audio handling
