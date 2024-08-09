from itertools import cycle
import networkx as nx
import os
from bokeh.io import save
from bokeh.models import Range1d, Circle, MultiLine, NodesAndLinkedEdges, TapTool, OpenURL, ColumnDataSource
from bokeh.plotting import figure
from bokeh.plotting import from_networkx
from bokeh.palettes import Viridis256, Spectral8, Purples256, Blues256, Greens256, Oranges256
from networkx.algorithms import community as comm
from urllib.parse import quote_plus
# CUSTOM IMPORT
from vizUTILS import create_url

def visualization(allEdges, mapper, mln_User, endPath, noEdges_fromFile, noVerticesLayer1, dataset_type, final_output_cluster_name):
    try:
        # assign a scale according to the number of nodes
        # This is to adjust the layout of the graph based on the number of nodes
        custom_scale = 10 if int(noEdges_fromFile) <= 1100 else 12 if int(noEdges_fromFile) <= 3000 else 14 if int(noEdges_fromFile) <= 6000 else 16
    
        # Creating networkX graph
        G = nx.Graph()

        # adding nodes and edges to graph
        nodes = range(int(noVerticesLayer1))
        G.add_nodes_from(nodes)
        if allEdges:
            G.add_edges_from(((int(edge[0]), int(edge[1])) for edge in allEdges))
        
        # Adding node labels from the primary_input mapping file
        labels = {node: mapper.get(str(node), str(node)) for node in G.nodes()}
        nx.set_node_attributes(G, labels, 'label')
        
        # creating urls from the respective labels
        urls = {node: create_url(labels[node], dataset_type) for node in G.nodes()}
        nx.set_node_attributes(G, urls, 'url')
        
        # calculating communities using the greedy modularity algorithm
        communities = comm.greedy_modularity_communities(G)
        
        # color pallete for the nodes
        extended_palette = cycle(Spectral8 + Oranges256 + Viridis256 + Purples256 + Blues256 + Greens256)
        communities_colors = {i: next(extended_palette) for i in range(len(communities))}
        
        # add modularity class and colors from the palette
        modularity_class = {node: ci for ci, community in enumerate(communities) for node in community}
        modularity_color = {}
        for community_index, community in enumerate(communities):
            for node in community:
                modularity_color[node] = communities_colors[community_index]
        
        nx.set_node_attributes(G, name='modularity_class', values=modularity_class)
        nx.set_node_attributes(G, name='modularity_color', values=modularity_color)
        
        # Calculate node degrees and add as attribute (for hover and sizing)
        degrees = dict(G.degree())
        nx.set_node_attributes(G, degrees, 'degree')
        
        #Choose colors for node and edge highlighting
        node_highlight_color = 'white'
        edge_highlight_color = 'black' 
        
        # Precompute layout if the graph is large or layout computation is expensive
        layout = nx.spring_layout(G, scale=custom_scale, center=(0,0))
        
        # Hovering over the nodes
        HOVER_TOOLTIPS = [
            ("Node ID", "@index"),
            ("Label", "@label"),
            ("Degree", "@degree"),
            ("Community", "@modularity_class"),
        ]

        # MAIN FIGURE
        plot = figure(
            title=f"{final_output_cluster_name} Network Graph", 
            x_range = Range1d(-10, 10), y_range = Range1d(-10, 10),
            sizing_mode="stretch_both", # autoresize figure
            tools = "pan,wheel_zoom,box_zoom,reset,save",
            tooltips = HOVER_TOOLTIPS,
            active_scroll = "wheel_zoom",
        )
        plot.title.text_font_size = '16pt'
           
        # Creating the network graph from the NetworkX graph
        network_graph = from_networkx(G, layout)
        
        # Prepare data for the ColumnDataSource
        node_data = {
            'index': list(G.nodes()),
            'label': [labels[node] for node in G.nodes()],
            'degree': [G.degree(node) for node in G.nodes()],
            'url': [urls[node] for node in G.nodes()],
            'modularity_class': [G.nodes[node]['modularity_class'] for node in G.nodes()],
            'modularity_color': [G.nodes[node]['modularity_color'] for node in G.nodes()],
        }
        source = ColumnDataSource(node_data)

        # NetworkX graph to Bokeh graph conversion and customization
        network_graph = from_networkx(G, layout)
        # Linking the data source to the network graph
        network_graph.node_renderer.data_source = source
        
        # Adding TapTool with OpenURL callback
        tap_tool = TapTool(callback=OpenURL(url="@url"))
        plot.add_tools(tap_tool)

        # Customize node renderer
        network_graph.node_renderer.glyph = Circle(size=13, fill_color='modularity_color')
        # Set node highlight colors
        network_graph.node_renderer.hover_glyph = Circle(size='adjusted_node_size', fill_color=node_highlight_color, line_width=2)
        network_graph.node_renderer.selection_glyph = Circle(size='adjusted_node_size', fill_color=node_highlight_color, line_width=2)
        
        # Customize edge renderer
        network_graph.edge_renderer.glyph = MultiLine(line_color='#333333', line_alpha=0.8, line_width=1)
        # Set edge highlight colors
        network_graph.edge_renderer.selection_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)
        network_graph.edge_renderer.hover_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)
        
        network_graph.selection_policy = NodesAndLinkedEdges()
        network_graph.inspection_policy = NodesAndLinkedEdges()
  
        plot.renderers.append(network_graph)
        
        # SAVE FIGURE ------------------------------------------------------------------------
        save_path = os.path.join(endPath, "visualization",f"bokeh_{final_output_cluster_name}_Network.html")
        save(plot, save_path, title=f"{final_output_cluster_name} Network Graph using Louvain Community Detection", resources='inline')
        return os.path.join(mln_User, "visualization",f"bokeh_{final_output_cluster_name}_Network.html")
    except Exception as e:
        print(f"ERROR occured for bokeh visualization: {e}")
