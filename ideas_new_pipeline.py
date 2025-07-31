'''
This script reads the ideas data file, and processes it,
Ideally for a group at a time (depending on the size of you data)
To cluster them into themes, assign theme names,
And summarise each cluster/ theme using llama and t5 small adaptively.
=> (t5 small and ollama are loaded locally.) 
'''




import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
from sklearn.metrics import silhouette_score
import numpy as np
from openpyxl import Workbook
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import ollama
import json
from tqdm import tqdm
from kneed import KneeLocator
import matplotlib.pyplot as plt




#####################
# Load data
df = pd.read_csv("ideasPBI.csv")

# Load T5-small once
tokenizer = AutoTokenizer.from_pretrained("xyz/downloadedT5small")
model = AutoModelForSeq2SeqLM.from_pretrained("xyz/downloadedT5small")
#####################



df["Ideas"] = df["Idea Name"].astype(str) + ": " + df["Description"].astype(str)
df.to_csv("ideas.csv", index=False)
df = pd.read_csv("ideas.csv")


# Step 1: Filter and reset index
# df = df[df["Segment"] == "Products"].copy().reset_index(drop=True)
df = df[df["Segment"] == "Corporate"].copy().reset_index(drop=True)
# df = df[df["Segment"] == "Foundry"].copy().reset_index(drop=True)
# df = df[df["Segment"].isna()].copy().reset_index(drop=True)
df["Ideas"] = df["Ideas"].fillna("").astype(str)
texts = df["Ideas"].tolist()

print("Step 1 done. Filtered.")



# Step 2: Load embedding model
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
embeddings = embedder.encode(texts, convert_to_tensor=False)
print("Step 2 done. Embedded sentence transformer.")



# Step 3: Find optimal number of clusters 

inertias = []
k_range = range(1, 15)

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(embeddings)
    inertias.append(kmeans.inertia_)

kneedle = KneeLocator(k_range, inertias, curve="convex", direction="decreasing")
optimal_k = kneedle.knee
print(f"Optimal number of clusters: {optimal_k}")

# Optional: Plot the elbow curve
# plt.plot(k_range, inertias, marker='o')
# plt.axvline(optimal_k, color='r', linestyle='--', label=f'Optimal k = {optimal_k}')
# plt.xlabel('Number of clusters (k)')
# plt.ylabel('Inertia')
# plt.title('Elbow Method using Inertia')
# plt.legend()
# plt.grid(True)
# plt.show()

n_clusters=optimal_k
kmeans = KMeans(n_clusters=optimal_k, random_state=42)
labels = kmeans.fit_predict(embeddings)
df["theme_cluster"] = labels
print("Step 3 done. Clustered.")




# Step 4: Generate theme names from top keywords

vectorizer = TfidfVectorizer(stop_words="english", max_features=10000)
X = vectorizer.fit_transform(df["Ideas"])
terms = vectorizer.get_feature_names_out()

theme_names = []

for i in range(n_clusters):
    # Get comments in this cluster
    cluster_indices = df[df["theme_cluster"] == i].index
    cluster_comments = X[cluster_indices]

    # Compute mean TF-IDF scores
    avg_tfidf = np.asarray(cluster_comments.mean(axis=0)).flatten()
    top_indices = avg_tfidf.argsort()[-30:][::-1]
    top_keywords = [terms[idx] for idx in top_indices]

    # Use Ollama to generate a theme from keywords
    prompt = f"""
You are a business analyst. Based on the following 30 keywords extracted from employee suggested ideas, generate one short, descriptive theme name (3-5 words max) that captures the central idea of the cluster.

Keywords:
{", ".join(top_keywords)}

Theme:
"""
    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    theme = response["message"]["content"].strip()
    theme_names.append(theme)
    print(f"Cluster {i}: {theme}")

theme_map = {i: name for i, name in enumerate(theme_names)}
df["theme"] = df["theme_cluster"].map(theme_map)

print("Step 4 done. Themes generated.")




# Step 5: Group by theme and get frequencies

grouped = df.groupby("theme").agg({
    "Ideas": list,
    "theme": "count",
    "Votes": "sum",
    "Idea Comments": "sum"
}).rename(columns={"theme": "frequency", "Votes": "SumOfVotes", "Idea Comments": "SumOfComments"}).reset_index()


print("Step 5 done. Grouped ideas by theme.")




# Step 6: Summarize grouped comments
# summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# def summarize_comments(comment_list):
#     text = " ".join(comment_list)
#     chunks = [text[i:i+1024] for i in range(0, len(text), 1024)]
#     summarized = [summarizer(chunk, max_length=40, min_length=30, do_sample=False)[0]["summary_text"]
#                   for chunk in chunks]
#     return " ".join(summarized)

# grouped["summary"] = grouped["Idea"].apply(summarize_comments)





t5_summarizer = pipeline("summarization", model=model, tokenizer=tokenizer, device=0 if torch.cuda.is_available() else -1)

# --- Helper for T5 summarization ---
def summarize_with_t5(text, max_length=120, min_length=30):
    try:
        return t5_summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)[0]['summary_text']
    except:
        return text[:max_length]  # fallback

# --- Helper for Ollama summarization ---
def summarize_with_ollama(text, model_name="mistral"):
    prompt = f"""
You are a business analyst. Summarize the following employee suggested ideas into a detailed, formal summary. Identify key concerns, suggestions, and patterns. Be concise but informative.

Ideas:
{text}

Summary:
"""
    response = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"].strip()

# --- Final Adaptive Function ---
def adaptive_summary(comment_list):
    full_text = "\n".join(comment_list)
    total_chars = len(full_text)

    if len(comment_list) <= 10 or total_chars < 2500:
        # Use Ollama directly
        summary = summarize_with_ollama(full_text)
        print(f"✔️ Ollama summarization done for group of {len(comment_list)} ideas.")
        return summary
    
    # Use T5 for chunks
    chunk_size = 4  # Adjust as needed
    t5_summaries = []
    for i in range(0, len(comment_list), chunk_size):
        chunk = "\n".join(comment_list[i:i+chunk_size])
        t5_summary = summarize_with_t5(chunk)
        t5_summaries.append(t5_summary)

    # Combine T5 summaries, summarize via Ollama
    combined = "\n".join(t5_summaries)
    summary = summarize_with_ollama(combined)
    print(f"✔️ T5 + Ollama summarization done for group of {len(comment_list)} ideas.")
    return summary

# --- Apply to dataframe ---
grouped["summary"] = grouped["Ideas"].apply(adaptive_summary)


print("Step 6 done. Summarizing.")




######################

# Step 7: Sort by frequency and keep relevant columns
final_output = grouped[["theme", "frequency", "SumOfVotes", "SumOfComments", "summary"]].sort_values(by="frequency", ascending=False)
full_data = df.copy()  # add other columns if needed

# Write both sheets to the same Excel file

# with pd.ExcelWriter("thematic_summary_ideas_IP.xlsx", engine="openpyxl") as writer:
#     final_output.to_excel(writer, sheet_name="IP Thematic Summary", index=False)
#     full_data.to_excel(writer, sheet_name="IP Data", index=False)

with pd.ExcelWriter("thematic_summary_ideas_IC.xlsx", engine="openpyxl") as writer:
    final_output.to_excel(writer, sheet_name="IC Thematic Summary", index=False)
    full_data.to_excel(writer, sheet_name="IC Data", index=False)

# with pd.ExcelWriter("thematic_summary_ideas_IF.xlsx", engine="openpyxl") as writer:
#     final_output.to_excel(writer, sheet_name="IF Thematic Summary", index=False)
#     full_data.to_excel(writer, sheet_name="IF Data", index=False)

# with pd.ExcelWriter("thematic_summary_ideas_NA.xlsx", engine="openpyxl") as writer:
#     final_output.to_excel(writer, sheet_name="NA Thematic Summary", index=False)
#     full_data.to_excel(writer, sheet_name="NA Data", index=False)

#######################

print("✅ Thematic summary saved.")
