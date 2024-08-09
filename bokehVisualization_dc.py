import networkx as nx
import os
from bokeh.io import save
from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine, NodesAndLinkedEdges, TapTool, OpenURL
from bokeh.plotting import figure
from bokeh.plotting import from_networkx
from bokeh.palettes import Blues3
# CUSTOM IMPORTS
from vizUTILS import create_url

def visualization(allEdges, mapper, mln_User, endPath, noEdges_fromFile, noVerticesLayer1, dataset_type, final_output_cluster_name):
    try:      
        # Assign a scale according to the number of nodes
        # This is to adjust the layout of the graph based on the number of nodes
        custom_scale = 10 if int(noEdges_fromFile) <= 1100 else 12 if int(noEdges_fromFile) <= 3000 else 14 if int(noEdges_fromFile) <= 6000 else 16
        
        # Creating a networkX graph object
        G = nx.Graph()

        # Adding nodes and edges to the graph
        nodes = range(int(noVerticesLayer1))
        G.add_nodes_from(nodes)

        if allEdges:
            G.add_edges_from(((int(edge[0]), int(edge[1])) for edge in allEdges))
        
        # Adding node labels from the primary_input mapping file
        labels = {node: mapper.get(str(node), str(node)) for node in G.nodes()}
        nx.set_node_attributes(G, labels, 'label')
        
        # Calculating node degrees and adding as attribute for hover and sizing
        degrees = dict(nx.degree(G))
        nx.set_node_attributes(G, degrees, 'degree')
        
        # Adjusting node size based on degree
        adjusted_node_size = {node: degree + 5 for node, degree in degrees.items()}
        nx.set_node_attributes(G, adjusted_node_size, 'adjusted_node_size')
        
        # Choosing colors for node and edge highlighting
        node_highlight_color = 'white'
        edge_highlight_color = 'black'  

        # Precompute layout if the graph is large or layout computation is expensive
        layout = nx.spring_layout(G, scale=custom_scale, center=(0,0))
        
        # Defining hover tooltips
        HOVER_TOOLTIPS = [
            ("Node ID", "@index"),
            ("Label", "@label"),
            ("Degree", "@degree"),
        ]

        # Creating the main figure
        plot = figure(
            title=f"{final_output_cluster_name} network graph based on Degree Centrality", 
            x_range = Range1d(-10, 10), y_range = Range1d(-10, 10),
            sizing_mode="stretch_both", # autoresize figure
            tools = "pan,wheel_zoom,box_zoom,reset,save",
            tooltips = HOVER_TOOLTIPS,
            active_scroll = "wheel_zoom",
        )
        plot.title.text_font_size = '16pt'
        
        # Rendering the network graph
        network_graph = from_networkx(G, layout)
        network_graph.node_renderer.glyph = Circle(size='adjusted_node_size', fill_color=Blues3[0])  # Constant color for all nodes
        # Setting node highlight colors
        network_graph.node_renderer.hover_glyph = Circle(size='adjusted_node_size', fill_color=node_highlight_color, line_width=2)
        network_graph.node_renderer.selection_glyph = Circle(size='adjusted_node_size', fill_color=node_highlight_color, line_width=2)
        
        # Create a ColumnDataSource from the node attributes in the graph
        node_data = {
            'index': list(G.nodes()),
            'label': [labels[node] for node in G.nodes() if node in labels],
            'adjusted_node_size': [adjusted_node_size[node] for node in G.nodes()],
            'url': [create_url(labels[node], dataset_type) for node in G.nodes()],
            'degree': [degrees[node] for node in G.nodes()],
        }
        source = ColumnDataSource(node_data)
        network_graph.node_renderer.data_source.data.update(source.data)
        
        tap_tool = TapTool(callback=OpenURL(url="@url"))
        plot.add_tools(tap_tool)
                    
        network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=1)
        # Set edge highlight colors
        network_graph.edge_renderer.selection_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)
        network_graph.edge_renderer.hover_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)
        network_graph.selection_policy = NodesAndLinkedEdges()
        network_graph.inspection_policy = NodesAndLinkedEdges()
        plot.renderers.append(network_graph)
        
        # SAVE FIGURE ------------------------------------------------------------------------
        save_path = os.path.join(endPath, "visualization",f"bokeh_DC_{final_output_cluster_name}_Network.html")
        save(plot, save_path, title=f"{final_output_cluster_name} Network Graph using Degree Centrality", resources='inline')
        return os.path.join(mln_User, "visualization",f"bokeh_DC_{final_output_cluster_name}_Network.html")
    except Exception as e:
        print(f"ERROR occured for bokeh visualization: {e}")