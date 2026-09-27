license: mit
pretty_name: Synthetic Manuscript Generator
tags:
  - synthetic-data
  - historical-manuscript
  - handwriting
  - devanagari
  - modi
  - sharada
configs:
  - config_name: devanagari
    data_dir: devanagari
  - config_name: modi
    data_dir: modi
  - config_name: sharada
    data_dir: sharada
---

# Synthetic Manuscript Generator

An automated Python pipeline...
# Synthetic Manuscript Generator

An automated Python pipeline for generating realistic synthetic historical manuscript folio images from raw Unicode text, together with synchronized Markdown transcription annotations.

The system is designed to generate manuscript-style data for three Indic scripts:

- Devanagari
- Modi
- Sharada

Each generated image is paired with a `.md` annotation containing metadata and the original Unicode transcription.

---

## 1. Project Overview

Historical manuscript datasets are often limited because genuine manuscripts can be difficult to collect, digitize, annotate, and distribute at scale.

This project provides a configurable synthetic data generation pipeline that creates manuscript-like folio images from raw Unicode source text.

The pipeline combines:

- Historical manuscript-style backgrounds
- Aged paper and palm-leaf textures
- Natural surface imperfections
- Unicode script rendering
- Handwriting-style variations
- Ink color variation
- Ink fading
- Smudging and bleeding
- Text layout variation
- Highlighted passages
- Marginal text
- Multiple text blocks
- Synchronized Markdown annotations

The generated dataset contains exactly 100 images for each supported script.

---

# 2. Supported Scripts

The generator currently supports:

| Script | Unicode | Dataset Size |
|---|---|---:|
| Devanagari | Yes | 100 |
| Modi | Yes | 100 |
| Sharada | Yes | 100 |

Total generated images:

**300 manuscript images**

Each image has one corresponding Markdown annotation file.

Total annotations:

**300 `.md` files**

---

# 3. Dataset Split

Each script is divided into:

| Split | Images per Script |
|---|---:|
| Train | 85 |
| Validation | 10 |
| Test | 5 |
| **Total** | **100** |

Therefore:

- Training images: 255
- Validation images: 30
- Test images: 15
- Total images: 300

---

# 4. Key Features

## Manuscript Background Generation

The system generates manuscript-style backgrounds including:

- Aged handmade paper
- Palm-leaf style surfaces
- Natural paper grain
- Fine and coarse texture
- Visible fibers
- Age spots
- Surface stains
- Darkened edges
- Folds and creases
- Surface aging
- Natural color variation
- Warping and curling effects

---

## Unicode Text Rendering

The system preserves the original Unicode transcription.

Supported scripts include:

- Devanagari
- Modi
- Sharada

The configured font is loaded separately for each script.

This allows the same rendering pipeline to support multiple Indic writing systems.

---

## Handwriting Variation

The rendering pipeline introduces controlled variations such as:

- Slight character slant
- Baseline variation
- Horizontal jitter
- Vertical jitter
- Character spacing variation
- Text waviness
- Stroke variation

These variations help avoid perfectly uniform computer-rendered text.

---

## Ink Effects

The generated manuscript text can contain:

- Natural ink color variation
- Variable opacity
- Faded strokes
- Ink smudging
- Ink bleeding
- Slight blur
- Stroke intensity variation

Multiple dark brown ink tones are used to simulate naturally aged writing.

---

## Layout Variation

The layout engine supports:

- Multiple text blocks
- Variable number of lines
- Line spacing variation
- Horizontal jitter
- Vertical jitter
- Marginal text
- Highlighted passages
- Different text positions
- Boundary protection

The renderer measures text using the actual configured font before placing it on the manuscript.

---

# 5. Pipeline

The overall generation pipeline is:

```text
Raw Unicode Source Text
          |
          v
     Text Loader
          |
          v
   Text Chunk Selection
          |
          v
 Manuscript Background
          |
          v
      Layout Engine
          |
          v
    Unicode Renderer
          |
          v
   Handwriting Effects
          |
          v
      Ink Effects
          |
          v
   Boundary Validation
          |
          v
     PNG Manuscript
          |
          +------------------+
          |                  |
          v                  v
      Image File       Markdown File
                         Annotation