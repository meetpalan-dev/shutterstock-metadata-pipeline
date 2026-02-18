# 📷 Shutterstock CSV Generator (Offline AI)

Automatically generates Shutterstock upload metadata from images using a local AI model.

No API  
No credits  
Runs fully offline after first setup

---

## What it does

This script prepares images for Shutterstock submission automatically.

It will:

• Filter images under 4MP  
• Detect duplicates  
• Generate AI description  
• Generate 20–50 keywords  
• Suggest categories  
• Create upload CSV ready for Shutterstock

---

## Folder Structure

```
project/
│
├── main.py
│
├── images/            ← put your images here
├── images_valid/      ← accepted images
├── too_small/         ← rejected images (<4MP)
├── duplicates/        ← duplicate files
├── videos/            ← unsupported files
│
└── shutterstock_content_upload.csv
```

All folders are created automatically if missing.

---

## Installation

Install dependencies:

```
pip install pillow transformers torch tqdm
```

---

## First Run (Model Download)

Run once with internet:

```
python main.py
```

The AI model will download (~1GB)

After that → works fully offline

---

## Usage

1) Put images into:

```
images/
```

2) Run:

```
python main.py
```

3) Upload generated CSV to Shutterstock

---

## Output

Creates:

```
shutterstock_content_upload.csv
```

You upload this file in the Shutterstock contributor panel.

---

## Notes

Best suited for:

• textures
• nature
• objects
• backgrounds

People/editorial content should be reviewed manually.

---

## License
MIT
