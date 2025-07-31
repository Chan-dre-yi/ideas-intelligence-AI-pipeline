# ideas-intelligence-pipeline

Pipeline:

DATA COLLECTION
1. Scrape ideas from a website through auto-pilot web-scraping (100s of pages) (initial approach)
2. OR use the backend database to collect ideas and its details (eventually)

USE CASE 1: 
THEME BASED CLUSTERING of ideas using K means clustering, 
and SUMMARIZING each theme using Ollama & T5-small adaptively
1. Filter based on idea groups assigned by user
2. Embed sentence transformer
3. Determine optimal no. of lusters using K means clustering
4. Generate theme names for each cluster using a prompt on Ollama and by giving the top keywords from each cluster
5. Group by theme, and get sum counts of vodes, frequencies and comments
6. Save results

USE CASE 2: 
VISUALIZING realtion of ideas, to facilitate linking them using an internal AI API
1. Looping through an AI API call and creating the linkage dataset: ideas_with_similarities.xlsx
2. Using networkx and plotly, visualizing the relations


Final Results:

Theme Clusters for one group
<img width="1919" height="1129" alt="image" src="https://github.com/user-attachments/assets/32f5464d-a1cb-4532-9318-28fb4e836efe" />

Summary of one theme
<img width="1919" height="1124" alt="image" src="https://github.com/user-attachments/assets/52772994-17ed-48fe-bbe1-723e504bc909" />

Hover (blue)
<img width="1919" height="1055" alt="image" src="https://github.com/user-attachments/assets/f7ad17fa-9d85-456e-964f-ae41ff67d6da" />

Click (red)
<img width="1923" height="1055" alt="image" src="https://github.com/user-attachments/assets/4beb886e-5076-4b15-b83b-05d143e5a7d3" />

Hover on related idea (yellow)
<img width="1919" height="1136" alt="image" src="https://github.com/user-attachments/assets/c1a1c77b-b224-4b73-bd85-62eff3d54251" />
