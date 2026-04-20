# Dataset Guide (Static + Dynamic Signs)

This project does not ship large datasets directly. Use this folder to organize and train your own models.

## Suggested structure

```text
datasets/
├── static/
│   ├── train/
│   ├── val/
│   └── test/
├── dynamic/
│   ├── train/
│   ├── val/
│   └── test/
└── metadata/
    ├── labels_static.csv
    └── labels_dynamic.csv
```

- `static/`: image-based signs (single-frame handshapes, PNG/JPG).
- `dynamic/`: temporal signs (GIF/video clips such as MP4).

## Minimum metadata columns

- `sample_id`
- `label`
- `split` (`train`, `val`, `test`)
- `path`
- `fps` (for dynamic only)
- `duration_ms` (for dynamic only)

## Practical notes for Raspberry Pi 4

- Prefer compressed 224x224 images for static datasets.
- Prefer short clips (1–3 seconds) and 15–25 FPS for dynamic datasets.
- Start with small vocab subsets, then expand.

## Offline STT assets

Place Vosk model directories under:

```text
models/vosk/
```

Run pipeline with:

```bash
python app.py --stt-backend vosk --vosk-model-path models/vosk/<model-folder>
```
