import networkx as nx
import os
import plotly.graph_objects as go

def visualization(allEdges, mapper, mln_User, endPath, noEdges_fromFile, noVerticesLayer1, mappingFile_present, final_output_cluster_name):
    try:
        # CREATE GRAPH -----------------------------------------------------------------------
        G = nx.Graph()
        # Add edges 
        if int(noEdges_fromFile) > 0:   # Check if there are any edges to add to the graph
            # Add all edges to the graph with weights, each edge is a tuple (node1, node2, weight)
            G.add_edges_from((edge[0], edge[1], {'weight': edge[2]}) for edge in allEdges)
        else:
            # If no edges, add all nodes as isolated nodes, numbered sequentially
            G.add_nodes_from(range(int(noVerticesLayer1)))
        
        # Calculate the degree centrality for each node in the graph
        dc = nx.degree_centrality(G)
        # define position for nodes in the graph ---------------------------------------------
        # Position nodes using Kamada-Kawai layout for aesthetic spacing
        pos = nx.kamada_kawai_layout(G)
        # Convert positions to a format suitable for Plotly (dictionary with nodes as keys)
        pos = {node: (x, y) for node, (x, y) in pos.items()}
        edge_pos = {(u, v): pos[u] for u, v in G.edges()}
        nx.set_edge_attributes(G, edge_pos, 'pos')
        # CREATE BLANK PLOTLY FIGURE ---------------------------------------------------------
        fig = go.Figure()
        # CREATE EDGES EDGE_TRACE ------------------------------------------------------------
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            # Ensure every edge has a weight attribute; default to 1.0 if missing
            if 'weight' not in edge[2]:
                edge[2]['weight'] = 1.0
            # Create a Plotly scatter trace for each edge
            edge_trace = go.Scatter(
                x=[x0, x1, None], y=[y0, y1, None],
                mode='lines',
                line=dict(width=edge[2]['weight'],color='#202213'),# Line styling
                hoverinfo='none',  # No additional info on hover
                showlegend=False  # Hide legend for edges
            )
            fig.add_trace(edge_trace)   # Add the trace to the figure

        # CREATE NODES NODE_TRACE ------------------------------------------------------------
        node_x = []
        node_y = []
        node_text = []
        for node in G.nodes():
            if noEdges_fromFile == 0:
                # should visualoze only the nodes here
                pass
            else:
                # Populate node attributes for plotting
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            marker=dict(
                showscale=True,
                colorscale='rainbow',
                reversescale=True,
                color=[],
                size = 15,
                colorbar=dict(
                    thickness=15,
                    title='Node Connections/ Degree Centrality',
                    xanchor='left',
                    titleside='right'
                ),
                line_width=2
            ),
            text=node_text, # Labels appearing on hover
            showlegend=True,
            hovertext=node_text,
            hoverinfo='text' 
                            )
        # COLOR NODE POINTS TEXT -------------------------------------------------------------
        # Add node colors and labels based on degree centrality and mapping information
        node_adjacencies = []
        for node, adjacencies in enumerate(G.adjacency()):
            node_adjacencies.append(len(adjacencies[1]))    # Number of connected edges
            if mappingFile_present:
                # Convert node to string since mapper keys are strings
                node_info = mapper.get(str(node), f'Unknown({node})')  # # Get label from mapper, Defaults to 'Unknown' if node not in mapper
                node_text.append('Node ID: ' + node_info + '<br />Degree Centrality: '+ str(len(adjacencies[1])))
            else:
                node_text.append('Node ID: ' + str(node) + '<br />Degree Centrality: '+ str(len(adjacencies[1])))
        node_trace.marker.color = node_adjacencies
        node_trace.text = node_text
        fig.add_trace(node_trace)
        
        # CREATE LAYOUT ----------------------------------------------------------------------
        # Define the layout for the visualization
        layout = go.Layout(
                title={
                    'text': f'<br />Network graph for {final_output_cluster_name.upper()} layer',
                    'y':1,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': dict(size=20, color='#343541', family='Arial')
                },
                legend_title_text=f"Nodes: {len(G.nodes)} | Edges: {len(G.edges)}",
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
                hovermode='closest',
                margin=dict(b=0,l=0,r=0,t=0),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                autosize = True,
        )
        # UPATE FIGURE -----------------------------------------------------------------------
        fig.update_layout(layout)   # Apply the layout settings to the figure
        # SAVE FIGURE ------------------------------------------------------------------------
        #final_output_cluster_name = final_output_cluster_name.split('.')[0] # Remove file extension from cluster name for the output file
        resultant_file_name = f"plotly_{final_output_cluster_name}_Network.html"  
        save_path = os.path.join(endPath, "visualization",resultant_file_name)
        fig.write_html(save_path)  # Save the figure as HTML
        
        # Save_path for MLN ------------------------------------------------------------------
        # save_path = os.path.join(mln_User, resultant_file_name)
        return save_path    # Return the path where the visualization was saved
    except Exception as e:
        print(f"ERROR occured for plotly visualization: {str(e)}")
        return str(e)
