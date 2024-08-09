import matplotlib.pyplot as plt
import os
from wordcloud import WordCloud
from io import BytesIO
import base64

def visualization(data, mapper, mln_User, endPath, mappingFile_present, G, input_file_extension, final_output_cluster_name):
    try: 
        communityData = data['Communities']
        
        input_file_extension = input_file_extension.split('.')[1]
        # Determine if the data comes from a vertex community (vcom) or an edge community (ecom)
        nodes_OR_edges = "nodes" if input_file_extension == "vcom" else "edges"
        
        uniqueNodesInEachCommunity = {}
        if input_file_extension == "ecom":
                    # Calculating unique nodes in each community for edge community files
                    for communityID, edges in communityData.items():
                        nodes = set()
                        for edge in edges:
                            nodes.add(edge[0])
                            nodes.add(edge[1])
                        uniqueNodesInEachCommunity[communityID] = len(nodes)

        # count the number of vertices in each community --------------------------------------------------------------------------------------
        verticesInEachCommunity = {'C'+str(key): len(value) if isinstance(value, list) else value for key, value in communityData.items()}  
            # print(len(verticesInEachCommunity)) #{'C1': 3, 'C2': 1, 'C3': 1, 'C4': 1}
        # calculate the number of communities to display in the word cloud --------------------------------------------------------------------
        coms_to_display = min(10, len(verticesInEachCommunity))

        # create word cloud -------------------------------------------------------------------------------------------------------------------
        wordcloud = WordCloud(
            width=500,
            height=500,
            background_color='black',
            colormap='hsv',
            collocations=False,
            min_font_size=10
        )

        # generate based on the number of vertices in each community --------------------------------------------------------------------------
        wordcloud.generate_from_frequencies(verticesInEachCommunity)

        # # plot the word cloud -----------------------------------------------------------------------------------------------------------------
        # Create a subplot with two rows and one column
        fig, (ax1,ax2)= plt.subplots(1, 2, figsize=(14, 6))

        # Plot the word cloud in the first subplot
        ax1.imshow(wordcloud, interpolation="bilinear", aspect='auto')
        # Set the title for the first subplot
        ax1.set_title(f'Word Cloud for {data["Layer"]} Layer', fontsize=16, fontweight='bold', pad=3)
        ax1.axis('off')

        # Add a legend to the second subplot -----------------------------------------------------------------------------------------------
        legend_text = f"Total Communities in {data['Layer']} Layer: {data['NumCommunities']}\n"
        legend_text += f"All communities in {data['Layer']} Layer:\n" if coms_to_display <= 10 else f"Top 10 Communities in {data['Layer']} Layer:\n"
        
        if input_file_extension == "vcom":
            legend_text += f"\n".join([f"{key}: {value} {nodes_OR_edges}" for key, value in sorted(verticesInEachCommunity.items(), key=lambda item: item[1], reverse=True)[:coms_to_display]])
        elif input_file_extension == "ecom":
            # join to legent text to print the following C1(communityID): 100(number of nodes) nodes, 200(number of edges) edges
            community_legend_text = []

            for communityID, nodes_count in sorted(uniqueNodesInEachCommunity.items(), key=lambda item: item[1], reverse=True)[:coms_to_display]:
                edges_count = verticesInEachCommunity.get('C'+str(communityID))

                # calculate the avergae density of each community if nodes is more than 0 else the value is 0
                average_degree = (2 * edges_count) / (nodes_count if nodes_count > 0 else 1)
                density = (2 * edges_count) / (nodes_count * (nodes_count - 1) if nodes_count > 1 else 1)

                community_legend_text.append(f"C{communityID}: {nodes_count} nodes, {edges_count} edges, {average_degree:.2f} average degree, {density:.2f} density")
            legend_text += "\n".join(community_legend_text)

        ax2.text(0, 1, legend_text, fontsize=12, va = 'top', ha = 'left', multialignment ='left')
        # Adjust the layout of the subplots
        fig.tight_layout(w_pad=-1)
        ax2.axis("off")
        
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

        # saving the word cloud as HTML file --------------------------------------------------------------------------------------------------
        endPath = os.path.relpath(mln_User)
        layerName = data['Layer']
        tmpfile = BytesIO()  # Create a BytesIO object to hold the image data
        plt.savefig(tmpfile, format="png", bbox_inches="tight", pad_inches=0)
        plt.close()
        # fig.savefig(tmpfile, format='png')  # Save the figure to the BytesIO object as PNG
        encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')  # Encode the image data as base64

        html_content = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body>
            <img src="data:image/png;base64,{encoded}" alt="Word Cloud">
        </body>
        </html>
        """
        # html_content = f'<img src=\'data:image/png;base64,{encoded}'
        html_path = os.path.join(endPath,"visualization",f"wordcloud_{final_output_cluster_name}_{input_file_extension}.html")
        with open(html_path, "w") as f:
            f.write(html_content)
        return html_path
    except Exception as e:
        print(e)
        return False