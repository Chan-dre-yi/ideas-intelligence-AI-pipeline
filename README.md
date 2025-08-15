# Ideas Intelligence AI Pipeline

An end-to-end pipeline to **collect**, **cluster**, **summarize**, and **visualize** crowdsourced ideas — enabling thematic insight extraction and link discovery at scale, with interactive network visualizations to help leadership efficiently explore, review, and act on emerging idea patterns — powered by locally hosted **LLMs (Ollama, Mistral, T5-small)**.

&nbsp;

### 🔍 Key Features

- **🔍 Automated Daily Ingestion**: Seamlessly collects 200+ new ideas each day from web or backend exports.
- **🔍 Smart Thematic Clustering**: Groups similar ideas using sentence embeddings and auto-tuned K-Means.
- **🔍 Generative LLM Summarization**: Uses Ollama, Mistral + T5-small to generate adaptive, theme-based summaries offline to preserve confidentiality for the data.
- **🔍 Insight Aggregation**: Tracks total votes, comments, and idea volume per cluster.
- **🔍 AI-Powered Similarity Linking**: Detects semantic relationships between ideas (using an internal Gen AI API endpoint, can be modified to use the local LLMs too).
- **🔍 Interactive Network Visualization**: Renders a searchable, clickable graph of idea connections using Dash.

&nbsp;

### 🛠 Built With

- **🛠 Python**: pandas, scikit-learn, sentence-transformers, plotly, networkx, Dash  
- **🛠 LLMs**: Ollama + T5-small (for theme summarization)  
- **🛠 API**: Internal AI similarity engine  
- **🛠 Data I/O**: CSV, Excel, Pickle 

&nbsp;

### 📊 Preview

Below are snapshots from a full run of the pipeline on one idea group. These examples illustrate both the **clustered themes** and the **interactive graph visualizations** that enable intuitive exploration and review.

&nbsp;

#### 📊 Theme Clusters for One Group

<img width="1919" height="1129" alt="Theme Clusters" src="https://github.com/user-attachments/assets/32f5464d-a1cb-4532-9318-28fb4e836efe" />

&nbsp;

#### 📊 Summary of One Theme

<img width="1919" height="1124" alt="Theme Summary" src="https://github.com/user-attachments/assets/52772994-17ed-48fe-bbe1-723e504bc909" />

---
&nbsp;

#### 🌐 Idea Relationship Network

##### 🌐🔵 Hover (Blue)

<img width="1919" height="1055" alt="Hover Blue" src="https://github.com/user-attachments/assets/f7ad17fa-9d85-456e-964f-ae41ff67d6da" />

&nbsp;

##### 🌐🔴 Click (Red)

<img width="1923" height="1055" alt="Click Red" src="https://github.com/user-attachments/assets/4beb886e-5076-4b15-b83b-05d143e5a7d3" />

&nbsp;

##### 🌐🟡 Hover on Related Idea (Yellow)

<img width="1919" height="1136" alt="Hover Yellow" src="https://github.com/user-attachments/assets/c1a1c77b-b224-4b73-bd85-62eff3d54251" />

---

&nbsp;

 ### 📌 Pipeline Overview

#### **📌 1. Data Ingestion**

> _Scripts: `ideas_web_scraper.py` → Inputs: credentials, links, and output file name | OR use exported file: `ideasPBI.csv`_

- **Web Scraping:** Scrape hundreds of idea pages using a headless browser (`ideas_web_scraper.py`).
- **Backend Import:** Alternatively, use a pre-exported backend file (`ideasPBI.csv`) for faster processing.


#### **📌 2. Thematic Clustering & Summarization (use_case_1)**

> _Script: `ideas_new_pipeline.py`  → Inputs: input file name, group filtering, and output file names (for each run) → Output: (depends what you name each file) → Merged: `thematic_summary.xlsx`_

Cluster ideas using Sentence Transformers and K-Means, and summarize each theme with Ollama + T5-small.

- Filter by user-defined groups
- Embed ideas and cluster them (auto-selecting optimal `k`)
- Generate cluster names and summaries using LLMs adaptively
- Output aggregated summaries per group, which can be merged into `thematic_summary.xlsx`


#### **📌 3. Idea Relationship Visualization (use_case_2)**

> _Script: `AI_parser.py` → Inputs: ideas base file, and AI API URL → Outputs: `ideas_with_similarities.xlsx`, `processed_ids.txt`, `results_checkpoint.pkl`_

> _Script: `network_viz.py` → Input: `ideas_with_similarities.xlsx` → Output: Dash app at `127.0.0.1:8050`_

Map relationships between similar ideas using an internal AI API and visualize them as an interactive network.

- Map similar ideas
- Visualize relationships with NetworkX + Dash

---


&nbsp;


### 🚀 Getting Started

Follow these steps to run the full pipeline from idea ingestion to clustering and visualization.


#### 🚀 Step 1: Collect Ideas

Run the web scraper with required inputs 
- supply the required credentials, links, and output file name to this script

```bash
python ideas_web_scraper.py
```
This will save scraped ideas into ideas_raw.csv. Alternatively, skip scraping and directly use the backend export if you have it. (`ideasPBI.csv`)

#### 🚀 Step 2: Run Theme-Based Clustering (Use Case 1)

Run clustering and summarization for each group
- Make sure you change the input file name, group filtering, and output file names before you run.
- Filtered groups are passed one at a time.
- Output files are generated per group.
  
```bash
python use_case_1/ideas_pipeline_one.py
```
- After processing all groups, merge them into a single file (e.g. `thematic_summary.xlsx`) as a consolidated result.

#### 🚀 Step 3: Generate Idea Similarities (Use Case 2)

Run the similarity mapping script
- modify the the ideas base file, and AI API URL before running

```bash
python use_case_2/AI_parser.py 
```
- this will generate the file `ideas_with_similarities.xlsx`, 
- along with `processed_ids.txt` and  `results_checkpoint.pkl` if it needs to be done in batches.

#### 🚀 Step 4: Visualize Idea Network

Use the generated similarity data to create an interactive network graph using Dash

```bash
python use_case_2/network_viz.py
```
- the network visualization will be available at `http://127.0.0.1:8050`.

---



&nbsp;

### 📁 Key Files

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


&nbsp;

### ​ ❓ FAQ

#### ❓ Why not just use the internal ChatGPT API for this?
- *We **did use the internal ChatGPT API** for similarity linking. But on its own, it couldn't **automate ingestion, clustering, or visualization**. The pipeline transforms Gen AI into a **repeatable, structured system at scale**, adaptively combining ChatGPT with models like **T5-small** (for summarization) and **Mistral** (for efficiency) to ensure both **accuracy** and **scalability**.*

---

#### ❓ Why not stick with CSV/ Excel or use SQL, instead of Neo4j?
- *CSV/Excel and SQL work for early prototyping, but as idea volume and links grew, multi-hop queries became **cumbersome** and error-prone. **Neo4j** was the **clear next step**—it stores **nodes and relationships natively**, supports **real-time visualization**, and runs **graph algorithms** (like community detection). While integration was halted due to a **re-org**, its use would have made the pipeline **faster, more maintainable**, and turned reviews from **weeks into instant, interactive exploration**.*

---

#### ❓ What was the real-world impact?
- *Review time dropped from **2–3 weeks to just 2–3 days**. Leadership gained instant visibility into **duplicates, themes, and clusters**, eliminating manual sifting. The tool enabled **one-click approval** of AI-suggested links, replacing **weeks of manual effort** with mere seconds—boosting both **engagement** and **decision speed**.*

---

#### ❓ How did you ensure reliability and enterprise readiness?
- *All tech choices—from model selection to clustering strategy—were **continuously reviewed by ultra-senior mentors (with 25–30 years of experience)**. This oversight ensured the solution was **practical, scalable, and aligned with enterprise standards**, not just a one-off experiment.*

---

#### ❓ Why not use a conventional search or dashboard tool?
- *Traditional BI tools or dashboards aren’t built for **semantic clustering**, **relationship mapping**, or **theme-based summarization**. Our solution uniquely combines **LLM summarization**, **sentence embeddings**, and **interactive network visuals**, offering leadership a **dynamic and insightful way** to explore employee ideas.*

---

#### ❓ What’s the project’s scalability roadmap?
- *The architecture is designed for modular growth:  **a. Neo4j integration** for scalable graph storage and querying  **b. Expanded AI models** for richer summarization/embedding  **c. Pipeline automation** for real-time idea ingestion and analysis. Even though the project was de-emphasized, it was clearly structured for future scaling and enterprise adoption.*

---
