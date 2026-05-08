from pathlib import Path
from src.layers.data_layer import DataLayer
from src.layers.preprocessing_layer import PreprocessingLayer
from src.layers.feature_extraction_layer import FeatureExtractionLayer
from src.layers.inference_layer import InferenceLayer
from src.layers.postprocessing_layer import PostprocessingLayer
from src.layers.storage_layer import StorageLayer
from src.layers.output_layer import OutputLayer

def register_known_people(data_layer: DataLayer, preprocessor: PreprocessingLayer, extractor: FeatureExtractionLayer, storage: StorageLayer):
    known_people = data_layer.list_known_people()
    if not known_people:
        print("[WARN] No known people found in data/known_people/")
        return {}

    embeddings = {}
    for person in known_people:
        images = data_layer.list_images_for_person(person)
        person_embs = []
        for img_path in images:
            print(f"Registering {person} - {img_path.name}")
            try:
                rgb = preprocessor.process(img_path)
                emb, _ = extractor.extract_primary(rgb)
                if emb is not None:
                    person_embs.append(emb)
                else:
                    print(f"   [WARN] No face detected in {img_path.name}")
            except Exception as e:
                print(f"   [FAIL] Error processing {img_path.name}: {e}")
        if person_embs:
            embeddings[person] = person_embs
            print(f"   [OK] {len(person_embs)} embedding(s) saved for {person}")
    return embeddings

def main():
    print("=== Facial Recognition System ===\n")

    data_layer = DataLayer()
    preprocessor = PreprocessingLayer()
    extractor = FeatureExtractionLayer(model_root=".")
    inference = InferenceLayer(metric="cosine")
    postprocess = PostprocessingLayer(threshold=0.80, min_margin=0.03)
    storage = StorageLayer(data_layer.get_embedding_storage_path())
    output = OutputLayer()

    embeddings = storage.load()
    if not embeddings:
        print("No previous embeddings found. Generating from known_people...\n")
        embeddings = register_known_people(data_layer, preprocessor, extractor, storage)
        if embeddings:
            storage.save(embeddings)
            print(f"\n[SAVE] Embeddings saved to {storage.storage_path}\n")
    else:
        print(f"[LOAD] Embeddings loaded from {storage.storage_path}\n")

    unknown_images = data_layer.list_unknown_images()
    if not unknown_images:
        print("No images found in data/unknown/ to recognize.")
        return

    for img_path in unknown_images:
        print(f"Recognizing: {img_path.name}")
        try:
            rgb = preprocessor.process(img_path)
            faces = extractor.extract_all(rgb, min_det_score=0.5)
            if not faces:
                print("   [WARN] No face detected.\n")
                continue

            detections = []
            for idx, (emb, face_obj) in enumerate(faces, start=1):
                results = inference.compare(emb, embeddings)
                name, confidence, recognized = postprocess.decide(results)

                label = f"{name}: {confidence*100:.1f}%" if (recognized and name) else f"Unknown ({confidence*100:.1f}%)"
                detections.append({"bbox": face_obj.bbox, "label": label, "recognized": recognized})

                print(f"   Face {idx}:")
                output.print_console(name, confidence, recognized)

            output.draw_results(img_path, detections)
            print()
        except Exception as e:
            print(f"   [FAIL] Error: {e}\n")

if __name__ == "__main__":
    main()
