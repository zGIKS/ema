from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from src.config.dotenv import load_dotenv
from src.data import DataLayer
from src.feature_extraction import FeatureExtractionLayer
from src.inference import InferenceLayer
from src.output import OutputLayer
from src.post_processing import PostprocessingLayer
from src.preprocessing import PreprocessingLayer
from src.storage import StorageLayer
from src.storage import PolicyStore, QPolicyOnDisk
from src.calibration.threshold_calibrator import ThresholdCalibrator
from src.calibration.pair_sampling import sample_similarity_pairs
from src.calibration.logistic_calibrator import LogisticCalibrator
from src.calibration.q_threshold_policy import QThresholdPolicyTrainer


def register_known_people(
    data_layer: DataLayer,
    preprocessor: PreprocessingLayer,
    extractor: FeatureExtractionLayer,
    min_det_score: float,
) -> dict:
    known_people = data_layer.list_known_people()
    if not known_people:
        print("[WARN] No known people found in data/known_people/")
        return {}

    embeddings: dict = {}
    for person in known_people:
        images = data_layer.list_images_for_person(person)
        person_embs = []
        for img_path in images:
            print(f"Registering {person} - {img_path.name}")
            try:
                rgb = preprocessor.process(img_path)
                all_faces = extractor.extract_all(rgb, min_det_score=min_det_score)
                if not all_faces:
                    print(f"   [WARN] No face detected in {img_path.name}")
                    continue

                # Largest face wins (avoid registering bystanders).
                def area(face_obj):
                    x1, y1, x2, y2 = face_obj.bbox
                    return (x2 - x1) * (y2 - y1)

                emb, _ = max(all_faces, key=lambda t: area(t[1]))
                if emb is not None:
                    person_embs.append(emb)
            except Exception as e:
                print(f"   [FAIL] Error processing {img_path.name}: {e}")
        if person_embs:
            embeddings[person] = person_embs
            print(f"   [OK] {len(person_embs)} embedding(s) saved for {person}")
    return embeddings


def build_parser(defaults: Settings) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Facial Recognition System (layered, local)")
    parser.add_argument("--threshold", type=float, default=defaults.threshold, help="Recognition cosine threshold")
    parser.add_argument("--min-margin", type=float, default=defaults.min_margin, help="Top1-top2 margin to accept")
    parser.add_argument("--min-det-score", type=float, default=defaults.min_det_score, help="Min detection score")
    parser.add_argument("--topk", type=int, default=defaults.topk, help="Print top-k matches per face")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild embeddings from data/known_people/")
    parser.add_argument(
        "--calibrate",
        action="store_true",
        help="Auto-calibrate threshold/min-margin from stored embeddings (uses GD/SGD/Momentum/Adam)",
    )
    parser.add_argument("--calib-optimizer", type=str, default="adam", help="gd|sgd|momentum|adam (default: adam)")
    parser.add_argument("--calib-steps", type=int, default=300, help="Calibration steps (default: 300)")
    parser.add_argument(
        "--train-logistic",
        action="store_true",
        help="Train a logistic calibrator via backprop (needs some people with >=2 photos)",
    )
    parser.add_argument("--logistic-optimizer", type=str, default="adam", help="gd|sgd|momentum|adam (default: adam)")
    parser.add_argument(
        "--train-q-policy",
        action="store_true",
        help="Train a Q-learning threshold policy from similarities (needs some people with >=2 photos)",
    )
    return parser


def run(argv: list[str] | None = None) -> int:
    # Carga automática de .env si existe (para usar el env directamente).
    load_dotenv(".env", override=False)

    from src.config.settings import Settings

    defaults = Settings.from_env()
    parser = build_parser(defaults)
    args = parser.parse_args(argv)

    print("=== Facial Recognition System ===\n")

    data_layer = DataLayer(data_root=defaults.data_root, allow_flat_known_people=defaults.allow_flat_known_people)
    preprocessor = PreprocessingLayer()
    extractor = FeatureExtractionLayer(
        model_name=defaults.model_name,
        model_root=defaults.model_root,
        det_size=defaults.det_size,
    )
    inference = InferenceLayer(metric=defaults.metric)
    postprocess = PostprocessingLayer(threshold=args.threshold, min_margin=args.min_margin)
    storage = StorageLayer(data_layer.get_embedding_storage_path())
    output = OutputLayer()

    embeddings = storage.load()
    if args.rebuild or not embeddings:
        print("Generating embeddings from known_people...\n")
        embeddings_v1 = register_known_people(
            data_layer,
            preprocessor,
            extractor,
            min_det_score=args.min_det_score,
        )
        if embeddings_v1:
            storage.save(embeddings_v1)
            embeddings = storage.load()
            print(f"\n[SAVE] Embeddings saved to {storage.storage_path}\n")
    else:
        print(f"[LOAD] Embeddings loaded from {storage.storage_path}\n")
        if isinstance(embeddings, dict) and "people" not in embeddings:
            print("[MIGRATE] Upgrading embeddings.json to v2 (normalized + prototypes)...\n")
            storage.save(embeddings)
            embeddings = storage.load()
            print(f"[MIGRATE] Saved upgraded embeddings to {storage.storage_path}\n")

    if args.calibrate and embeddings:
        pos, neg = sample_similarity_pairs(embeddings, max_pairs=2000, seed=0)
        if len(pos) < 5:
            print("[CALIBRATE] Not enough positive pairs (need >=2 photos for some people). Skipping.\n")
        else:
            calibrator = ThresholdCalibrator(optimizer=args.calib_optimizer, lr=0.05)
            res = calibrator.fit(
                pos_sims=pos,
                neg_sims=neg,
                init_threshold=args.threshold,
                init_min_margin=args.min_margin,
                steps=args.calib_steps,
            )
            args.threshold = res.threshold
            args.min_margin = res.min_margin
            print(
                f"[CALIBRATE] threshold={res.threshold:.3f} min_margin={res.min_margin:.3f} loss={res.loss:.4f}\n"
            )

    # Backprop-based calibrator (trained from similarity pairs).
    logistic_params: tuple[np.ndarray, float] | None = None
    if args.train_logistic and embeddings:
        pos, neg = sample_similarity_pairs(embeddings, max_pairs=4000, seed=1)
        if len(pos) < 5:
            print("[LOGISTIC] Not enough positive pairs (need >=2 photos for some people). Skipping.\n")
        else:
            lc = LogisticCalibrator(optimizer=args.logistic_optimizer, lr=0.2)
            res = lc.fit(pos_sims=pos, neg_sims=neg, steps=500, seed=1)
            w = np.asarray(res.w, dtype=np.float32)
            b = float(res.b)
            logistic_params = (w, b)
            print(f"[LOGISTIC] trained w={res.w} b={res.b:.3f} loss={res.loss:.4f}\n")

    # Q-learning policy training (learns per-similarity-bin threshold offsets).
    q_policy = None
    policy_store = PolicyStore(Path(defaults.q_policy_path))
    if args.train_q_policy and embeddings:
        pos, neg = sample_similarity_pairs(embeddings, max_pairs=4000, seed=2)
        if len(pos) < 5:
            print("[Q-LEARNING] Not enough positive pairs (need >=2 photos for some people). Skipping.\n")
        else:
            trainer = QThresholdPolicyTrainer(n_bins=20)
            res = trainer.fit(pos, neg, base_threshold=args.threshold, episodes=3000, seed=2)
            policy_store.save_q_policy(QPolicyOnDisk(q_table=res.q_table, bin_edges=res.bin_edges, actions=res.actions))
            q_policy = policy_store.load_q_policy()
            print(f"[Q-LEARNING] policy saved to {defaults.q_policy_path}\n")
    else:
        q_policy = policy_store.load_q_policy()

    unknown_images = data_layer.list_unknown_images()
    if not unknown_images:
        print("No images found in data/unknown/ to recognize.")
        return 0

    for img_path in unknown_images:
        print(f"Recognizing: {img_path.name}")
        try:
            rgb = preprocessor.process(img_path)
            faces = extractor.extract_all(rgb, min_det_score=args.min_det_score)
            if not faces:
                print("   [WARN] No face detected.\n")
                continue

            detections = []
            for idx, (emb, face_obj) in enumerate(faces, start=1):
                results = inference.compare(emb, embeddings)
                name, confidence, recognized = postprocess.decide(results)

                # Optional Q-learning: adjust effective threshold based on similarity bin.
                if q_policy is not None and results:
                    sim = float(results[0][1])
                    bin_edges = np.asarray(q_policy.bin_edges, dtype=np.float32)
                    state = int(np.digitize([sim], bin_edges)[0] - 1)
                    state = max(0, min(len(q_policy.q_table) - 1, state))
                    q_row = np.asarray(q_policy.q_table[state], dtype=np.float32)
                    action_idx = int(np.argmax(q_row))
                    offset = float(q_policy.actions[action_idx])
                    effective_threshold = float(args.threshold + offset)
                    recognized = (confidence >= effective_threshold) and recognized

                # Optional backprop calibrator: turn similarity into probability and use it as extra gate.
                if logistic_params is not None and results:
                    sim = float(results[0][1])
                    x = np.asarray([sim, 1.0], dtype=np.float32)
                    w, b = logistic_params
                    p = 1.0 / (1.0 + float(np.exp(-(float(x @ w) + b))))
                    recognized = recognized and (p >= 0.5)

                label = f"{name}: {confidence*100:.1f}%" if (recognized and name) else f"Unknown ({confidence*100:.1f}%)"
                detections.append({"bbox": face_obj.bbox, "label": label, "recognized": recognized})

                print(f"   Face {idx}:")
                output.print_console(name, confidence, recognized)
                if args.topk > 1 and results:
                    k = min(args.topk, len(results))
                    print("   Top matches:")
                    for n, s in results[:k]:
                        print(f"     - {n}: {s*100:.2f}%")
                if (not recognized) and confidence >= (args.threshold - 0.08):
                    print(
                        f"   Tip: similarity {confidence:.3f} is close to threshold {args.threshold:.2f}. "
                        f"Try `--threshold {max(0.0, confidence - 0.01):.2f}` (and/or lower `--min-margin`)."
                    )

            output.draw_results(img_path, detections)
            print()
        except Exception as e:
            print(f"   [FAIL] Error: {e}\n")

    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
