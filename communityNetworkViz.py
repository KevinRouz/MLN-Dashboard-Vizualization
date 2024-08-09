import os
import networkx as nx
from bokeh.io import show
from bokeh.plotting import figure, from_networkx, save
from bokeh.palettes import Viridis256, Spectral8, Oranges256, Purples256, Blues256, Greens256
from bokeh.models import MultiLine, Circle, ColumnDataSource, LinearColorMapper, ColorBar, Legend, LegendItem, TapTool, OpenURL
from networkx.algorithms import community as comm
import itertools
# CUSTOM IMPORTS
from vizUTILS import create_url

def visualization(data, mapper, mln_User, endPath, dataset_type, G, input_file, final_output_cluster_name):
    try:
        # calculate degree of each node
        degrees = dict(nx.degree(G))
        nx.set_node_attributes(G, name='degree', values=degrees)

        # Set node size based on degree ----------------------------------------------------
        adjusted_node_size = dict([(node, degree + 5) for node, degree in nx.degree(G)])
        nx.set_node_attributes(G, name='adjusted_node_size', values=adjusted_node_size)

        # Detect communities using greedy modularity maximization.
        communities = comm.greedy_modularity_communities(G)
        
        # MODULARITY CLASS ------------------------------------------------------------------
        # Assign each node to a modularity class based on the detected communities.
        modularity_class = {node: i for i, community in enumerate(communities) for node in community}
        nx.set_node_attributes(G, name='modularity_class', values=modularity_class)
        
        # MODULARITY COLOR ------------------------------------------------------------------
        # Assign colors to each community by cycling through an extended color palette.
        extended_palette = Spectral8 + Oranges256 + Viridis256 + Purples256 + Blues256 + Greens256
        color_iterator = itertools.cycle(extended_palette)
        community_colors = {i: next(color_iterator) for i in range(len(communities))}
        modularity_color = {node: community_colors[modularity_class[node]] for node in G.nodes()}
        nx.set_node_attributes(G, name='modularity_color', values=modularity_color)
        
        # Prepare color mapper
        color_mapper = LinearColorMapper(palette=list(community_colors.values()), low=0, high=len(communities) - 1)

        # add labels to nodes ---------------------------------------------------------------
        labels = {node: mapper.get(str(node), f"Node {node}") for node in G.nodes()}
        nx.set_node_attributes(G, labels, "label")
        urls = {node: create_url(labels[node], dataset_type) for node in G.nodes()}
        nx.set_node_attributes(G, urls, "url")

        # Set up the data source for Bokeh visual elements with node attributes.
        node_data = {
            'index': list(G.nodes()),
            'degree': list(nx.get_node_attributes(G, 'degree').values()),
            'adjusted_node_size': [adjusted_node_size[node] for node in G.nodes()],
            'label': list(nx.get_node_attributes(G, 'label').values()),
            'modularity_class': list(nx.get_node_attributes(G, 'modularity_class').values()),
            'modularity_color': list(nx.get_node_attributes(G, 'modularity_color').values()),
            'url': [urls[node] for node in G.nodes()],  # URLs added here to each node
        }
        source = ColumnDataSource(node_data)
        
        from bokeh.models import EdgesAndLinkedNodes, NodesAndLinkedEdges
        #Choose colors for node and edge highlighting
        node_highlight_color = 'white'
        edge_highlight_color = 'black'

        size_by_this_attribute = 'adjusted_node_size'
        color_by_this_attribute = 'modularity_color'

        # bokeh --------------------------------------------------------------------------------------------------------------------------------
        # Create a Bokeh figure with interactive tools and hover tooltips.
        title = f"{data['Layer']} Community Network Visualization"
        HOVER_TOOLTIPS = [
            ("Node ID ", "@index"), 
            ("Label ", "@label"), 
            ('Degree ', '@degree'),
            ('Community ', '@modularity_class')    
        ]
        fig = figure(
                tooltips = HOVER_TOOLTIPS,
                tools="pan,wheel_zoom,box_zoom,reset,save",
                active_scroll='wheel_zoom',
                x_range=(-10,10), y_range=(-10,10),
                title=title,
                sizing_mode="stretch_both" # autoresize
        )
        fig.title.text_font_size = '16pt'
        
        # Set up TapTool with OpenURL callback using the URL from the node's data source
        tap_tool = TapTool(callback=OpenURL(url="@url"))
        fig.add_tools(tap_tool)
        
        network_graph = from_networkx(G, nx.spring_layout, scale=10, center=(0, 0))
        network_graph.node_renderer.data_source = source  # Use updated source with URL
        
        #Set node sizes and colors according to node degree (color as category from attribute)
        network_graph.node_renderer.glyph = Circle(size=size_by_this_attribute, fill_color=color_by_this_attribute)
        #Set node highlight colors
        network_graph.node_renderer.hover_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width=2)
        network_graph.node_renderer.selection_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width=2)

        #Set edge opacity and width
        network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=1)
        #Set edge highlight colors
        network_graph.edge_renderer.selection_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)
        network_graph.edge_renderer.hover_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)
        
        #Highlight nodes and edges
        network_graph.selection_policy = NodesAndLinkedEdges()
        network_graph.inspection_policy = NodesAndLinkedEdges()

        # Legend --------------------------------------------------------------------------------------------------------------------------------
        legend = Legend(items=[
            LegendItem(label=f"Total Number of Communities : {data['NumCommunities']}", renderers=[network_graph.node_renderer]),
        ], location="top_left")
        fig.add_layout(legend)

        # add color bar --------------------------------------------------------------------------------------------------------------------------
        color_bar = ColorBar(color_mapper=color_mapper, label_standoff=12, border_line_color=None, location=(0, 0), title="Community")
        fig.add_layout(color_bar, 'right')

        fig.renderers.append(network_graph)

        # save bokeh plot
        save_path = os.path.join(endPath,"visualization",f"bokeh_{final_output_cluster_name}_comNet.html")
        save(fig, save_path, title=f"{data['Layer']} Community Network", resources='inline')
        return_path = os.path.join(mln_User,"visualization",f"bokeh_{final_output_cluster_name}_comNet.html")
        
        
        #Old naming
        # save_path = os.path.join(endPath,"visualization",f"bokeh_{data['Layer']}_comNet.html")
        # save(fig, save_path, title=f"{final_output_cluster_name} Community Network", resources='inline')
        # return_path = os.path.join(mln_User,"visualization",f"bokeh_{data['Layer']}_comNet.html")
        return return_path
    except Exception as e:
        return False