import urllib.parse

def determine_dataset_type(path_to_input_file):
    """
    Determines the dataset type based on keywords found in the file path.

    This function examines the file path for specific keywords to categorize the dataset.
    If 'Airlines' is found in the path, it categorizes it as 'airport'. If 'IMDb' is found,
    it is categorized as 'movies'. If 'USCounty' is found, it is categorized as 'USCounty'. 
    If 'DBLP' is found, it is categorized as 'DBLP'.
    If 'Accident' is found, it is categorized as 'Accident'
    If none of these keywords are present, it returns 'unknown'.

    Parameters:
        path_to_input_file (str): The file path of the input data.

    Returns:
        str: A string representing the dataset type ('airport', 'movies', 'USCounty', 'DBLP', 'Accident', or 'unknown').
    """
    if 'Airlines' in path_to_input_file:
        return 'airport'
    elif 'IMDb' in path_to_input_file:
        return 'movies'
    elif 'USCounty' in path_to_input_file:
        return 'USCounty'
    elif 'DBLP' in path_to_input_file:
        return 'DBLP'
    elif 'Accident' in path_to_input_file:
        return 'Accident'
    return 'unknown'

def create_url(node_label, dataset_type):
    """
    Creates a URL based on the node label and dataset type.

    This function generates a URL for a Google search query related to the node label,
    formatted according to the dataset type. If the dataset type is 'airport', it generates
    a Google Maps search URL for airports. If the dataset type is 'movies', it generates
    a Google search URL for the movie title on IMDb. If the dataset type is 'USCounty',
    it generates a Google search URL for county information.

    Parameters:
        node_label (str): The label of the node, which could be an airport name, movie title, or county name.
        dataset_type (str): The type of dataset ('airport', 'movies', 'USCounty', 'DBLP', 'Accident') which determines the URL format.

    Returns:
        str or None: The URL as a string if applicable, or None if the dataset type is 'unknown' or node_label is "0".
    """
    if dataset_type == 'airport':
        if node_label != "0":
            airport_code = node_label.split(',')[2]  # Assumes 'node_label' format is "id,lat,long,airportCode"
            return f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote_plus(airport_code)}+airport"
#            return f"https://www.google.com/maps/search/?api=1&query={node_label}"
    elif dataset_type == 'movies':
        if node_label != "0":
            # Extracting the movie title from the mapper output
            title = node_label.split(',')[1]  # Assumes 'node_label' format is "id,title"
            movie_search_query = urllib.parse.quote_plus(f"{title} IMDb")
            return f"https://www.google.com/search?q={movie_search_query}"
    elif dataset_type == 'USCounty':
        if node_label != "0":
            return f"https://www.google.com/search?q={urllib.parse.quote_plus(node_label)}+county"
    elif dataset_type == 'DBLP':
        if node_label != "0":
            # Extracting the author list from the mapper output
            author_list = node_label.split(',', 1)[1]  # Assumes 'node_label' format is "id,author_list"
            #author_search_query = urllib.parse.quote_plus(f"{author_list}")
            return f"https://www.google.com/search?q={author_list}"
    elif dataset_type == 'Accident':
        if node_label != "0":
#            return f"https://www.google.com/maps/search/?api=1&query={node_label}"
            # Extracting the latitude and longitude values either "lat,long" or "lat,long,attr_val"
            location = ','.join(node_label.split(',')[:2])
            return f"https://www.google.com/maps/search/?api=1&query={location}"            
    return None  # For 'unknown' or any other type, do not create a URL
