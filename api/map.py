import folium
import os
import json
import requests
from folium.plugins import Draw
SPECIES_POPULATION_COLOR_MAP = {
    ("Barren-ground Caribou", "Dolphin and Union"): "#D462FF",  # Purple
    ("Caribou", "Barren-ground"): "#5588FF",  # Blue
    ("Caribou", "Boreal"): "#DACBA4",  # Beige
    ("Peary Caribou", None): "#FFBF4E",  # Orange
    ("Greater Sage-grouse", None): "#FA5F55",  # Red
    ("Wood Bison", None): "#FF9FCC",  # Pink
    ("Woodland Caribou", "Southern Mountain"): "#5FCB5A",  # Green
}

PRIORITY_SPECIES_FILE_PATH = 'static/priority_species.geojson'

def load_local_geojson(file_path):
    """Load local GeoJSON file and return it as a dictionary."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)  # Load it as a dictionary
    else:
        print(f"File {file_path} does not exist.")
        return None

def preprocess_species_data(species_data):
    """Preprocess the GeoJSON data by replacing COSEWIC status codes with labels."""
    COSEWIC_STATUS_MAP = {
        1: 'Extinct', 2: 'Extirpated', 3: 'Endangered', 4: 'Threatened', 5: 'Special Concern'
    }
    for feature in species_data['features']:
        cosewic_status_code = feature['properties'].get('COSEWIC_Status')
        if cosewic_status_code in COSEWIC_STATUS_MAP:
            feature['properties']['COSEWIC_Status_Label'] = COSEWIC_STATUS_MAP[cosewic_status_code]
        else:
            feature['properties']['COSEWIC_Status_Label'] = 'Unknown'
    return species_data

def add_priority_species_layer(m):
    """Add the priority species layer to the map."""
    species_data = load_local_geojson(PRIORITY_SPECIES_FILE_PATH)
    if species_data:
        species_data = preprocess_species_data(species_data)

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

        folium.GeoJson(
            species_data,
            name="Priority Species Data",
            style_function=style_species,
            tooltip=folium.GeoJsonTooltip(
                fields=['CommName_E', 'Population_E', 'COSEWIC_Status_Label', 'SARA_Status'],
                aliases=['Species', 'Population', 'COSEWIC Status', 'SARA Status'],
                localize=True,
                sticky=True
            )
        ).add_to(m)
    else:
        print("No priority species data to load.")

def add_critical_habitat_layer(m):
    """Add the critical habitat WMS layer to the map."""
    try:
        folium.WmsTileLayer(
            url='https://maps-cartes.ec.gc.ca/arcgis/services/CWS_SCF/CriticalHabitat/MapServer/WMSServer',
            layers='0',
            name="Critical Habitat Data",
            fmt='image/png',
            transparent=True,
            control=True
        ).add_to(m)
    except Exception as e:
        print(f"Error adding Critical Habitat WMS layer: {e}")

def add_vegetation_zones_layer(m):
    """Add the Vegetation Zones GeoJSON layer to the map."""
    VEGETATION_ZONES_FILE_PATH = 'static/vegetation_map.geojson'

    VEGETATION_COLOR_MAP = {
    "High Arctic Sparse Tundra": "#D4E157",
    "Mid-Arctic Dwarf Shrub Tundra": "#FFEB3B",
    "Low Arctic Shrub Tundra": "#FFC107",
    "Subarctic Alpine Tundra": "#FF9800",
    "Western Boreal Alpine Tundra": "#F57C00",
    "Cordilleran Alpine Tundra": "#E65100",
    "Pacific Alpine Tundra": "#A5D6A7",
    "Eastern Alpine Tundra": "#66BB6A",
    "Subarctic Woodland-Tundra": "#81C784",
    "Northern Boreal Woodland": "#4CAF50",
    "Northwestern Boreal Forest": "#388E3C",
    "West-Central Boreal Forest": "#2E7D32",
    "Eastern Boreal Forest": "#1B5E20",
    "Atlantic Maritime Heathland": "#26A69A",
    "Pacific Maritime Rainforest": "#80CBC4",
    "Pacific Dry Forest": "#00796B",
    "Pacific Montane Forest": "#004D40",
    "Cordilleran Subboreal Forest": "#8E24AA",
    "Cordilleran Montane Forest": "#5E35B1",
    "Cordilleran Rainforest": "#4527A0",
    "Cordilleran Dry Forest": "#311B92",
    "Eastern Temperate Mixed Forest": "#3949AB",
    "Eastern Temperate Deciduous Forest": "#1E88E5",
    "Acadian Temperate Forest": "#1976D2",
    "Rocky Mountains Foothills Parkland": "#0D47A1",
    "Great Plains Parkland": "#BBDEFB",
    "Intermontane Shrub-Steppe": "#90CAF9",
    "Rocky Mountains Foothills Fescue Grassland": "#64B5F6",
    "Great Plains Fescue Grassland": "#42A5F5",
    "Great Plains Mixedgrass Grassland": "#2196F3",
    "Central Tallgrass Grassland": "#1E88E5",
    "Cypress Hills": "#1565C0",
    "Glaciers": "#0D47A1"
    }


    vegetation_data = load_local_geojson(VEGETATION_ZONES_FILE_PATH)

    if vegetation_data:
        folium.GeoJson(
            vegetation_data,
            name="Vegetation Zones",
            style_function=lambda feature: {
                'fillColor': VEGETATION_COLOR_MAP.get(feature['properties']['level_2'], 'gray'),
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.6
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['level_1'],
                aliases=['Vegetation Zone:'],
                localize=True,
                sticky=True
            )
        ).add_to(m)
    else:
        print("No vegetation data to load.")

def add_wildfire_hotspots_layer(m):
    """Add the Wildfire hotspots WMS layer to the map."""
    try:
        folium.WmsTileLayer(
            url='https://geo.weather.gc.ca/geomet',
            layers='RAQDPS-FW.CE_HOTSPOTS.2019',
            name="Wildfire Hotspots 2019",
            fmt='image/png',
            transparent=True,
            control=True
        ).add_to(m)
    except Exception as e:
        print(f"Error adding Wildfire Hotspots WMS layer: {e}")

def add_protected_areas_wms_layer(m):
    """Add the protected areas WMS layer to the map."""
    try:
        folium.WmsTileLayer(
            url='https://maps-cartes.ec.gc.ca/arcgis/services/CWS_SCF/CPCAD/MapServer/WMSServer',
            layers='0',
            name="Protected Areas Data",
            fmt='image/png',
            transparent=True,
            control=True
        ).add_to(m)
    except Exception as e:
        print(f"Error adding Protected Areas WMS layer: {e}")


def create_map():
    """Create the interactive map with priority species and critical habitats."""
    m = folium.Map(
        location=[56.1304, -106.3468],
        zoom_start=4,
        control_scale=True,
        tiles=None
    )

    folium.TileLayer(
        tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="&copy; OpenStreetMap contributors",
        name="OpenStreetMap",
        overlay=False,
        control=True
    ).add_to(m)

    folium.TileLayer(
        tiles="https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="ArcGIS Satellite Imagery",
        overlay=False,
        control=True
    ).add_to(m)


    add_priority_species_layer(m)
    add_critical_habitat_layer(m)
    add_vegetation_zones_layer(m)
    add_wildfire_hotspots_layer(m)

    add_protected_areas_wms_layer(m)

    draw = Draw(export=True)
    draw.add_to(m)

    folium.LayerControl(position='topright', collapsed=False).add_to(m)

    dropdown_html = '''
        <div style="position: fixed; bottom: 20px; right: 10px; width: 320px; height: auto;
                    background-color: white; border:2px solid grey; border-radius: 8px; padding: 15px; z-index:9999; font-size:14px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">

            <label for="legend-select" style="font-weight:bold; font-size: 16px; display:block; text-align:center; margin-bottom:10px;">Select Legend:</label>
            
            <!-- Dropdown to switch between legends -->
            <select id="legend-select" style="width: 100%; padding: 5px; font-size: 14px;" onchange="showLegend()">
                <option value="priority">Priority Species Legend</option>
                <option value="critical">Critical Habitat Legend</option>
                <option value="vegetation">Vegetation Zones Legend</option>
                <option value="wildfire">Wildfire Hotspots Legend</option>
                <option value="protected">Protected Areas Legend</option>
            </select>

            <!-- Priority Species Legend -->
            <div id="priority-legend" style="display: block;">
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
                    <div style="background-color: #FA5F55; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Greater Sage-grouse
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #FF9FCC; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Wood Bison
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #5FCB5A; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Woodland Caribou, Southern Mountain population
                </div>
            </div>

            <!-- Critical Habitat Legend with Gradient -->
            <div id="critical-legend" style="display: none;">
                <strong>Critical Habitat Legend</strong><br>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #FEDEC2; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Low Criticality Habitat Area
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #FDC6A2; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Moderate Criticality Habitat Area
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #E84841; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> High Criticality Habitat Area
                </div>
            </div>

            <!-- Vegetation Zones Legend -->
            <div id="vegetation-legend" style="display: none; max-height: 300px; overflow-y: scroll;">
                <strong>Vegetation Zones Legend</strong><br>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #D4E157; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> High Arctic Sparse Tundra
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #FFEB3B; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Mid-Arctic Dwarf Shrub Tundra
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #FFC107; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Low Arctic Shrub Tundra
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #FF9800; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Subarctic Alpine Tundra
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #F57C00; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Western Boreal Alpine Tundra
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #E65100; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Cordilleran Alpine Tundra
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #A5D6A7; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Pacific Alpine Tundra
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #66BB6A; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Eastern Alpine Tundra
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #81C784; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Subarctic Woodland-Tundra
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #4CAF50; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Northern Boreal Woodland
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #388E3C; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Northwestern Boreal Forest
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #2E7D32; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> West-Central Boreal Forest
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #1B5E20; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Eastern Boreal Forest
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #26A69A; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Atlantic Maritime Heathland
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #80CBC4; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Pacific Maritime Rainforest
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #00796B; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Pacific Dry Forest
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #004D40; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Pacific Montane Forest
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #8E24AA; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Cordilleran Subboreal Forest
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #5E35B1; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Cordilleran Montane Forest
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #4527A0; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Cordilleran Rainforest
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #311B92; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Cordilleran Dry Forest
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #3949AB; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Eastern Temperate Mixed Forest
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #1E88E5; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Eastern Temperate Deciduous Forest
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #1976D2; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Acadian Temperate Forest
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #0D47A1; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Rocky Mountains Foothills Parkland
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #BBDEFB; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Great Plains Parkland
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #90CAF9; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Intermontane Shrub-Steppe
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #64B5F6; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Rocky Mountains Foothills Fescue Grassland
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #42A5F5; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Great Plains Fescue Grassland
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #2196F3; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Great Plains Mixedgrass Grassland
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #1E88E5; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Central Tallgrass Grassland
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #1565C0; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Cypress Hills
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #0D47A1; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Glaciers
                </div>
            </div>

            <!-- Wildfire Hotspots Legend -->
            <div id="wildfire-legend" style="display: none;">
                <strong>Wildfire Hotspots Legend</strong><br>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #CFCFCF; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Low hotspot activity
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #F9DA7B; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Moderate hotspot activity
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #DE4A00; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> High hotspot activity
                </div>
            </div>

             <!-- Protected Areas Legend -->
            <div id="protected-legend" style="display: none;">
                <strong>Protected Areas Legend</strong><br>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #006400; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Terrestrial protected area
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #90EE90; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Terrestrial other effective area-based conservation measure
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #0000FF; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Marine protected area
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #00BFFF; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Marine other effective area-based conservation measure
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="background-color: #A9A9A9; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Not included in statistics
                </div>
            </div>

        </div>

<script>
    function showLegend() {
        var selectedLegend = document.getElementById("legend-select").value;
        document.getElementById("priority-legend").style.display = (selectedLegend === "priority") ? "block" : "none";
        document.getElementById("critical-legend").style.display = (selectedLegend === "critical") ? "block" : "none";
        document.getElementById("vegetation-legend").style.display = (selectedLegend === "vegetation") ? "block" : "none";
        document.getElementById("wildfire-legend").style.display = (selectedLegend === "wildfire") ? "block" : "none";
        document.getElementById("protected-legend").style.display = (selectedLegend === "protected") ? "block" : "none";
    }
</script>
    '''


    m.get_root().html.add_child(folium.Element(dropdown_html))

    m.save('templates/map.html')

if __name__ == "__main__":
    create_map()
