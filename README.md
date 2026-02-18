# 📦 Shutterstock Metadata Pipeline

Generate Shutterstock-ready metadata (description, keywords, categories) automatically using an offline AI caption model.

This tool scans a folder of images, filters unusable files, removes duplicates, generates captions, and exports a ready-to-upload CSV.

No API  
No internet required after setup  
No manual tagging pain

---

## 🧠 What it does

### Input
```
images/
    photo1.jpg
    photo2.png
    DSC_1234.jpeg
```

### Pipeline
1. Filters images smaller than 4MP
2. Removes duplicate files using hash comparison
3. Generates AI captions (BLIP offline model)
4. Converts caption → description
5. Extracts 20–50 keywords automatically
6. Chooses Shutterstock categories
7. Exports CSV ready for upload

### Output
```
outputs/shutterstock_upload.csv
```

Upload this CSV directly to Shutterstock contributor panel.

---

## 🗂 Folder structure

```
shutterbot/
│
├── main.py
├── requirements.txt
├── images/              # Put raw images here
├── images_valid/        # Auto filtered valid images
├── too_small/           # Rejected (<4MP)
├── duplicates/          # Duplicate files moved here
└── outputs/
    └── shutterstock_upload.csv
```

---

## ⚙️ Installation

### 1. Install Python
Python 3.10+ recommended

### 2. Install dependencies
```
pip install -r requirements.txt
```

---

## 🤖 Download AI model (ONE TIME ONLY)

Run this once while internet is ON:

```
python -c "from transformers import BlipProcessor, BlipForConditionalGeneration; BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base'); BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base')"
```

After this the script works fully offline.

---

## 🚀 Usage

Put images inside:

```
images/
```

Then run:

```
python main.py
```

---

## 📄 Output CSV Format

| Filename | Description | Category 1 | Category 2 | Keywords |
|--------|-------|-------|-------|-------|
| image1.jpg | Natural green plant growing outdoors | Nature | Objects | plant, leaf, natural, texture... |

Upload this CSV in Shutterstock bulk uploader.

---

## 🧩 How keywords are generated

The script:
- Cleans caption text
- Removes stopwords
- Adds commercial stock keywords
- Ensures minimum keyword count
- Limits to 50 keywords (Shutterstock limit)

No ChatGPT required. No paid APIs.

---

## 🛠 Why this exists

Manual tagging hundreds of photos is slow and painful.

This tool was built to:
- Speed up stock uploads
- Stay offline
- Avoid monthly AI costs
- Keep workflow simple

---

## ⚠️ Notes

- People photos may still require manual model release
- AI captions are not perfect — review before uploading large batches
- Works best for nature, objects, textures, architecture

---

## 📜 License
MIT — use freely
