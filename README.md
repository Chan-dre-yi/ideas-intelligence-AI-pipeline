# 💡 Ideas Intelligence Pipeline

An end-to-end pipeline to **collect**, **cluster**, **summarize**, and **visualize** crowdsourced ideas — enabling thematic insight extraction and link discovery at scale, with interactive network visualizations to help leadership efficiently explore, review, and act on emerging idea patterns — powered by locally hosted LLMs (Ollama, T5-small).

---

## 🔧 Tech Stack

- **Python**: pandas, scikit-learn, sentence-transformers, plotly, networkx, Dash  
- **LLMs**: Ollama + T5-small (for theme summarization)  
- **API**: Internal AI similarity engine  
- **Data I/O**: CSV, Excel, Pickle 
---

## 📌 Pipeline Overview

### **1. Data Collection**

> _Script: `ideas_parser.py`_

> _CSV: `ideasPBI.csv`_

- **Auto-Pilot Scraping** (`ideas_parser.py`):  
  Scrapes ideas from a website across hundreds of pages using an automated, headless browser setup.
  
- **Backend Data Access** (`ideasPBI.csv`):  
  Alternative or eventual approach via direct export from the backend database for faster, more reliable ingestion.


### 2. use_case_1: Thematic Clustering & Adaptive Summarization

> _Script: `ideas_new_pipeline.py` → Output: `thematic_summary.xlsx`_

Apply K-Means clustering on idea embeddings to surface core themes and generate smart summaries using lightweight LLMs.

#### **Steps**
- **Filter** ideas based on user-assigned groups.
- **Embed** idea text using Sentence Transformers.
- **Cluster** with K-Means — optimal `k` is auto-determined.
- **Generate Theme Names** using:
   - Top keywords from each cluster.
   - A prompt sent to **Ollama + T5-small** for adaptive summarization.
- **Aggregate Insights**:
   - Sum of votes, comment counts, and idea frequency per theme.
- **Export Results** to `thematic_summary.xlsx`.


### 3. use_case_2: Visualizing Idea Relationships

> _Scripts: `AI_parser.py`, `network_viz.py` → Output: `ideas_with_similarities.xlsx`, Dash app at `127.0.0.1:8050`_

Discover hidden connections between ideas using an internal AI similarity API and visualize their relationships as a network.

#### **Steps**
- **Create Linkage Dataset** (`AI_parser.py`):
   - Loop through all idea pairs.
   - Use internal AI API to find similar ideas.
   - Save results as `ideas_with_similarities.xlsx`.
   - Progress tracked using `processed_ids.txt` and `results_checkpoint.pkl`.

- **Visualize Network** (`network_viz.py`):
   - Use **NetworkX** and **Plotly Dash** to render an interactive graph.
   - Nodes represent ideas; edges show semantic similarity.
   - Launched locally at: `http://127.0.0.1:8050/`

---

## 📁 Key Files

| File                         | Description                                      |
|------------------------------|--------------------------------------------------|
| `ideas_parser.py`            | Auto-scrapes ideas from web pages                |
| `ideasPBI.csv`               | Backend export of ideas (alternative to scraping)|
| `ideas_new_pipeline.py`      | Performs clustering, summarization               |
| `thematic_summary.xlsx`      | Output summary of clustered themes               |
| `AI_parser.py`               | Generates similarity scores using internal API   |
| `ideas_with_similarities.xlsx` | Relationship dataset                          |
| `processed_ids.txt`          | Tracking file for API parsing progress           |
| `results_checkpoint.pkl`     | Intermediate results checkpoint                  |
| `network_viz.py`             | Visualizes idea connections with NetworkX + Dash |
| `127.0.0.1:8050`             | Local Dash app for exploring the graph           | 

---

## 🚀 Getting Started (Optional)

> Coming soon — setup instructions, environment config, and usage examples.







---

## 🖼️ Final Results

Below are snapshots from a full run of the pipeline on one idea group. These examples illustrate both the **clustered themes** and the **interactive graph visualizations** that enable intuitive exploration and review.

### 📊 Theme Clusters for One Group

<img width="1919" height="1129" alt="Theme Clusters" src="https://github.com/user-attachments/assets/32f5464d-a1cb-4532-9318-28fb4e836efe" />

---

### 📝 Summary of One Theme

<img width="1919" height="1124" alt="Theme Summary" src="https://github.com/user-attachments/assets/52772994-17ed-48fe-bbe1-723e504bc909" />

---

### 🧠 Idea Relationship Network

#### 🔵 Hover (Blue)

<img width="1919" height="1055" alt="Hover Blue" src="https://github.com/user-attachments/assets/f7ad17fa-9d85-456e-964f-ae41ff67d6da" />

#### 🔴 Click (Red)

<img width="1923" height="1055" alt="Click Red" src="https://github.com/user-attachments/assets/4beb886e-5076-4b15-b83b-05d143e5a7d3" />

#### 🟡 Hover on Related Idea (Yellow)

<img width="1919" height="1136" alt="Hover Yellow" src="https://github.com/user-attachments/assets/c1a1c77b-b224-4b73-bd85-62eff3d54251" />

