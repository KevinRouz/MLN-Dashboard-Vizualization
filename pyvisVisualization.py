from pyvis.network import Network  # Imports the Network class from the pyvis module for network visualization.
import os  # Imports the os module, which provides functions for interacting with the operating system.
import networkx as nx  # Imports the networkx library, allowing for the creation, manipulation, and study of complex networks.

"""
    WARNING: if this file creates an error when deployed on bangkok
    refer to the following line:
    >>> result_net.show(os.path.join(endPath, "visualization",f"pyvis_{clusterName}_Network.html"), notebook=False)
    
    and set the notebook parameter to True or remove it.
    
    ERROR details:
    https://stackoverflow.com/questions/75565224/in-pyvis-i-always-get-this-error-attributeerror-nonetype-object-has-no-attr
"""

def visualization(allEdges, mapper, mln_User, endPath, noEdges_fromFile, noVerticesLayer1, mappingFile_present, final_output_cluster_name):
    try:
        G = nx.Graph()  # Initializes a new graph instance using networkx.
        # Adds edges to the graph from a list of tuples where each tuple contains node1, node2, and the weight of the edge.
        G.add_edges_from(((node1, node2, {'weight': weight}) for node1, node2, weight in allEdges)) 
        
        # static layout to imporve performance
        layout = nx.spring_layout(G)
        
        # creating the network graph layout
        result_net = Network(
            font_color="yellow",
            width="100%",
            height="100vh",    # vh is view port height
            bgcolor="#222222",
            # heading=f"Network Graph for {final_output_cluster_name}", # ALERT: this prints the heading twice BUG 
            # I have fixed the above issue on official pyvis module, just waiting for owners to review and merge the changes. ~VS

            # neighborhood_highlight=True,  # ALERT: turning this on will not disappear the loading bar at all. BUG
            # filter_menu=True,
        )
        #setting physics layout of the network
        result_net.force_atlas_2based(spring_length=100)
        
        # Add nodes with labels from the mapper dictionary
        for node in G.nodes():
            node_id = str(node) # Converts the node identifier to a string.
            # Retrieves the label for the node from the mapper dictionary or defaults to "Node {node_id}".
            node_label = mapper.get(node_id, f"Node {node_id}")
            result_net.add_node(
                node_id,
                label=node_label,  # Sets the label of the node in the visualization.
                title=node_label,  # Sets the hover-over title of the node in the visualization.
                border_width=5,  # Sets the border width of nodes.
                borderWidthSelected=10,  # Sets the border width of nodes when selected.
                color={'background': 'white', 'border': 'magenta'}, # Sets the background and border colors of nodes.
                # x=layout[node][0]*1e3, 
                # y=layout[node][1]*1e3,
            )
        
        # Adds edges to the network visualization with specific styles.
        for node1,node2,weigth in allEdges:
            result_net.add_edge(node1, node2, value = weigth, color = {'color': 'cyan', 'highlight': 'pink', 'hover': 'yellow'})
            
        # Update node titles with neighbor information
        neighbor_map = result_net.get_adj_list()
        for node in result_net.nodes:
            node_id = node["id"]
            # Sets the title of each node to list its neighbors.
            node["title"] = "Adjacent Nodes:\n" + "\n".join([mapper.get(neighbor, f"Node {neighbor}") for neighbor in neighbor_map[node_id]])
            # Sets the value (size) of the node in the network based on the number of connections.
            node["value"] = len(neighbor_map[node_id])


        result_net.toggle_hide_edges_on_drag(False)  # Keeps edges visible when dragging nodes.
        result_net.set_edge_smooth("dynamic")  # Sets the edges to be dynamically smooth.
        # result_net.toggle_physics(False)
        result_net.show_buttons(filter_=['physics'])  # Displays buttons to control physics settings in the network.
        # Saves and shows the network visualization as an HTML file.
        # result_net.show(os.path.join(endPath, "visualization",f"pyvis_{clusterName}_Network.html"), notebook=False)
        result_net.show(os.path.join(endPath, "visualization",f"pyvis_{final_output_cluster_name}_Network.html"))
	# Returns the path to the created visualization.
        return os.path.join(mln_User, "visualization", f"pyvis_{final_output_cluster_name}_Network.html")
    except Exception as e:
            print(f"ERROR occured for pyvis (interactive) visualization: {e}")

