# Facial Recognition System - 7 Layers

Stack: Python, OpenCV, ArcFace (insightface), NumPy, local JSON storage.

## Structure

```
.
├── data/
│   ├── known_people/       # Folders per person with images
│   ├── unknown/            # Images to recognize
│   └── embeddings.json     # Generated embeddings
├── models/                 # Models downloaded by insightface (buffalo_l)
├── output/
│   └── result.jpg          # Image marked with result
├── src/
│   ├── config/             # Defaults / settings
│   ├── data/               # Data layer
│   ├── preprocessing/      # Preprocessing layer
│   ├── feature_extraction/ # Feature extraction layer
│   ├── inference/          # Inference layer
│   ├── post_processing/    # Post-processing layer
│   ├── storage/            # Storage layer
│   ├── output/             # Output layer
│   ├── algorithms/         # Utility algorithms (optimizers, recursion, etc.)
│   ├── calibration/        # Optional calibration modules
│   └── main.py             # Entry point (recommended)
├── main.py
├── requirements.txt
└── shell.nix               # NixOS environment
```

## Installation

### Linux / macOS / Windows

```bash
pip install -r requirements.txt
```

### Using uv (recommended)

```bash
./scripts/bootstrap.sh
```

### Using .env

1. Copy `.env.example` to `.env`
2. Run normally (it auto-loads `.env`):

```bash
uv run python -m src.main
```

### NixOS

Use the provided shell for system libraries (`libstdc++`, `zlib`, etc.):

```bash
nix-shell
uv pip install -r requirements.txt
uv run python main.py
```

## Usage

1. Place images of known people in `data/known_people/<name>/` (recommended).
   - Optional: set `FR_ALLOW_FLAT_KNOWN=1` to also accept images directly under `data/known_people/` and use the filename as the person name.
2. Place images to recognize in `data/unknown/`.
3. Run:

```bash
python main.py
```

Alternative:

```bash
python -m src.main
```

First run generates embeddings from `known_people` and saves them to `data/embeddings.json`. Subsequent runs load directly from file.
If there are multiple images in `data/unknown/`, it will process all and save a result per file in `output/`.

### Useful flags

```bash
# Rebuild embeddings after adding/changing known people photos
python main.py --rebuild

# Calibrate recognition strictness
python main.py --threshold 0.74 --min-margin 0.02

# Debug matches
python main.py --topk 3

# Auto-calibrate from stored embeddings (needs some people with >=2 photos)
python main.py --calibrate --calib-optimizer adam

# Optional: train extra calibrators (needs some people with >=2 photos)
python main.py --train-logistic --logistic-optimizer adam
python main.py --train-q-policy
```

## Adjustments

- **Recognition threshold**: use `--threshold` (default 0.80).
- **Recognition threshold**: use `--threshold` (default 0.60).
- **Margin filter**: use `--min-margin` (default 0.03).
- **Detection strictness**: use `--min-det-score` (default 0.50).
- **Debug output**: use `--topk` to print top matches.
- **CPU/GPU**: defaults to CPU (`ctx_id=-1` in `FeatureExtractionLayer`). For CUDA, change to `ctx_id=0`.

## Notes

- `insightface` automatically downloads the `buffalo_l` model to `models/buffalo_l/` (~275 MB) on first run.
- Runs on CPU by default.
- If you delete `data/embeddings.json`, the system will regenerate embeddings from `known_people`.
- If an unknown image contains multiple faces, the system detects and recognizes each face and draws a box/label per face in `output/<image>_result.jpg`.

## Layer Flow

1. **Data Layer**: manages paths for known and unknown images.
2. **Preprocessing Layer**: loads, resizes, converts to RGB.
3. **Feature Extraction Layer**: detects *all* faces and extracts 512-D L2-normalized embeddings with ArcFace.
4. **Inference Layer**: compares embeddings by cosine similarity.
5. **Post-processing Layer**: applies threshold (0.80) + top1/top2 margin to reduce false positives.
6. **Storage Layer**: saves/loads embeddings to/from `embeddings.json` (v2 stores per-person prototype + per-image embeddings).
7. **Output Layer**: prints per-face results to console and generates an annotated image per input.
