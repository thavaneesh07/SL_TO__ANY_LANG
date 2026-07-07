# Setup on a New PC

## Quick Start

This repository is designed to be portable and cloneable on any machine.

### 1. Clone the repository

```bash
git clone --branch portable https://github.com/thavaneesh07/SL_TO__ANY_LANG.git
# or
git clone --branch portable https://github.com/ketan-kv/ISLtoKan.git
```

The `portable` branch is lightweight (~50 MB) and includes all code and documentation without the large video datasets.

### 2. Set up the Python environment

```bash
cd "SL_TO__ANY_LANG"  # or ISLtoKan

# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 3. Get the large video assets (if needed)

The following folders are intentionally kept local and not in the repository:
- `video_data/` — Raw video files
- `video_dataset/` — Processed dataset
- `video_model/` — Pre-trained model and landmarks
- `Video_word_context/` — Language context data

**Options:**
- **Copy from the original PC** — Transfer these folders via external drive, USB, or network share.
- **Use cloud storage** — Upload these to Google Drive, OneDrive, or AWS S3 and download on the new PC.
- **Regenerate landmarks** — Run `preprocess.py` on your own dataset if you don't need the exact training data.

### 4. Ready to work

Once the environment is set up, you can:
- Train the model: `python train.py`
- Run inference: `python main.py`
- Work on the codebase as normal

## Why is it set up this way?

GitHub has limits on repository size. Keeping large datasets local ensures:
- ✅ Fast clones on any new PC (~30 seconds instead of 10+ minutes)
- ✅ Smaller bandwidth requirements
- ✅ Easier to manage versions independently

The `main` branch on both remotes still tracks the full history for reference, but `portable` is the recommended branch for day-to-day work on new machines.

## Need help?

- Check the [README.md](README.md) for workflow details.
- See [PROJECT_EXPLANATION.md](PROJECT_EXPLANATION.md) for the full architecture.
