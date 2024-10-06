import folium
import os

# Mapping COSEWIC and SARA status codes to labels
COSEWIC_STATUS_MAP = {
    1: 'Extinct', 2: 'Extirpated', 3: 'Endangered', 4: 'Threatened', 5: 'Special Concern'
}

# Map species + population to unique colors as shown in the legend
SPECIES_POPULATION_COLOR_MAP = {
    ("Barren-ground Caribou", "Dolphin and Union"): "#D462FF",  # Purple
    ("Caribou", "Barren-ground"): "#5588FF",  # Blue
    ("Caribou", "Boreal"): "#DACBA4",  # Beige
    ("Peary Caribou", None): "#FFBF4E",  # Orange
    ("Greater Sage-grouse", None): "#FA5F55",  # Red
    ("Wood Bison", None): "#FF9FCC",  # Pink
    ("Woodland Caribou", "Southern Mountain"): "#5FCB5A",  # Green
}

# Local path for the saved Priority Species GeoJSON file
PRIORITY_SPECIES_FILE_PATH = 'static/priority_species.geojson'

def load_local_geojson(file_path):
    """Load local GeoJSON file."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return f.read()
    else:
        print(f"File {file_path} does not exist.")
        return None

def create_map():
    """Create the interactive map with priority species."""
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

    # Load local Priority Species GeoJSON data
    species_data = load_local_geojson(PRIORITY_SPECIES_FILE_PATH)
    if species_data:
        # Define a style function to color the species regions
        def style_species(feature):
            species = feature['properties'].get('CommName_E', 'Unknown')
            population = feature['properties'].get('Population_E', None)
            color = SPECIES_POPULATION_COLOR_MAP.get((species, population), 'gray')
            return {
                'fillColor': color,
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.7
            }

        # Add species GeoJSON layer to the map
        folium.GeoJson(
            species_data,
            name="Priority Species Data",
            style_function=style_species,
            tooltip=folium.GeoJsonTooltip(
                fields=['CommName_E', 'Population_E', 'COSEWIC_Status', 'SARA_Status'],
                aliases=['Species', 'Population', 'COSEWIC Status', 'SARA Status'],
                localize=True,
                sticky=True,
            )
        ).add_to(m)

    # Add Layer Control for base maps and overlays
    folium.LayerControl(position='topright', collapsed=False).add_to(m)

    # Add a styled legend dropdown with species + population colors
    dropdown_html = '''
    <div style="position: fixed; bottom: 20px; right: 10px; width: 320px; height: auto;
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
