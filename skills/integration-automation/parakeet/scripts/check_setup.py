#!/usr/bin/env python3
"""Verify Parakeet installation and dependencies.

Usage:
    check_setup.py

Checks:
- Python version
- Required packages (nemo_toolkit, torch, sounddevice, soundfile)
- Parakeet model availability
- Hardware acceleration (MPS/CUDA)
- Microphone access
"""

import sys
import os

# Add Parakeet to path (configurable via PARAKEET_HOME)
PARAKEET_PATH = os.environ.get(
    "PARAKEET_HOME",
    os.path.expanduser("~/Programming/parakeet-dictate")
)
sys.path.insert(0, PARAKEET_PATH)


def check_mark(passed: bool) -> str:
    return "OK" if passed else "FAIL"


def main():
    all_passed = True

    print("Parakeet Dictation - Setup Check")
    print("=" * 40)
    print()

    # Check Python version
    py_version = sys.version_info
    py_ok = py_version >= (3, 10)
    print(f"Python version: {py_version.major}.{py_version.minor}.{py_version.micro} [{check_mark(py_ok)}]")
    if not py_ok:
        print("  -> Python 3.10+ required")
        all_passed = False

    # Check Parakeet path
    parakeet_ok = os.path.exists(PARAKEET_PATH)
    print(f"Parakeet path: {PARAKEET_PATH} [{check_mark(parakeet_ok)}]")
    if not parakeet_ok:
        print("  -> Parakeet not found at expected path")
        all_passed = False
        print()
        print("RESULT: FAIL - Parakeet not installed")
        sys.exit(1)

    # Check NeMo toolkit
    try:
        import nemo.collections.asr as nemo_asr
        nemo_ok = True
        print(f"NeMo toolkit: installed [{check_mark(nemo_ok)}]")
    except ImportError as e:
        nemo_ok = False
        print(f"NeMo toolkit: not found [{check_mark(nemo_ok)}]")
        print(f"  -> {e}")
        all_passed = False

    # Check PyTorch
    try:
        import torch
        torch_ok = True
        print(f"PyTorch: {torch.__version__} [{check_mark(torch_ok)}]")
    except ImportError:
        torch_ok = False
        print(f"PyTorch: not found [{check_mark(torch_ok)}]")
        all_passed = False

    # Check sounddevice
    try:
        import sounddevice as sd
        sd_ok = True
        print(f"sounddevice: installed [{check_mark(sd_ok)}]")
    except ImportError:
        sd_ok = False
        print(f"sounddevice: not found [{check_mark(sd_ok)}]")
        all_passed = False

    # Check soundfile
    try:
        import soundfile as sf
        sf_ok = True
        print(f"soundfile: installed [{check_mark(sf_ok)}]")
    except ImportError:
        sf_ok = False
        print(f"soundfile: not found [{check_mark(sf_ok)}]")
        print("  -> Install with: pip install soundfile")
        all_passed = False

    print()

    # Check hardware acceleration
    if torch_ok:
        print("Hardware Acceleration:")
        if torch.backends.mps.is_available():
            print("  MPS (Apple Silicon): available")
        else:
            print("  MPS (Apple Silicon): not available")

        if torch.cuda.is_available():
            print(f"  CUDA: available ({torch.cuda.get_device_name(0)})")
        else:
            print("  CUDA: not available")

        if not torch.backends.mps.is_available() and not torch.cuda.is_available():
            print("  -> Will use CPU (slower)")

    print()

    # Check microphone access
    if sd_ok:
        try:
            default_input = sd.query_devices(kind='input')
            mic_ok = default_input is not None
            if mic_ok:
                print(f"Microphone: {default_input['name']} [{check_mark(mic_ok)}]")
            else:
                print(f"Microphone: no default input device [{check_mark(mic_ok)}]")
                all_passed = False
        except Exception as e:
            mic_ok = False
            print(f"Microphone: error checking [{check_mark(mic_ok)}]")
            print(f"  -> {e}")
            all_passed = False

    print()

    # Try loading model (quick check)
    if nemo_ok:
        print("Model check:")
        try:
            from src.config import get_config
            config = get_config()
            print(f"  Model: {config.model_name}")
            print("  Status: ready to load (not pre-loaded)")
            print("  Note: First transcription will download/load model (~10-30s)")
        except Exception as e:
            print(f"  Error: {e}")
            all_passed = False

    print()
    print("=" * 40)

    if all_passed:
        print("RESULT: OK - Parakeet is ready to use")
        print()
        print("Try: /parakeet check    - This check")
        print("     /parakeet dictate  - Record from mic")
        print("     /parakeet <file>   - Transcribe audio file")
    else:
        print("RESULT: FAIL - Some checks failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
