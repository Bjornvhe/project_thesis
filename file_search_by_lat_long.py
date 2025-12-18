from netCDF4 import Dataset
import os
from tqdm import tqdm


def find_file_by_spec_point(target_lat, target_lon, folder_path):
    matching_entries = []
    tolerance = 0.5  # degrees, 0.1 degree ~ 11 km
    for folder_name in tqdm(os.listdir(folder_path), desc="Scanning files"):
        if folder_name.startswith('202501'):
            folder_path_ = os.path.join(folder_path, folder_name)
            for file_name in os.listdir(folder_path_):
                if file_name.endswith("_nc"): 
                    file_path = os.path.join(folder_path_, file_name)
                    try:
                        with Dataset(file_path, mode='r') as data:
                            prn_codes = data.variables['PRN'][:]
                            splat = data.variables['splat'][:]
                            splon = data.variables['splon'][:]

                            time_dim, channel_dim = prn_codes.shape

                            for t in range(time_dim):
                                for c in range(channel_dim):
                                    lat = splat[t, c]
                                    lon = splon[t, c]
                                    prn = prn_codes[t, c]

                                    if abs(lat - target_lat) <= tolerance and abs(lon - target_lon) <= tolerance:
                                        print(f" Match found in file: {file_name}, PRN: {prn}, time index: {t}")
                                        matching_entries.append({
                                            'file': file_path,
                                            'prn': int(prn),
                                            'time_index': t,
                                            'lat': lat,
                                            'lon': lon
                                        })
                                        break
                    except Exception as e:
                        print(f"Error reading {file_name}: {e}")

    return matching_entries


if __name__ == "__main__":
    # FILL INN OWN FILE NAME
    folder_path = ''
    print("Provide target latitude and longitude to find the corresponding file:")
    target_lat = float(input()) # Example latitude 10.324902
    target_lon = float(input())  # Example longitude 79.753311
    print(f"Searching for spec.point ({target_lat}, {target_lon}) in files...")

    file_paths = find_file_by_spec_point(target_lat, target_lon, folder_path)
    if file_paths != []:
        print(f"File(s) containing the spec.point ({target_lat}, {target_lon})")
    else:
        print(f"No file found containing the spec.point ({target_lat}, {target_lon})")

