import os
import plotly.express as px

def visualization(data, mapper, mln_User, endPath, mappingFile_present, G, input_file, final_output_cluster_name):
    try: 
        nodes_OR_edges = ""
        ecom_vcom_FLAG = ""
        unique_EdgesorNodes_InEachCommunity = {}
        
        if input_file.endswith('.ecom'):
            input_file_extension = 'ecom'
            nodes_OR_edges = "edges"
        elif input_file.endswith('.vcom'):
            input_file_extension = 'vcom'
            nodes_OR_edges = "vertices"

        communityData = data.get('Communities') # stores data['Communities']\
            
        # calculating unique nodes in each community --------------------------------------------------------------------------------------
        for communityID, edges in communityData.items():
            if input_file.endswith('.ecom'):
                unique_EdgesorNodes_InEachCommunity[communityID] = len(edges)
            elif input_file.endswith('.vcom'):
                nodes = set()
                for edge in edges:
                    nodes.add(edge[0])
                    nodes.add(edge[1])
                unique_EdgesorNodes_InEachCommunity[communityID] = len(nodes)
                # print(unique_EdgesorNodes_InEachCommunity)   # prints {1: 27, 3: 41, 2: 45} 

        # count the number of vertices in each community --------------------------------------------------------------------------------------
        # verticesInEachCommunity = {'C'+str(key): len(value) if isinstance(value, list) else value for key, value in communityData.items()}
        
        # sorting the data
        sortedData = dict(sorted(unique_EdgesorNodes_InEachCommunity.items(), key=lambda item: item[1], reverse=True))
        
        # Create a bar graph from the verticesInEachCommunity data using Plotly
        fig = px.bar(
            x=list(sortedData.keys()),
            y=list(sortedData.values()),
            #text_auto='.2s',
            labels={'x': 'Community', 'y': f'Number of {nodes_OR_edges}'},
            title=f'Number of {nodes_OR_edges} in Each Community'
        )
        fig.update_traces(
            textangle = 0,
            textposition='outside',
            textfont_size=10,
            cliponaxis=False,
        )
        
        fig.update_xaxes(
            categoryorder='total descending',
        )

        html_file_generated = os.path.join(endPath,"visualization",f"bar_chart_{final_output_cluster_name}_{input_file_extension}.html")
        fig.write_html(html_file_generated)
        return os.path.join(mln_User, "visualization",f"bar_chart_{final_output_cluster_name}_{input_file_extension}.html")
    except Exception as e:
        print(e)
        return False
