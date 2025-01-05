#!/usr/bin/env python3

import os
import numpy as np
import pandas as pd
from pyulog import ULog
from pyulog.px4 import PX4ULog
from typing import TypedDict, List
import argparse


class MissionData(TypedDict):
    dataset: str
    attr: str
    timestamp: np.ndarray[np.int32]
    values: np.ndarray[np.float32]


def get_all_topics(ulog) -> dict:
    params = {}
    for dataset_name in ulog.data_list:
        # Get all field names except 'timestamp' which we handle separately
        fields = [field.field_name for field in dataset_name.field_data if field.field_name != 'timestamp']
        params[dataset_name.name] = fields
    return params

def get_custom_topics() -> dict:
    return {
        "vehicle_attitude": [
            "roll",
            "pitch",
            "yaw",
            "q[0]",
            "q[1]",
            "q[2]",
            "q[3]"
        ],
        "vehicle_attitude_setpoint": [
            "roll_d",
            "pitch_d",
            "yaw_d",
            "roll_body",
            "pitch_body",
            "yaw_body",
        ],
        "vehicle_local_position": [
            "x",
            "y",
            "z",
            "yaw",
            "vx",
            "vy",
            "vz",
            "ax",
            "ay",
            "az",
            "delta_xy[0]",
            "delta_xy[1]",
            "delta_z",
            "eph",
            "epv",
            "evv"            
        ],
        "vehicle_local_position_setpoint": [
            "x",
            "y",
            "z",
            "yaw",
            "vx",
            "vy",
            "vz",
            "thrust[0]",
            "thrust[1]",
            "thrust[2]",
        ],
        "sensor_combined": [
            "accelerometer_m_s2[0]",
            "accelerometer_m_s2[1]",
            "accelerometer_m_s2[2]",
            "gyro_rad[0]",
            "gyro_rad[1]",
            "gyro_rad[2]",
        ],
        "vehicle_magnetometer": [
            "magnetometer_ga[0]",
            "magnetometer_ga[1]",
            "magnetometer_ga[2]",
        ],
        "vehicle_air_data": [
            "baro_alt_meter", # normalize the data
            "baro_temp_celcius",
            "baro_pressure_pa",
            "rho"
        ],
        "gps_position": [
            "alt",
            "eph",
            "epv",
            "satellites_used",
            "fix_type",
            "noise_per_ms",
            "jamming_indicator"
        ],
        "vehicle_global_position": [
            "alt",
            "lat",
            "lon"
        ],
        # "position_setpoint_triplet": [
        #     "current": [
        #         "x",
        #         "y",
        #         "z",
        #         "yaw"
        #     ]
        # ],
        "actuator_controls_0": [
            "control[0]",
            "control[1]",
            "control[2]",
            "control[3]"
        ],
        "distance_sensor": [
            "current_distance"
        ],
        "actuator_outputs": [
            "output[0]",
            "output[1]",
            "output[2]",
            "output[3]",
            "output[4]",
            "output[5]",
            "output[6]",
            "output[7]"
        ],
        "trajectory_setpoint": [
            "x",
            "y",
            "z",
            "yaw"
        ],
        "vehicle_visual_odometry": [
            "x",
            "y",
            "z",
            "q[0]",
            "q[1]",
            "q[2]",
            "q[3]",
            "vx",
            "vy",
            "vz",
        ],
        "rate_ctrl_status": [
            "rollspeed_integ",
            "pitchspeed_integ",
            "yawspeed_integ"
        ],
        "battery_status": [
            "voltage_v",
            "voltage_filtered_v",
            "current_a",
            "current_filtered_a",
            "discharged_mah",
            "remaining",
            "scale",
            "connected"
        ],
        "vehicle_rates_setpoint": [
            "roll",
            "pitch",
            "yaw"
        ],
        "vehicle_angular_velocity": [
            "xyz[0]",
            "xyz[1]",
            "xyz[2]"
        ],
        "vehicle_status": [
            "arming_state",
            "vehicle_type",
            "nav_state",
            "failsafe",
            "rc_signal_lost",
            "data_link_lost",
            "engine_failure",
            "mission_failure",
        ],
        "manual_control_setpoint": [
            "x",
            "y",
            "r",
            "z"
        ],
        "estimator_status": [
            "vibe[0]",
            "vibe[1]",
            "vibe[2]",
        ],
        "input_rc": [
            "rssi",
            "rc_lost"
        ],
        "cpuload": [
            "load",
            "ram_usage"
        ],
        # "ekf2_innovations": [
        #     "hagl_innov",
        #     "hagl_innov_var"
        # ],
        "system_power": [
            "voltage5v_v",
            "voltage3v3_v"
        ],
        "telemetry_status": [
            "rate_rx",
            "rate_tx"
        ],
        "vehicle_land_detected": [
            "ground_contact",
            "maybe_landed",
            "landed",
            "in_ground_effect"
        ]
    }


def extract_topics(ulog) -> List[MissionData] | str:
    # Get all topics and their attributes
    params = get_all_topics(ulog)
    #params = get_custom_topics()
    # create each column for the given attributes in params
    cols = []
    for dataset, attrs in params.items():
        try:
            data = ulog.get_dataset(dataset).data
        except (KeyError, IndexError, ValueError) as error:
            print("Error:", error, "Dataset:", dataset)
            continue
        for attr in attrs:
            values = data.get(attr)
            timestamp = data["timestamp"]

            if values is not None:    
                cols.append(
                    {
                        "dataset": dataset,
                        "attr": attr,
                        "timestamp": timestamp,
                        "values": values,
                    }
                )
            else:
                print(f"{attr} not found in {dataset}")

    return cols

def subsample(col1, col2):
    # Linear interpolation between points
    col1["values"] = np.interp(col2["timestamp"], col1["timestamp"], col1["values"])
    col1["timestamp"] = col2["timestamp"]


def upsample(col1, col2):
    # Linear interpolation to upsample
    col2["values"] = np.interp(col1["timestamp"], col2["timestamp"], col2["values"])
    col2["timestamp"] = col1["timestamp"]


def synchronize_timeseries(cols: List[MissionData], reference_index) -> None:
    # down sample or upsample according to the size of given topic index as aligning_index
    for col in cols:
        if len(col["timestamp"]) > len(cols[reference_index]["timestamp"]):
            subsample(col, cols[reference_index])
        else:
            upsample(cols[reference_index], col)


def cols_to_df(cols: List[MissionData]) -> pd.DataFrame:
    return pd.DataFrame(
        np.vstack([cols[0]["timestamp"]] + [col["values"] for col in cols]).T,
        columns=["timestamp"] + [f'{col["dataset"]}.{col["attr"]}' for col in cols],
    )


# change to current file's dir
os.chdir(os.path.dirname(os.path.abspath(__file__)))

cwd = os.path.dirname(os.path.abspath(__file__))
ulg_dir = os.path.join(cwd, "../data/ulg_files")
ulg_paths = [
    os.path.join(ulg_dir, ulg_file_name) for ulg_file_name in os.listdir(ulg_dir)
]

output_csv_dir = os.path.join(cwd, "../data/csv_files")

# make sure output csv dir exist
if not os.path.isdir(output_csv_dir):
    os.makedirs(output_csv_dir)

parser = argparse.ArgumentParser(description='Convert ULog files to CSV format')
parser.add_argument('--skip-processed', action='store_false', default=False, 
                   help='Skip files that have already been processed')
args = parser.parse_args()
skip_processed = args.skip_processed

for i, ulog_path in enumerate(ulg_paths):
    csv_loc = os.path.join(output_csv_dir, os.path.basename(ulog_path)[:-4] + ".csv")

    # do not process files that have already been processed if --skip-processed is set
    if skip_processed:
        if os.path.exists(csv_loc):
            print(f"{i+1} | File {csv_loc} already processed, skipping...")
            continue


    ulog = ULog(ulog_path)
    px4ulog = PX4ULog(ulog)
    px4ulog.add_roll_pitch_yaw()

    cols = extract_topics(ulog)
    if isinstance(cols, str):
        print(f"{i+1} | Skipping {ulog_path}, missing dataset {cols}")
        continue

    # Convert lengths of time to numpy array
    timestamps_len = np.array([len(col["timestamp"]) for col in cols])
    
    # Find longest (highest frequency) series
    longest_idx = np.argmax(timestamps_len)
    longest_len = timestamps_len[longest_idx]
    
    # Find shortest (lowest frequency) series
    shortest_idx = np.argmin(timestamps_len)
    shortest_len = timestamps_len[shortest_idx]
    
    # Statistical measures
    mean_len = np.mean(timestamps_len)
    median_len = np.median(timestamps_len)
    
    # Find the column closest to the median
    centroid_idx = np.argmin(np.abs(timestamps_len - median_len))

    # down or upsample data with the size of alignment column and 
    # change timestamps with the timestamp of the alignment column
    synchronize_timeseries(cols, centroid_idx)
    df = cols_to_df(cols)

    # save to csv
    if df.shape[0] < 100:
        print(f"{i+1} | Mission mode in file {csv_loc} too short, skipping...")
        continue
    print(f"{i+1} | Converting {ulog_path} to csv")
    df.to_csv(csv_loc, index=False)
