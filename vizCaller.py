import os  # Imports the 'os' module which provides a way of using operating system dependent functionality.
import re  # Imports the 're' module which provides support for regular expressions.
import csv  # Imports the 'csv' module which provides functionality to read and write data to and from CSV files.
from vizUTILS import determine_dataset_type  # Imports the 'determine_dataset_type' function from the 'vizUTILS' module.

# Declares a global variable 'dataset_type' and initializes it with the string "Unknown".
dataset_type = "Unknown"
input_file_extension = "Unknown"

def createViz(endPath_para, clusterName_para, vizGraphType, input_file_extension, input_file):
    """
    Determines whether a new visualization file needs to be created based on the 
    absence of an existing file at the specified path.

    This function constructs a filename for a visualization based on the visualization 
    type and input file extension. It checks if a file with that name already exists 
    in a designated visualization directory within the given end path. The function 
    supports creating filenames for wordcloud visualizations specifically if the 
    file type is '.ecom' or '.vcom', otherwise it defaults to a general naming scheme.

    Parameters:
        endPath_para (str): The base directory path where the visualization directory exists.
        clusterName_para (str): The name of the cluster which is used in the naming of the visualization file.
        vizGraphType (str): The type of visualization (e.g., 'wordcloud', 'network', etc.).
        input_file_extension (str): The file extension that helps in determining the specific 
                                    visualization file naming convention (e.g., '.ecom', '.vcom').

    Returns:
        bool: True if the visualization file does not exist and needs to be created, False otherwise.
    """
    
    # if vizGraphType.lower() == 'wordcloud' and input_file_extension in ['.ecom', '.vcom']:
    #     file_name = f"wordcloud_{clusterName_para}_{input_file_extension.strip('.')}.html"
    # else:
    #     file_name = f"{vizGraphType}_{clusterName_para}_{'comNet' if input_file_extension in ['.ecom', '.vcom'] else 'Network'}.html"
        
    if input_file_extension == '.ecom':
        suffix = 'ecom'
    elif input_file_extension == '.vcom':
        suffix = 'vcom'
    else:
        suffix = 'Network'
    
    file_name = f"{vizGraphType}_{clusterName_para}_{suffix}.html"
    
    viz_file_path = os.path.join(endPath_para, "visualization", file_name)
    
    print(f"Checking path: {viz_file_path}")
    if not os.path.exists(viz_file_path):
        print(f"viz file path does not exist: creating new visualization")
        return True  # File does not exist, so return True to create a new visualization
    
    # Check the timestamps of the input file and the visualization file
    input_file_mtime = os.path.getmtime(input_file)  # Modification time of the input file
    print(f"{input_file} modification date: {input_file_mtime}")
    
    viz_file_mtime = os.path.getmtime(viz_file_path)    # Modification time of the existing visualization file
    print(f"{viz_file_path} modification date: {viz_file_mtime}")
    
    #Check if input file is newer than the visualization file. If true, then return true to create a new visualization.
    return input_file_mtime > viz_file_mtime  # Return True if the input file is newer, otherwise False


def create_mapper(mapping_file_path, mapping_file_present):
    """
    Creates a mapping from node IDs to corresponding labels or geographical coordinates.

    This function reads from a CSV file specified by `mapping_file_path` to construct
    a dictionary mapping node IDs to either labels or tuples of geographical coordinates
    (longitude, latitude). The structure of the mapping depends on the number of columns
    in the CSV file. The function handles three scenarios:
    1. Two columns: Maps node IDs to labels.
    2. Three columns: Maps node IDs to a tuple of (longitude, latitude).
    3. More than three columns with comma-separated values in the second column: 
       Maps node IDs to a tuple of (longitude, latitude) parsed from the second column.

    Parameters:
        mapping_file_path (str): The file path to the CSV file containing the mapping data.
        mapping_file_present (bool): A boolean indicating whether the mapping file is 
                                    present and should be read. If `False`, the function 
                                    will return an empty dictionary.

    Returns:
        dict: A dictionary where the keys are node IDs (str) and the values are either 
              labels (str) or tuples of geographical coordinates (float, float), depending 
              on the CSV file structure.
    """
    mapper = {}
    # If a mapping file is present, read it and cretate the mapping.
    if mapping_file_present:
        with open(mapping_file_path, "r", newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip the header
            for row in reader:
                node_id = row[0].strip()  # Retrieves and strips whitespace from the node ID.
                # Handle different types of mapping files with varying numbers of columns.
                if len(row) == 2:  # Handles the case where the row has two columns (node ID and label).
                    mapper[node_id] = row[1].strip()
                elif len(row) == 3:  # Handles the case where the row has three columns (node ID, longitude, latitude).
                    lon, lat = row[1].strip(), row[2].strip()
                    mapper[node_id] = (float(lon), float(lat))
                elif len(row) > 3 and ',' in row[1]:  # Handles a complex case where the second column contains multiple values separated by commas.
                    _, lon, lat = row[1].split(',')
                    mapper[node_id] = (float(lon), float(lat))
    return mapper

# Each 'vizFunction' defined below imports a specific visualization module and calls a function within that module to generate a visualization.

def plotlyViz(allEdges, mapper, mln_User, endPath, noEdges_fromFile, noVerticesLayer1, mappingFile_present, final_output_cluster_name):
    import plotlyVisualization as pv
    return(pv.visualization(allEdges, mapper, mln_User, endPath, noEdges_fromFile, noVerticesLayer1, mappingFile_present, final_output_cluster_name))

def bokehViz(allEdges, mapper, mln_User, endPath, noEdges_fromFile, noVerticesLayer1, mappingFile_present, final_output_cluster_name):
    import bokehVisualization as bv
    return(bv.visualization(allEdges, mapper, mln_User, endPath, noEdges_fromFile, noVerticesLayer1, dataset_type, final_output_cluster_name))

def bokehDcViz(allEdges, mapper, mln_User, endPath, noEdges_fromFile, noVerticesLayer1, mappingFile_present, final_output_cluster_name):
    import bokehVisualization_dc as bv_dc
    return(bv_dc.visualization(allEdges, mapper, mln_User, endPath, noEdges_fromFile, noVerticesLayer1, dataset_type, final_output_cluster_name))
    
def pyvisViz(allEdges, mapper, mln_User, endPath, noEdges_fromFile, noVerticesLayer1, mappingFile_present, final_output_cluster_name):
    import pyvisVisualization as pyv
    return(pyv.visualization(allEdges, mapper, mln_User, endPath, noEdges_fromFile, noVerticesLayer1, mappingFile_present, final_output_cluster_name))
    
def mapViz(allEdges, mapper, mln_User, endPath, noEdges_fromFile, noVerticesLayer1, mappingFile_present, final_output_cluster_name):
    import mapVisualization as mpv
    return(mpv.visualization(allEdges, mapper, mln_User, endPath, noEdges_fromFile, noVerticesLayer1, mappingFile_present, final_output_cluster_name))

def wordCloudViz(data, mapper, mln_User, endPath, mappingFile_present, G, input_file, final_output_cluster_name):
    import wordCloudViz as wc
    return(wc.visualization(data, mapper, mln_User, endPath, mappingFile_present, G, input_file_extension, final_output_cluster_name))

def bubbleChartViz(data, mapper, mln_User, endPath, mappingFile_present, G, input_file, final_output_cluster_name):
    import bubbleChartViz as bcv
    return(bcv.visualization(data, mapper, mln_User, endPath, mappingFile_present, G, input_file, final_output_cluster_name))

def communityNetworkViz(data, mapper, mln_User, endPath, mappingFile_present, G, input_file, final_output_cluster_name):
    import communityNetworkViz as comNetG
    return(comNetG.visualization(data, mapper, mln_User, endPath, dataset_type, G, input_file, final_output_cluster_name))
    
def barChartViz(data, mapper, mln_User, endPath, mappingFile_present, G, input_file, final_output_cluster_name):
    import barChartViz as bcv
    return(bcv.visualization(data, mapper, mln_User, endPath, mappingFile_present, G, input_file, final_output_cluster_name))

# A dictionary that maps visualization types to their corresponding function handlers.
vizDictionary = {
    "plotly_visualization": plotlyViz,
    "bokeh_visualization": bokehViz,
    "bokeh_dc_visualization": bokehDcViz,
    "pyvis_visualization": pyvisViz,
    "map_visualization": mapViz,
    "word_cloud_visualization": wordCloudViz,
    "bubble_chart_visualization": bubbleChartViz,
    "community_network_visualization": communityNetworkViz,
    'bar_chart_visualization': barChartViz,
}

def readNCall(pathToInputFile, mappingInputFile , mln_User, vizType):
    """
    Processes the input file to determine the dataset type and decide whether a new visualization
    needs to be created or an existing one should be reused. It also handles mapping file operations
    and calls the appropriate visualization function based on the visualization type.

    The function attempts to identify the dataset type, extracts the username from the path, checks 
    for the presence of a mapping file, and determines the need for creating a new visualization. 
    It supports various file types and handles them accordingly, creating the necessary visualization 
    if it doesn't already exist.

    Parameters:
        pathToInputFile (str): The path to the input file containing the data.
        mappingInputFile (str): The path where the mapping files are stored.
        mln_User (str): The base path for the user's data directory.
        vizType (str): The type of visualization to generate.

    Returns:
        str or bool: The path to the existing or newly created visualization file if successful, 
                     False if an error occurs during the process.

    Raises:
        Exception: Descriptive error message if any operation within the function fails.
    """
    try:    
        cluster = pathToInputFile
        orig_input_file = f'{cluster}'
        input_file = f'{cluster}'
        print(input_file)
        
        global dataset_type
        dataset_type = determine_dataset_type(input_file)   # Determine and set the dataset type based on the input file.
        
        inputFile_base_name = os.path.basename(input_file).split('.')[0]
        endPath = os.path.relpath(mln_User)

        # Code to identify a username within a given path.
        # Identify the index where "itlab" or username might reside (considering different path structures)
        potential_username_indices = [-1, -2]  # Check both the last and second-last element
        path_components = mln_User.split('/')
        for index in potential_username_indices:
            # Check if the element at the index is not empty and doesn't start with "." (hidden folder)
            if path_components[index] and not path_components[index].startswith("."):
                username = path_components[index]
                print("USERNAME: %s" % username)
                break  # Exit the loop after finding the first valid username
        
        global input_file_extension
        input_file_extension = os.path.splitext(input_file)[-1] if any(input_file.endswith(ext) for ext in [".ecom", ".net", ".vcom"]) else ""
        
        # Define visualization type to simplified graph type mapping
        viz_type_to_graph_type = {
            'plotly_visualization': 'plotly',
            'bokeh_visualization': 'bokeh',
            'bokeh_dc_visualization': 'bokeh',
            'community_network_visualization': 'bokeh',
            'pyvis_visualization': 'pyvis',
            'map_visualization': 'map',
            'word_cloud_visualization': 'wordcloud',
            'bubble_chart_visualization': 'bubblechart',  
            'bar_chart_visualization': 'barchart'         
        }
        vizGraphType = viz_type_to_graph_type.get(vizType, 'unknown')
        print("Visualization graph TYPE: ", vizGraphType)
        
        if username:
            final_output_cluster_name = inputFile_base_name.replace(f"{username}_", '')
            final_output_cluster_name = final_output_cluster_name.replace(f"{username}_", '')
            
        # checking if mapping file exists
        # TODO: check for this mapping input file for com_net     
        mapping_file_path = os.path.join(mappingInputFile, f"{inputFile_base_name}.map")
        print("Mapping file PATH: ", mapping_file_path)
        mappingFile_present = os.path.exists(mapping_file_path)
        print("Mapping file PRESENT: ", mappingFile_present)
        
        # check if we need to create viz or load generated viz
        # if True, create viz and save it
        if createViz(mln_User, final_output_cluster_name, vizGraphType, input_file_extension, orig_input_file):
            print("Create VISUALIZATION: TRUE")
            if input_file.endswith('.net'):
                allEdges = []
                with open(os.path.relpath(input_file), "r") as f:
                    allLines = f.readlines()
                    clusterName = allLines[0].strip()
                    noVerticesLayer1 = allLines[1].strip()
                    noEdges_fromFile = allLines[2].strip()
                    x = int(noVerticesLayer1) + int(3)
                    f.seek(0)  # reset the file pointer to the beginning of the file
                    for line in f.readlines()[x:]:
                        node1, node2, weigth = line.strip().split(',')
                        allEdges.append((node1, node2, float(weigth)))
                    # print(allEdges[0]) # prints node1, node2, weight(1.0)
            elif input_file.endswith('.ecom'):
                # dictionary to maintain the data
                data = {}    
                import networkx as nx
                G = nx.Graph()
                # read input file ---------------------------------------------------------------------------------------------------------------------
                with open(os.path.relpath(input_file), 'r') as f:
                    lines = f.readlines()
                # extract ecom info from input file and store in dictionary
                for i, line in enumerate(lines):
                    if line.startswith('# Edge Community File for Layer'):
                        data['Layer'] = lines[i+1].strip()
                    elif line.startswith('# Number of Vertices'):
                        data['NumVertices'] = int(lines[i+1].strip())
                    elif line.startswith('# Number of Non-Singleton Communities'):
                        data['NumCommunities'] = int(lines[i+1].strip())
                    elif line.startswith('# Number of Community Edges'):
                        data['NumCommunitiesEdges'] = int(lines[i+1].strip())
                    elif line.startswith('# Edge Community Allocation'):
                        data['Communities'] = {}
                        for j in range(i+1, len(lines)):
                            if not lines[j].startswith('#'):
                                v1id, v2id, commID = map(int, lines[j].strip().split(','))
                                G.add_node(v1id, community=commID)
                                G.add_node(v2id, community=commID)
                                G.add_edge(v1id, v2id)
                                if commID not in data['Communities']:
                                    data['Communities'][commID] = []
                                data['Communities'][commID].append((v1id, v2id))
                # print(data['Communities']) #{'Layer': 'L2', 'NumVertices': 6, 'NumCommunities': 4, 'Communities': {1: [1, 2, 3], 2: [4], 3: [5], 4: [6]}}
            elif input_file.endswith('.vcom'):
                # dictionary to maintain the data
                data = {}    
                import networkx as nx
                G = nx.Graph()
                # read input file ---------------------------------------------------------------------------------------------------------------------
                with open(os.path.relpath(input_file), 'r') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines):
                        if line.startswith('# Vertex Community File for Layer'):
                            data['Layer'] = lines[i+1].strip()
                        elif line.startswith('# Number of Vertices'):
                            data['NumVertices'] = int(lines[i+1].strip())
                        elif line.startswith('# Number of Total Communities'):
                            data['NumCommunities'] = int(lines[i+1].strip())
                        elif line.startswith('# Vertex Community Allocation'):
                            data['Communities'] = {}
                            for j in range(i+1, len(lines)):
                                if not lines[j].startswith('#'):
                                    vid, commID = map(int, lines[j].strip().split(','))
                                    if commID in data['Communities']:
                                        data['Communities'][commID].append(vid)
                                    else:
                                        data['Communities'][commID] = [vid]
            
            # create mapper
            mapper = create_mapper(mapping_file_path, mappingFile_present)
                
            vizFunctionToCall = vizDictionary[vizType.lower()]
            
            print(f"Calling {vizFunctionToCall}")
            if input_file.endswith('.net'):
                return(vizFunctionToCall(allEdges, mapper, mln_User, endPath, noEdges_fromFile, noVerticesLayer1, mappingFile_present, clusterName))
            if input_file.endswith('.ecom') or input_file.endswith('.vcom'):
                return(vizFunctionToCall(data, mapper, mln_User, endPath, mappingFile_present, G, input_file, final_output_cluster_name))
        else:
            print("Create viz: FALSE")
            replacer = ""
            if input_file_extension == '.net':
                replacer = "Network"
            if input_file_extension == '.ecom':
                replacer = "ecom"
            if input_file_extension == '.vcom':
                replacer ="vcom"
            return_path_to_viz = os.path.join(mln_User, "visualization", f"{vizGraphType}_{final_output_cluster_name}_{replacer}.html")
            print("VIZ ALREADY EXISTS: ", return_path_to_viz)
            return return_path_to_viz
    except Exception as e:
        print(e)
        return False