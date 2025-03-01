import folium
from shapely.wkt import loads

# WKT Polygon for the State of Colorado
colorado_wkt = "POLYGON((-109.0603 41.0034, -102.0416 41.0034, -102.0416 36.9931, -109.0603 36.9931, -109.0603 41.0034))"

# WKT Polygons for the Woodland Park area
wp1_wkt = "POLYGON((-105.080 38.980, -105.020 38.980, -105.020 38.920, -105.080 38.920, -105.080 38.980))"
wp2_wkt = "POLYGON((-105.110 38.960, -105.050 38.960, -105.050 38.900, -105.110 38.900, -105.110 38.960))"

# Convert polygons to a Shapely objects
colorado_polygon = loads(colorado_wkt)
wp1_polygon = loads(wp1_wkt)
wp2_polygon = loads(wp2_wkt)

# Create a map centered around Colorado
colorado_centroid = colorado_polygon.centroid
m = folium.Map(location=[colorado_centroid.y, colorado_centroid.x], zoom_start=7)

# Add Colorado polygon to the map
folium.Polygon(locations=[(y, x) for x, y in colorado_polygon.exterior.coords], color="red", fill=True, fill_opacity=0.2).add_to(m)

# Add WP polygons to the map
folium.Polygon(locations=[(y, x) for x, y in wp1_polygon.exterior.coords], color="green", fill=True, fill_opacity=0.5).add_to(m)
folium.Polygon(locations=[(y, x) for x, y in wp2_polygon.exterior.coords], color="green", fill=True, fill_opacity=0.5).add_to(m)

# Save map to file
map_filepath = "co_polygon_map.html"
m.save(map_filepath)