# Academic Vibe Check 🧠

**A Neuro-Symbolic AI System for Early Academic Risk Detection & Psychosocial Monitoring.**

This repository contains the full source code for a hybrid AI system that combines **Machine Learning (XGBoost)** with **Knowledge Representation & Reasoning (Fuzzy Logic)** to assess student academic risks. The system features a gamified "Vibe Check" frontend to reduce test anxiety and improve data veracity.

Aligned with **SDG 4: Quality Education** and **SDG 3: Good Health and Well-being**.

## 📂 Contents

* **`advisor-engine/`**: The Gamified Application used to predict at-risk students
* **`data/`**: The Data used to train the model
* **`documentation/`**: PDFs and Guides
* **`models/`**: Models that are the drafts and the release
* **`notebooks/`**: Jupyter Notebooks
* **`video/`**: Video Presentation

## 🚀 Key Features

* **Hybrid Intelligence:** Uses XGBoost for grade prediction and Fuzzy Logic for psychosocial reasoning (e.g., the "Buffering Effect" of teacher support).
* **Gamified Interface:** Replaces boring surveys with an emoji-based "BuzzFeed-style" quiz.
* **Real-time Diagnostics:** Provides immediate, explainable feedback on Math Anxiety, Belonging, and Digital Poverty.
* **Production Ready:** Dockerized architecture serving Vue static files via Python FastAPI.

## ⚡ Quick Start (Recommended: Docker)

The easiest way to run the full system (Frontend + Backend) is using Docker.

```bash
cd advisor-engine

# 1. Build the image
docker build -t advisor-app .

# 2. Run the container
docker run -p 8000:8000 advisor-app
```

## ⚡ Quick Start (Jupyter Notebooks)
* Open `notebooks/DPS_At_Risk_Student_Data_Filtering.ipynb` to download and ready the data (Filter it to just Use PH Data, Impute Missing Fields)
* Open `notebooks/DPS_Data_Exploration.ipynb` to explore the data
* Open `notebooks/DPS_Model_Training.ipynb` to train the model
