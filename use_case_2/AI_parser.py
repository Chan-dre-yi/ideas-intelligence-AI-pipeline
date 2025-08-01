'''
This script uses the basic ideas data,
And parses an internal AI API endpoint
To find similar ideas, and saves into ideas_with_similarities.xlsx.
'''





import pandas as pd
import requests
import re
import time
import os
import pickle

# === 1. Load CSV ===

#################
df = pd.read_csv("")
#################

df['ID'] = df['ID'].astype(str)
id_to_idea = dict(zip(df['ID'], df['Idea Name']))
df["Similar Idea IDs"] = ""  # New column for results

# === 2. Auth Headers & Cookies ===

##################
url = ""
##################

processed_log = "processed_ids.txt"
results_pickle = "results_checkpoint.pkl"

# === 3. Load processed log ===
processed_ids = set()
if os.path.exists(processed_log):
    with open(processed_log, 'r') as f:
        processed_ids = set(line.strip() for line in f)

# === 4. Load checkpointed results ===
if os.path.exists(results_pickle):
    with open(results_pickle, 'rb') as f:
        saved_results = pickle.load(f)
        for idea_id, similar_ids in saved_results.items():
            df.loc[df['ID'] == idea_id, "Similar Idea IDs"] = ", ".join(similar_ids)
else:
    saved_results = {}

# === 5. Main Loop ===
save_every = 10
processed_this_run = 0

# for idx, row in df.iterrows():
#     idea_id = str(row['ID'])
#     if idea_id in processed_ids:
#         continue

#     name = row['Idea Name']
#     desc = row['Description']

#     query = f"find ideas similar to {name}. with description of {desc}"
#     params = {"q": query, "messages": "false"}

#     try:
#         response = requests.get(url, headers=headers, cookies=cookies, params=params, verify=False)
#         response.raise_for_status()
#         content = response.json().get("content", "")

#         # Extract valid similar idea IDs
#         # suggested_ids = re.findall(r"Idea (\d{3,5})", content)
#         suggested_ids = re.findall(r'idea[^\d]*(\d{3,5})', content, flags=re.IGNORECASE)
#         valid_similar_ids = [sid for sid in suggested_ids if sid in id_to_idea]

#         # Store in DataFrame and checkpoint
#         df.at[idx, "Similar Idea IDs"] = ", ".join(valid_similar_ids)
#         saved_results[idea_id] = valid_similar_ids

#         # Update processed log
#         with open(processed_log, 'a') as f:
#             f.write(f"{idea_id}\n")
#         processed_this_run += 1

#         print(f"✅ Processed {idea_id}: {len(valid_similar_ids)} similar ideas")

#         # Save checkpoint every N
#         if processed_this_run % save_every == 0:
#             with open(results_pickle, 'wb') as f:
#                 pickle.dump(saved_results, f)
#             print("💾 Saved checkpoint.")

#     except Exception as e:
#         print(f"❌ Failed at ID {idea_id}: {e}")
#         break

#     time.sleep(1.5)

max_retries = 3
retry_delay = 5  # seconds

for idx, row in df.iterrows():
    idea_id = str(row['ID'])
    if idea_id in processed_ids:
        continue

    name = row['Idea Name']
    desc = row['Description']

    query = f"find ideas similar to {name}. with description of {desc}"
    params = {"q": query, "messages": "false"}

    content = ""
    success = False  # track if request succeeds

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, cookies=cookies, params=params, verify=False)
            response.raise_for_status()
            content = response.json().get("content", "")
            success = True
            break  # exit retry loop
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Attempt {attempt+1} failed for ID {idea_id}: {e}")
            if attempt < max_retries - 1:
                print(f"🔁 Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"❌ Failed after {max_retries} attempts at ID {idea_id}. Stopping script.")
                break  # exit retry loop

    if not success:
        break  # ❗Stop outer loop if all retries failed

    # Extract valid similar idea IDs
    suggested_ids = re.findall(r'idea[^\d]*(\d{3,5})', content, flags=re.IGNORECASE)
    valid_similar_ids = [sid for sid in suggested_ids if sid in id_to_idea]

    # Store in DataFrame and checkpoint
    df.at[idx, "Similar Idea IDs"] = ", ".join(valid_similar_ids)
    saved_results[idea_id] = valid_similar_ids

    # Update processed log
    with open(processed_log, 'a') as f:
        f.write(f"{idea_id}\n")
    processed_this_run += 1

    print(f"✅ Processed {idea_id}: {len(valid_similar_ids)} similar ideas")

    # Save checkpoint every N
    if processed_this_run % save_every == 0:
        with open(results_pickle, 'wb') as f:
            pickle.dump(saved_results, f)
        print("💾 Saved checkpoint.")

    time.sleep(1.5)

# === 6. Final Save ===
df.to_excel("ideas_with_similarities.xlsx", index=False)
print("✅ Done. File saved as 'ideas_with_similarities.xlsx'")
