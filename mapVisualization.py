import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import networkx as nx
# from geopy.geocoders import Nominatim
# from geopy.extra.rate_limiter import RateLimiter
import os


#ASantra (06/13): Code updated for it to work with Airline map file format (nodeID, "lat,long,airportcode/labelInfo")
def visualization(allEdges, mapper, mln_User, endPath, noEdges_fromFile, noVerticesLayer1, mappingFile_present, clusterName):
    if mappingFile_present:
        # converting the mapper dict to data dict with seperate lists
        data = {
            "Node_id": [],
            "latitude": [],
            "longitude": [],
            "atr_val": []            
        }
        
        #print(mappingFile_present)
        #print(noVerticesLayer1)
        #print(mapper.items([1]))
        numberOfAttr = 0
        for node_id, details in mapper.items():
             #print(details)
             parts = details.split(',')
             numberOfAttr = len(parts)
             data["Node_id"].append(node_id)
             data["latitude"].append(float(parts[0]))
             data["longitude"].append(float(parts[1]))
             if (numberOfAttr > 2):
                 data["atr_val"].append((parts[2]))
        df = pd.DataFrame(data)
        df.set_index('Node_id', inplace=True)
        # # Initialize the geolocator with a user agent to avoid blocks
        # geolocator = Nominatim(user_agent='geoapiExercises')
        # geocode = RateLimiter(geolocator.reverse, min_delay_seconds=1)  # Adding delay to avoid hitting request limits
        # # Fetching city names using latitude and longitude
        # df['location'] = df.apply(lambda row: geocode((row['latitude'], row['longitude'])).address, axis=1)
        
        # Initialize the graph to compute node degrees
        G = nx.Graph()
        G.add_nodes_from(df.index)  # Ensuring all nodes are added to the graph, even if they have no edges
        G.add_edges_from((edge[0], edge[1]) for edge in allEdges if edge[0] in df.index and edge[1] in df.index)
            
        # Calculate degrees
        degrees = dict(G.degree())
        df['degree'] = df.index.map(degrees.get).fillna(0)
        
        # initialize a pltoly figure
        fig = go.Figure()

        # Add traces for the nodes
        if (numberOfAttr > 2):
            fig.add_trace(
                go.Scattermapbox(
                    mode="markers+text",
                    lon=df['longitude'],
                    lat=df['latitude'],
                    marker=go.scattermapbox.Marker(
                        size=15,
                    ),
                    text=df.index,  # Showing node index by default
                    # hover_name=df['location'],
                    hoverinfo='text',
                    hovertext=df.apply(lambda row: f"ID: {row.name}<br>Label: {row.atr_val}<br>Lat: {row.latitude}<br>Lon: {row.longitude}<br>Degree: {row.degree}", axis=1)
                )
            )
        else:
            fig.add_trace(
                go.Scattermapbox(
                    mode="markers+text",
                    lon=df['longitude'],
                    lat=df['latitude'],
                    marker=go.scattermapbox.Marker(
                        size=10,
                    ),
                    text=df.index,  # Showing node index by default
                    # hover_name=df['location'],
                    hoverinfo='text',
                    hovertext=df.apply(lambda row: f"ID: {row.name}<br>Lat: {row.latitude}<br>Lon: {row.longitude}<br>Degree: {row.degree}", axis=1)
                )
            )

        
        # Add traces for the edges
        for edge in allEdges:
            if edge[0] in df.index and edge[1] in df.index:
                fig.add_trace(
                    go.Scattermapbox(
                        mode="lines",
                        lon=[df.loc[edge[0], 'longitude'], df.loc[edge[1], 'longitude']],
                        lat=[df.loc[edge[0], 'latitude'], df.loc[edge[1], 'latitude']],
                        line=dict(color='red',width=0.05),
                        hoverinfo='skip'
                    )
                )
        
        # Update the layout for the map
        fig.update_layout(
            mapbox = {
                'style': "open-street-map",
                'center': go.layout.mapbox.Center(
                    lat = df['latitude'].mean(),
                    lon = df['longitude'].mean()
                ),
                'zoom': 3
            },
            showlegend = False,
            margin = {"r":0, "t":0, "l":0, "b":0}
        )

        #fig.update_layout(mapbox_style="open-street-map")
        #fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        # SAVE FIGURE ------------------------------------------------------------------------
        clusterName = clusterName.split('.')[0] # remove the .txt extension
        save_path = os.path.join(endPath, "visualization",f"map_{clusterName}_Network.html")
        fig.write_html(save_path)
        return os.path.join(mln_User, "visualization", f"map_{clusterName}_Network.html")
