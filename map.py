import folium
import json
from folium.plugins import Draw

def create_map():
    # Create base map centered on Calgary with limited bounds (adjust coordinates for exact city bounds)
    m = folium.Map(
        location=[51.0447, -114.0719], 
        zoom_start=12,
        max_bounds=True,
        control_scale=True,
        tiles=None  # This prevents the default OpenStreetMap layer from being loaded
    )

    # Add ArcGIS World Imagery as the default layer
    folium.TileLayer(
        tiles="https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="ArcGIS Satellite Imagery",
        overlay=True,
        control=True
    ).add_to(m)

    # Add OpenStreetMap tile layer (disabled by default)
    folium.TileLayer(
        tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        name="OpenStreetMap",
        attr="&copy; OpenStreetMap contributors",
        control=True,
        overlay=False  # Not enabled by default
    ).add_to(m)

    # Add Calgary's boundary using a GeoJSON file (disabled by default)
    with open('static/calgary_boundary.geojson', encoding='utf-8') as f:
        geojson_data = json.load(f)
    folium.GeoJson(
        geojson_data, 
        name='Calgary Boundary',
        overlay=False  # Not enabled by default
    ).add_to(m)

    # Add lasso tool using Leaflet Draw
    draw = Draw(export=True)
    draw.add_to(m)

    # Path to the GeoJSON file for all communities
    geojson_path = 'static/all_communities_aggregated.geojson'

    # Load the GeoJSON file
    with open(geojson_path, 'r', encoding='utf-8') as f:
        all_communities_geojson = json.load(f)

    # Function to define color scale based on crime count
    def get_color(crime_count):
        if crime_count > 50:
            return 'darkred'
        elif crime_count > 30:
            return 'red'
        elif crime_count > 15:
            return 'orange'
        elif crime_count > 5:
            return 'yellow'
        else:
            return 'green'

    # Add all communities as a single layer (enabled by default)
    folium.GeoJson(
        all_communities_geojson,
        style_function=lambda feature: {
            'fillColor': get_color(feature['properties']['Crime Count']),
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.5
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['Community', 'Crime Count'],
            aliases=['Community: ', 'Total Crimes: '],
            localize=True
        ),
        name="Crime Heatmap",
        overlay=True  # Enabled by default
    ).add_to(m)

    # Add Layer Control to switch between map layers
    folium.LayerControl().add_to(m)

    # Save the map to HTML
    m.save('templates/map.html')
