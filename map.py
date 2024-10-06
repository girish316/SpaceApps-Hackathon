import folium
import requests

# Mapping COSEWIC and SARA status codes to labels
COSEWIC_STATUS_MAP = {
    1: 'Extinct', 2: 'Extirpated', 3: 'Endangered', 4: 'Threatened', 5: 'Special Concern'
}

SARA_STATUS_MAP = {
    1: 'Schedule 1', 2: 'Schedule 2', 3: 'Schedule 3'
}

# Map species + population to unique colors as shown in the legend
SPECIES_POPULATION_COLOR_MAP = {
    ("Barren-ground Caribou", "Dolphin and Union"): "#D462FF",  # Purple
    ("Caribou", "Barren-ground"): "#5588FF",  # Blue
    ("Caribou", "Boreal"): "#DACBA4",  # Beige
    ("Peary Caribou", None): "#FFBF4E",  # Orange
    ("Wood Bison", None): "#FF9FCC",  # Pink
    ("Woodland Caribou", "Southern Mountain"): "#5FCB5A",  # Green
}

def create_map():
    # Create base map centered on Canada
    m = folium.Map(
        location=[56.1304, -106.3468],  # Center on Canada
        zoom_start=4,
        control_scale=True,
        tiles=None  # No default tiles
    )

    # Add OpenStreetMap as a base layer
    folium.TileLayer(
        tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="&copy; OpenStreetMap contributors",
        name="OpenStreetMap",
        overlay=False,
        control=True
    ).add_to(m)

    # Add ArcGIS Satellite Imagery as a base layer
    folium.TileLayer(
        tiles="https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="ArcGIS Satellite Imagery",
        overlay=False,
        control=True
    ).add_to(m)

    # Fetch Priority Species data from the ESRI REST service
    esri_rest_url = 'https://maps-cartes.ec.gc.ca/arcgis/rest/services/CWS_SCF/PrioritySpecies/MapServer/0/query'
    params = {
        'where': '1=1',
        'outFields': '*',
        'f': 'geojson'
    }
    
    response = requests.get(esri_rest_url, params=params)
    
    if response.status_code == 200:
        species_data = response.json()  # Get the GeoJSON response

        # Pre-process the data to apply the status mappings before passing to the tooltip
        for feature in species_data['features']:
            # Replace COSEWIC status with its label
            cosewic_status = feature['properties'].get('COSEWIC_Status')
            if cosewic_status is not None:
                feature['properties']['COSEWIC_Status'] = COSEWIC_STATUS_MAP.get(cosewic_status, 'Unknown')

            # Replace SARA status with its label
            sara_status = feature['properties'].get('SARA_Status')
            if sara_status is not None:
                feature['properties']['SARA_Status'] = SARA_STATUS_MAP.get(sara_status, 'Unknown')

        # Define a style function to color the regions based on both species and population
        def style_function(feature):
            species = feature['properties'].get('CommName_E', 'Unknown')
            population = feature['properties'].get('Population_E', None)

            # Map species + population to specific colors from the legend
            color = SPECIES_POPULATION_COLOR_MAP.get((species, population), 'gray')  # Default to gray for unknown

            return {
                'fillColor': color,
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.7
            }

        # Add GeoJSON layer to the map with styling and enhanced tooltip
        folium.GeoJson(
            species_data,
            name="Priority Species Data",
            style_function=style_function,
            tooltip=folium.GeoJsonTooltip(
                fields=['CommName_E', 'Population_E', 'COSEWIC_Status', 'SARA_Status'],
                aliases=['Species', 'Population', 'COSEWIC Status', 'SARA Status'],
                localize=True,
                sticky=True,
            )
        ).add_to(m)
    else:
        print("Failed to fetch data")

    # Add Layer Control for base maps and overlays
    folium.LayerControl(position='topright', collapsed=False).add_to(m)

    # Add a styled legend dropdown with species + population colors
    dropdown_html = '''
    <div style="position: fixed; 
    bottom: 20px; right: 10px; width: 320px; height: auto; 
    background-color: white; border:2px solid grey; border-radius: 8px; padding: 15px; z-index:9999; font-size:14px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
    
    <label for="legend-select" style="font-weight:bold; font-size: 16px; display:block; text-align:center; margin-bottom:10px;">Priority Species Legend:</label>

    <div style="display: flex; align-items: center; margin-bottom: 6px;">
        <div style="background-color: #D462FF; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Barren-ground Caribou, Dolphin and Union population
    </div>
    <div style="display: flex; align-items: center; margin-bottom: 6px;">
        <div style="background-color: #5588FF; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Caribou, Barren-ground population
    </div>
    <div style="display: flex; align-items: center; margin-bottom: 6px;">
        <div style="background-color: #DACBA4; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Caribou, Boreal population
    </div>
    <div style="display: flex; align-items: center; margin-bottom: 6px;">
        <div style="background-color: #FFBF4E; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Peary Caribou
    </div>
    <div style="display: flex; align-items: center; margin-bottom: 6px;">
        <div style="background-color: #FF9FCC; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Wood Bison
    </div>
    <div style="display: flex; align-items: center; margin-bottom: 6px;">
        <div style="background-color: #5FCB5A; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Woodland Caribou, Southern Mountain population
    </div>
    </div>
    '''

    # Add the legend HTML to the map
    m.get_root().html.add_child(folium.Element(dropdown_html))

    # Save the map to the 'templates' folder, replacing the old one
    m.save('templates/map.html')

    print("Map has been created and saved to 'templates/map.html'")

if __name__ == "__main__":
    create_map()
