import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from netCDF4 import Dataset
import os
from math import radians, cos, sin, sqrt, atan2


def load_nc_file(file_path):
    return Dataset(file_path, mode='r')

def extract_ddm(data):
    ddms = data.variables['DDMpower'][:]
    prns = data.variables['PRN'][:]
    gps_weeks = data.variables['GPSWeek'][:]
    gps_secs = data.variables['GPSSec'][:]
    quality_flags = data.variables['quality_flags'][:]
    splat = data.variables['splat'][:]
    splon = data.variables['splon'][:]
    code_phase = data.variables['CodePhase'][:]
    doppler_freq = data.variables['DopplerFrequency'][:]
    doppler_shift = data.variables['DopplerShift'][:]

    return (ddms, prns, gps_weeks, gps_secs,
            quality_flags, splat, splon,
            doppler_freq, doppler_shift, code_phase)

def plot_ddm(ddm, prn, splat, splon, gps_week, gps_sec, flags,
             DopplerFrequency, DopplerShift, CodePhase, index):

    Ndopp, Ncode = ddm.shape 

    # ---- Physical bin spacing ----
    code_bin = 0.25      # chips/bin assumed value, NOT PROVIDED MIGHT BE WRONG
    doppler_bin = 500.0  # Hz/bin

    # ---- Centers ----
    code_center = Ncode // 2
    dopp_center = Ndopp // 2    # 32

    # ---- Axis limits ----
    code_min = CodePhase + (0 - code_center) * code_bin
    code_max = CodePhase + (Ncode - code_center - 1) * code_bin

    dopp_min = DopplerFrequency + (0 - dopp_center + DopplerShift) * doppler_bin
    dopp_max = DopplerFrequency + (Ndopp - dopp_center - 1 + DopplerShift) * doppler_bin

    plt.figure(figsize=(8, 6))

    plt.imshow(
        ddm,
        origin="lower",
        aspect="auto",
        cmap="viridis",
        extent=[code_min, code_max, dopp_min, dopp_max]
    )

    plt.colorbar(label="Power [W]")
    plt.xlabel("Code delay [chips]")
    plt.ylabel("Doppler frequency [Hz]")

    flag_text = " | ".join(flags) if flags else "No flags"
    plt.title(
        f"DDM PRN {prn}\n"
        f"SP lat/lon ({splat:.6f}, {splon:.6f})\n"
        f"GPS Week {gps_week}, Sec {gps_sec}\n"
        f"Flags: {flag_text}"
    )

    plt.tight_layout()
    plt.savefig(
        f""
        f"ddm_prn{prn}_idx{index}.png"
    )
    plt.close()


def haversine(lat1, lon1, lat2, lon2):
    # Earth radius in kilometers
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def process_files(data_file, target_lat, target_lon, radius_km):
    data = load_nc_file(data_file)
    (ddms, prns, gps_weeks, gps_secs, quality_flags, splat, splon, doppler_freq, doppler_shift, code_phase) = extract_ddm(data)

    for i in range(len(ddms)):
        for j in range(prns.shape[1]):
            splat_prn = splat[i][j]
            splon_prn = splon[i][j]
            distance = haversine(target_lat, target_lon, splat_prn, splon_prn)

            if distance <= radius_km:
                ddm = ddms[i][j]
                prn = prns[i][j]
                flag_value = quality_flags[i][j]
                flags = decode_flags(flag_value)
                print(f'Generating DDM number {i+1} for PRN: {prn} at distance {distance:.2f} km')
                plot_ddm(ddm,prn,splat_prn,splon_prn,gps_weeks[i],gps_secs[i],flags,doppler_freq[i][j],doppler_shift[i][j],code_phase[i][j], f"{i}_{j}")

            else:
                prn = prns[i][j]
                print(f'Skipping DDM number {i+1} for PRN: {prn} at distance {distance:.2f} km (outside radius)')

    print("Filtered DDM plots generated.")

def decode_flags(flag_value): # Decodes the bitmask inside quality_flag variable
    flags = {
        2: "SP on land",
        4: "SP near land",
        8: "DDM max out of range",
        16: "Failed data",
        32: "Instrument temperature error",
        64: "Low signal (<3× noise std)",
        128: "Spike anomaly",
        256: "LEO telemetry error",
        512: "LEO telemetry error",
        1024: "Effected DDM"
    }
    active_flags = [desc for bit, desc in flags.items() if flag_value & bit]
    return active_flags

def list_nc_files(base_path):
    if not os.path.exists(base_path):
        print(f"Folder not found: {base_path}")
        return
    nc_files = []
    for folder_name in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder_name)
        nc_files += [f for f in os.listdir(folder_path) if f.endswith("nc")]
        if not nc_files:
            print("No netCDF files found.")
            return
    #Name selection
    indx_or_name = input("Select file by index or name (i/n): ").strip().lower()
    if indx_or_name == 'n':
        file_name = input("Enter the exact file name: ").strip()
        if file_name in nc_files:
            folder_name = file_name[14:22]
            full_path = os.path.join(base_path, folder_name, file_name)
            print(f"Selected file: {full_path}")
            return full_path
        else:
            print("File not found in the directory.")
            return
    print("Select a netCDF file by index:")
    print('File descriptions: TRITON_YYMMDD_HHMMSS_CorDDM_v2.0_nc')
    for idx, file in enumerate(nc_files):
        print(f"{idx + 1}: {file}")

    #Indexed selection
    selected = input()  
    selected_index = int(selected) - 1
    selected_file = nc_files[selected_index]
    full_path = os.path.join(folder_path, selected_file)
    print(f"Selected file: {full_path}")
    return full_path

if __name__ == "__main__":
    #FILL IN OWN FILE NAME LOCATION
    file_name = list_nc_files('')
    target_lat = float(input("Enter target latitude: "))
    target_lon = float(input("Enter target longitude: "))
    radius_km = float(input("Enter search radius in km (e.g., 50): "))
    process_files(file_name, target_lat, target_lon, radius_km)

