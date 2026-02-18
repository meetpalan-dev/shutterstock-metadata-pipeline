# ============================================================
# SHUTTERSTOCK AUTO METADATA PIPELINE (OFFLINE SAFE)
# ============================================================

# -------- FORCE OFFLINE MODE (MUST BE FIRST) ----------------
import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

# ------------------------------------------------------------
import csv
import re
import time
import shutil
import hashlib
from PIL import Image
from tqdm import tqdm
from transformers import BlipProcessor, BlipForConditionalGeneration

# ================= CONFIG ===================================

SOURCE_DIR = "images"
VALID_DIR = "images_valid"
SMALL_DIR = "too_small"
DUP_DIR = "duplicates"

OUTPUT_CSV = "shutterstock_content_upload.csv"

MIN_PIXELS = 4_000_000
MIN_KEYWORDS = 20
MIN_DESC_WORDS = 10

IMAGE_EXTS = (".jpg", ".jpeg", ".png")

# ================= STOPWORDS ================================

STOPWORDS = {
    "a","an","the","and","or","but","so","yet",
    "of","in","on","at","by","for","to","from","with","without",
    "this","that","these","those","it","its","their","his","her",
    "is","are","was","were","be","been","being",
    "has","have","had","do","does","did",
    "photo","photograph","photography","image","picture",
    "shot","capture","captured",
    "high","quality","best","beautiful","nice",
    "scene","view","perspective","angle",
    "background","foreground",
    "", " "
}

# ================= CATEGORIES ===============================

VALID_CATEGORIES = [
    "Abstract","Animals/Wildlife","Arts","Backgrounds/Textures",
    "Beauty/Fashion","Buildings/Landmarks","Business/Finance",
    "Education","Food and drink","Healthcare/Medical","Holidays",
    "Industrial","Interiors","Nature","Objects","Parks/Outdoor",
    "People","Religion","Science","Signs/Symbols",
    "Sports/Recreation","Technology","Transportation","Vintage"
]

CATEGORY_RULES = {
    "flower": ["Nature","Parks/Outdoor"],
    "plant": ["Nature","Objects"],
    "animal": ["Animals/Wildlife","Nature"],
    "bird": ["Animals/Wildlife","Nature"],
    "person": ["People","Objects"],
    "face": ["People","Objects"],
    "temple": ["Buildings/Landmarks","Religion"],
    "building": ["Buildings/Landmarks","Objects"],
    "firework": ["Holidays","Parks/Outdoor"],
    "texture": ["Backgrounds/Textures","Abstract"],
}

# ================= UTILS ===================================

def clean_text(text):
    text = re.sub(r"[^a-zA-Z0-9 ]+", "", text.lower())
    return text.strip()

def is_copy_name(filename):
    name = filename.lower()
    return (
        "copy" in name
        or re.search(r"\(\d+\)", name)
        or re.search(r"-\d+$", name)
    )

def image_md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

# ================= FILTERING ================================

def filter_images():
    os.makedirs(VALID_DIR, exist_ok=True)
    os.makedirs(SMALL_DIR, exist_ok=True)

    valid = small = errors = 0

    print("\nFiltering images...")

    for f in os.listdir(SOURCE_DIR):
        path = os.path.join(SOURCE_DIR, f)

        if not f.lower().endswith(IMAGE_EXTS):
            continue

        try:
            with Image.open(path) as img:
                w, h = img.size
                pixels = w * h

            if pixels < MIN_PIXELS:
                shutil.move(path, os.path.join(SMALL_DIR, f))
                small += 1
            else:
                shutil.move(path, os.path.join(VALID_DIR, f))
                valid += 1

        except Exception:
            errors += 1

    print("✔ Filtering completed")
    print(f"✔ Valid images: {valid}")
    print(f"✖ Too small (<4MP): {small}")
    print(f"✔ No errors" if errors == 0 else f"⚠ Errors: {errors}")

# ================= DUPLICATES ===============================

def remove_duplicates():
    os.makedirs(DUP_DIR, exist_ok=True)

    hash_map = {}
    removed = 0

    print("\nChecking duplicates...")

    for f in os.listdir(VALID_DIR):
        path = os.path.join(VALID_DIR, f)

        if not f.lower().endswith(IMAGE_EXTS):
            continue

        try:
            h = image_md5(path)

            if h not in hash_map:
                hash_map[h] = f
                continue

            existing = hash_map[h]

            # Decide which one to KEEP
            # Rule: keep original-looking name, move copy-looking name
            if is_copy_name(f) and not is_copy_name(existing):
                shutil.move(path, os.path.join(DUP_DIR, f))
                removed += 1
            elif not is_copy_name(f) and is_copy_name(existing):
                shutil.move(os.path.join(VALID_DIR, existing),
                            os.path.join(DUP_DIR, existing))
                hash_map[h] = f
                removed += 1
            else:
                # fallback: move newer file
                shutil.move(path, os.path.join(DUP_DIR, f))
                removed += 1

        except Exception as e:
            print(f"⚠ Duplicate check error on {f}: {e}")

    if removed:
        print(f"✔ Duplicates removed: {removed}")
    else:
        print("✔ No duplicates found")

# ================= BLIP (OFFLINE) ===========================

print("\nLoading BLIP model (offline)...")

processor = BlipProcessor.from_pretrained(
    "Salesforce/blip-image-captioning-base",
    local_files_only=True,
    use_fast=False
)

model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base",
    local_files_only=True
)

# ================= METADATA ================================

def generate_caption(image):
    inputs = processor(image, return_tensors="pt")
    out = model.generate(**inputs, max_length=40)
    return processor.decode(out[0], skip_special_tokens=True)

def build_description(caption):
    caption = clean_text(caption)
    words = caption.split()

    if len(words) < MIN_DESC_WORDS:
        caption += " natural outdoor environment with realistic visual detail"

    return caption.capitalize()

def extract_keywords(caption):
    words = clean_text(caption).split()
    keywords = [w for w in words if w not in STOPWORDS]

    enrich = [
        "natural","outdoor","texture","detail","environment",
        "realistic","scenic","composition","visual","surface"
    ]

    for e in enrich:
        if e not in keywords:
            keywords.append(e)

    filler = [
        "aesthetic","documentation","travel","design",
        "material","context","pattern","background"
    ]

    for f in filler:
        if len(keywords) >= MIN_KEYWORDS:
            break
        keywords.append(f)

    return keywords[:50]

def choose_categories(text):
    text = text.lower()
    for key, cats in CATEGORY_RULES.items():
        if key in text:
            return cats[:2]
    return ["Objects","Nature"]

# ================= MAIN ====================================

filter_images()
remove_duplicates()

images = [f for f in os.listdir(VALID_DIR) if f.lower().endswith(IMAGE_EXTS)]

rows = []

print(f"\nGenerating metadata for {len(images)} images\n")

for img_name in tqdm(images, ncols=80):
    path = os.path.join(VALID_DIR, img_name)
    image = Image.open(path).convert("RGB")

    caption = generate_caption(image)
    description = build_description(caption)
    keywords = extract_keywords(caption)
    cat1, cat2 = choose_categories(caption)

    rows.append([
        img_name,
        description,
        cat1,
        cat2,
        ", ".join(keywords)
    ])

# ================= CSV =====================================

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Filename","Description","Category 1","Category 2","Keywords"])
    writer.writerows(rows)

print("\n✔ DONE — Shutterstock CSV ready")
