'''
This script enables interactive visualisation of related ideas,
From the file ideas_with_similarities.xlsx.
'''




import pandas as pd
import networkx as nx
import plotly.graph_objs as go
from dash import Dash, dcc, html, Input, Output




##################
# Ctrl + F => https://ideas.xyz.com/idea/{idea_id}
# and change it like you need
##################





# === 1. Load Data ===
df = pd.read_excel("ideas_with_similarities.xlsx")
df['ID'] = df['ID'].astype(str)

# Build lookup
idea_info = df.set_index('ID')[['Idea Name', 'Description', 'Votes', 'Idea Comments']].to_dict(orient='index')

# === 2. Build Graph ===
G = nx.Graph()
for idea_id in df['ID']:
    G.add_node(idea_id)

for _, row in df.iterrows():
    source = row['ID']
    if pd.isna(row['Similar Idea IDs']) or row['Similar Idea IDs'].strip() == "":
        continue
    similar_ids = [x.strip() for x in row['Similar Idea IDs'].split(",")]
    for target in similar_ids:
        if target in G.nodes and source != target:
            G.add_edge(source, target)

# === 3. Layout ===
pos = nx.spring_layout(G, seed=42, k=0.5)

def wrap_text(text, width=80):
    if not isinstance(text, str):
        text = ""
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 <= width:
            current_line += (" " if current_line else "") + word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return "<br>".join(lines)

def generate_figure(highlight_node=None):
    connected_nodes = set()
    highlight_edges_x, highlight_edges_y = [], []
    normal_edges_x, normal_edges_y = [], []

    if highlight_node:
        connected_nodes = set(G.neighbors(highlight_node))

    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        coords = [x0, x1, None], [y0, y1, None]
        if highlight_node and (u == highlight_node or v == highlight_node):
            highlight_edges_x.extend(coords[0])
            highlight_edges_y.extend(coords[1])
        else:
            normal_edges_x.extend(coords[0])
            normal_edges_y.extend(coords[1])

    normal_edge_trace = go.Scatter(
        x=normal_edges_x,
        y=normal_edges_y,
        mode='lines',
        line=dict(width=1, color='#888'),
        hoverinfo='none'
    )

    highlight_edge_trace = go.Scatter(
        x=highlight_edges_x,
        y=highlight_edges_y,
        mode='lines',
        line=dict(width=2, color='red'),
        hoverinfo='none'
    )

    node_x, node_y, hover_texts, colors, customdata = [], [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        info = idea_info.get(node, {})
        idea = wrap_text(info.get("Idea Name", ""), 80)
        desc = wrap_text(info.get("Description", ""), 80)
        similar = df.loc[df["ID"] == node, "Similar Idea IDs"].values
        similar_str = similar[0] if len(similar) > 0 and isinstance(similar[0], str) else "None"

        hover_texts.append(
            f"<b>ID:</b> {node}<br><b>Idea:</b> {idea}<br><b>Description:</b> {desc}<br><b>Similar Idea IDs:</b> {similar_str}"
        )
        customdata.append(node)

        if node == highlight_node:
            colors.append("red")
        elif node in connected_nodes:
            colors.append("yellow")
        else:
            colors.append("LightSkyBlue")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        hovertext=hover_texts,
        customdata=customdata,
        marker=dict(
            size=20,
            color=colors,
            line=dict(width=2, color='DarkSlateGrey')
        )
    )

    fig = go.Figure(
        data=[normal_edge_trace, highlight_edge_trace, node_trace],
        layout=go.Layout(
            title="Idea Similarity Network",
            title_x=0.5,
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            dragmode='pan'
        )
    )
    return fig


# === Dash App ===
app = Dash(__name__)

app.layout = html.Div([
    html.Div(id='selected-idea-card', style={
        'position': 'absolute', 'top': '10px', 'left': '10px', 'zIndex': 10,
        'backgroundColor': '#f9f9f9', 'padding': '10px', 'border': '1px solid #ccc',
        'borderRadius': '5px', 'boxShadow': '2px 2px 8px rgba(0,0,0,0.1)', 'maxWidth': '320px'
    }),
    dcc.Graph(id='network-graph', figure=generate_figure(), style={'height': '90vh'}),
])

@app.callback(
    Output('network-graph', 'figure'),
    Output('selected-idea-card', 'children'),
    Input('network-graph', 'clickData')
)
def update_on_click(clickData):
    if clickData and clickData['points']:
        idea_id = clickData['points'][0]['customdata']
        info = idea_info.get(idea_id, {})
        card = html.Div([
            html.H4(f"Idea ID: {idea_id}"),
            html.P(info.get("Idea Name", ""), style={'whiteSpace': 'pre-wrap', 'maxWidth': '300px'}),
            html.P(f"Votes: {info.get('Votes', 'N/A')}"),
            html.P(f"Idea Comments: {info.get('Idea Comments', 'N/A')}"),
            html.A("🔗 View Full Idea", href=f"https://ideas.xyz.com/idea/{idea_id}", target="_blank",
                   style={'display': 'inline-block', 'marginTop': '5px', 'textDecoration': 'none',
                          'backgroundColor': '#007bff', 'color': 'white', 'padding': '5px 10px',
                          'borderRadius': '5px'})
        ])
        return generate_figure(highlight_node=idea_id), card
    return generate_figure(), None

if __name__ == '__main__':
    app.run(debug=True)
