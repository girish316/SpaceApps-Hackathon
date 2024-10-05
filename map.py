import folium
import json
from folium.plugins import Draw

def create_map():
    # Create base map centered on Calgary
    m = folium.Map(
        location=[51.0447, -114.0719], 
        zoom_start=12,
        control_scale=True,
        tiles=None  # Prevents default OpenStreetMap layer from being loaded
    )

    # Add ArcGIS World Imagery as the default layer
    folium.TileLayer(
        tiles="https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="ArcGIS Satellite Imagery",
        overlay=False,
        control=True
    ).add_to(m)

    # Add OpenStreetMap tile layer (optional)
    folium.TileLayer(
        tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        name="OpenStreetMap",
        attr="&copy; OpenStreetMap contributors",
        overlay=False  # Not enabled by default
    ).add_to(m)

    # Add lasso tool
    draw = Draw(export=True)
    draw.add_to(m)

    # Load the GeoJSON file for crime data
    geojson_path = 'static/all_communities_aggregated.geojson'
    with open(geojson_path, 'r', encoding='utf-8') as f:
        all_communities_geojson = json.load(f)

    # Get crime data and color scaling
    crime_counts = [feature['properties']['Crime Count'] for feature in all_communities_geojson['features']]
    mean_crime = sum(crime_counts) / len(crime_counts)

    def get_color(crime_count):
        if crime_count > mean_crime:
            return 'red'
        elif crime_count > (mean_crime / 2):
            return 'orange'
        else:
            return 'green'

    # Add crime heatmap
    folium.GeoJson(
        all_communities_geojson,
        style_function=lambda feature: {
            'fillColor': get_color(feature['properties']['Crime Count']),
            'color': 'transparent',
            'weight': 0,
            'fillOpacity': 0.3
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['Community', 'Crime Count'],
            aliases=['Community: ', 'Total Crimes: '],
            localize=True
        ),
        name="Crime Heatmap",
        overlay=True
    ).add_to(m)

    # Load the traffic data from GeoJSON
    traffic_geojson_path = 'static/traffic_2023.geojson'
    with open(traffic_geojson_path, 'r', encoding='utf-8') as f:
        traffic_geojson = json.load(f)

    # Fix field names: replace spaces with underscores
    for feature in traffic_geojson['features']:
        feature['properties']['Section_Name'] = feature['properties'].pop('Section Name')
        feature['properties']['Traffic_Volume'] = feature['properties'].pop('Volume')

    # Function to define line color and weight based on traffic volume
    def get_traffic_style(volume):
        if volume > 122016:
            return {'color': '#5A2A8E', 'weight': 12}  # Purple
        elif volume > 92512:
            return {'color': '#2F5FA0', 'weight': 9}  # Dark Blue
        elif volume > 63008:
            return {'color': '#4AA9E4', 'weight': 6}  # Moderate Blue
        elif volume > 33504:
            return {'color': '#7FC3EB', 'weight': 3}  # Sky Blue
        else:
            return {'color': '#B3DDF2', 'weight': 2}  # Light Blue

    # Add the traffic data layer to the map with gradient coloring
    folium.GeoJson(
        traffic_geojson,
        name="Traffic Volume Flow",
        style_function=lambda feature: get_traffic_style(feature['properties']['Traffic_Volume']),
        tooltip=folium.GeoJsonTooltip(
            fields=['Section_Name', 'Traffic_Volume'],  # Use sanitized field names
            aliases=['Road Section', 'Traffic Volume']
        )
    ).add_to(m)

    # Load police stations GeoJSON and add markers to the map
    police_stations_path = 'static/police_stations.geojson'
    with open(police_stations_path, 'r', encoding='utf-8') as f:
        police_geojson = json.load(f)

    # Add police station markers with styled tooltips
    folium.GeoJson(
        police_geojson,
        name="Police Stations",
        marker=folium.CircleMarker(radius=7, color='green', fill=True, fill_opacity=1),
        tooltip=folium.GeoJsonTooltip(
            fields=['NAME', 'STATION_TY', 'INFO'],
            aliases=['Name', 'Station Type', 'Contact Info'],
            localize=True
        )
    ).add_to(m)

    # Load the community services GeoJSON and add as a layer
    community_services_path = 'static/community_services.geojson'
    with open(community_services_path, 'r', encoding='utf-8') as f:
        community_services_geojson = json.load(f)

    # Add community services layer with styled tooltips using available fields
    folium.GeoJson(
        community_services_geojson,
        name="Community Services",
        marker=folium.CircleMarker(radius=5, color='red', fill=True, fill_opacity=.8),
        tooltip=folium.GeoJsonTooltip(
            fields=['NAME', 'ADDRESS', 'TYPE'],  # Use available fields like NAME, ADDRESS, TYPE
            aliases=['Service Name', 'Address', 'Service Type'],  # Adjust aliases accordingly
            localize=True
        )
    ).add_to(m)

    # Add Layer Control to switch between layers
    folium.LayerControl().add_to(m)

    # Add a legend container with dropdown (styled and positioned in the bottom right)
    dropdown_html = '''
    <div style="position: fixed; 
    bottom: 10px; right: 10px; width: 320px; height: auto; 
    background-color: white; border:2px solid grey; border-radius: 8px; padding: 15px; z-index:9999; font-size:14px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
    
    <label for="legend-select" style="font-weight:bold; font-size: 16px; display:block; text-align:center; margin-bottom:10px;">Select a Legend:</label>
    <select id="legend-select" style="width: 100%; padding: 8px; font-size: 14px; border: 2px solid grey; border-radius: 5px; background-color: #f9f9f9;">
        <option value="none">None</option>
        <option value="traffic-legend">Traffic Volume Flow</option>
        <option value="crime-legend">Crime Heatmap</option>
    </select>

    <!-- Traffic Volume Flow Legend (Initially hidden) -->
    <div id="traffic-legend" style="display:none; margin-top:15px;">
        <div style="background-color: #4AA9E4; color: white; padding: 8px; text-align: center; font-weight: bold; border-radius: 5px; margin-bottom: 10px;">
        Traffic Volumes for 2023
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 6px;">
            <div style="background-color: #5A2A8E; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> 122,016 - 151,520
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 6px;">
            <div style="background-color: #2F5FA0; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> 92,512 - 122,016
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 6px;">
            <div style="background-color: #4AA9E4; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> 63,008 - 92,512
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 6px;">
            <div style="background-color: #7FC3EB; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> 33,504 - 63,008
        </div>
        <div style="display: flex; align-items: center;">
            <div style="background-color: #B3DDF2; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> 4,000 - 33,504
        </div>
    </div>

    <!-- Crime Heatmap Legend (Initially hidden) -->
    <div id="crime-legend" style="display:none; margin-top:15px;">
        <div style="background-color: #FF0000; color: white; padding: 8px; text-align: center; font-weight: bold; border-radius: 5px; margin-bottom: 10px;">
        Crime Heatmap
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 6px;">
            <div style="background-color: red; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> High Crime
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 6px;">
            <div style="background-color: orange; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Medium Crime
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 6px;">
            <div style="background-color: green; width: 30px; height: 15px; border-radius: 2px; margin-right: 10px;"></div> Low Crime
        </div>
    </div>
    </div>
    '''

    # Add dropdown to the map
    m.get_root().html.add_child(folium.Element(dropdown_html))

    # Add JavaScript to handle legend visibility
    m.get_root().html.add_child(folium.Element('''
    <script>
        document.getElementById("legend-select").addEventListener("change", function() {
            var selectedLegend = this.value;

            // Hide both legends first
            document.getElementById("traffic-legend").style.display = "none";
            document.getElementById("crime-legend").style.display = "none";

            // Show the selected legend
            if (selectedLegend === "traffic-legend") {
                document.getElementById("traffic-legend").style.display = "block";
            } else if (selectedLegend === "crime-legend") {
                document.getElementById("crime-legend").style.display = "block";
            }
        });
    </script>
    '''))

    # Save the map to HTML
    m.save('templates/map.html')
