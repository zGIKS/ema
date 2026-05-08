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
│   └── layers/             # Each layer of the architecture
├── main.py
├── requirements.txt
└── shell.nix               # NixOS environment
```

## Installation

### Linux / macOS / Windows

```bash
pip install -r requirements.txt
```

### NixOS

Use the provided shell for system libraries (`libstdc++`, `zlib`, etc.):

```bash
nix-shell
uv pip install -r requirements.txt
uv run python main.py
```

## Usage

1. Place images of known people in `data/known_people/<name>/`.
2. Place images to recognize in `data/unknown/`.
3. Run:

```bash
python main.py
```

First run generates embeddings from `known_people` and saves them to `data/embeddings.json`. Subsequent runs load directly from file.
If there are multiple images in `data/unknown/`, it will process all and save a result per file in `output/`.

## Adjustments

- **Recognition threshold**: edit `threshold=0.80` in `main.py` (Post-processing layer).
- **Distance metric**: `cosine` (default) or `euclidean` in `InferenceLayer`.
- **ArcFace model**: `buffalo_l` by default. You can change it in `FeatureExtractionLayer`.
- **CPU/GPU**: defaults to CPU (`ctx_id=-1`). If you have CUDA, change to `ctx_id=0` in `FeatureExtractionLayer`.

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
