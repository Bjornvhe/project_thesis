import os
import plotly.graph_objects as go
from netCDF4 import Dataset
from pyproj import Transformer


# Base directory containing folders named YYYYMMDD
#FILL IN OWN FILE NAME LOCATION
base_path = ''

# List available folders
folders = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d)) and d.isdigit()]
print("Available folders (YYYYMMDD):")
for i, folder in enumerate(folders):
    print(f"{i + 1}: {folder}")

# Choose a folder
folder_choice = input("Enter the number of the folder you want to explore: ")
try:
    folder_index = int(folder_choice.strip()) - 1
    selected_folder = folders[folder_index]
except (ValueError, IndexError):
    print("Invalid folder selection.")
    exit()

# Full path to selected folder
folder_path = os.path.join(base_path, selected_folder)

# List netCDF files in the selected folder
nc_files = [f for f in os.listdir(folder_path) if f.endswith("_nc")]
print(f"\nAvailable netCDF files in {selected_folder}:")
for i, file_name in enumerate(nc_files):
    print(f"{i + 1}: {file_name}")

# Choose files to visualize
file_choice = input("Enter the numbers of the files you want to visualize (comma-separated): ")
try:
    selected_indices = [int(i.strip()) - 1 for i in file_choice.split(',')]
    selected_files = [nc_files[i] for i in selected_indices if 0 <= i < len(nc_files)]
except (ValueError, IndexError):
    print("Invalid file selection.")
    exit()

# Initialize Plotly figure and coordinate transformer
fig = go.Figure()
transformer = Transformer.from_crs("epsg:4978", "epsg:4326", always_xy=True)

# Loop through selected files
for selected_file in selected_files:
    file_path = os.path.join(folder_path, selected_file)

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        continue

    try:
        with Dataset(file_path, mode='r') as data:
            prn_codes = data.variables['PRN'][:]
            splat = data.variables['splat'][:]
            splon = data.variables['splon'][:]
            SVPosX = data.variables['SVPosX'][:]
            SVPosY = data.variables['SVPosY'][:]
            SVPosZ = data.variables['SVPosZ'][:]

            time_dim, channel_dim = prn_codes.shape

            # Plot specular point segments
            for c in range(channel_dim):
                for t in range(time_dim - 1):
                    lat_segment = splat[t:t+2, c]
                    lon_segment = splon[t:t+2, c]
                    prn = prn_codes[t, c]

                    fig.add_trace(go.Scattergeo(
                        lon=lon_segment,
                        lat=lat_segment,
                        mode='lines',
                        line=dict(width=1),
                        name=f'PRN {prn}',
                        showlegend=False
                    ))

            # Transform satellite position from ECEF to lat/lon
            sat_lon, sat_lat, _ = transformer.transform(SVPosX, SVPosY, SVPosZ)

            fig.add_trace(go.Scattergeo(
                lon=sat_lon,
                lat=sat_lat,
                mode='lines',
                line=dict(color='red', width=2),
                name=f'Satellite Track ({selected_file})'
            ))

    except Exception as e:
        print(f"Error reading {selected_file}: {e}")

# Final plot layout
fig.update_layout(
    title='Specular Points and LEO Satellite Tracks',
    geo=dict(
        projection_type='natural earth',
        showland=True,
        landcolor='rgb(217, 217, 217)',
        showcountries=True
    )
)

# Show the plot
fig.show()
