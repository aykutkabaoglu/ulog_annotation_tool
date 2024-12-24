#!/usr/bin/env python3

import os
import numpy as np
import pandas as pd
from pyulog import ULog
from pyulog.px4 import PX4ULog
from typing import TypedDict, List

#TODO: Timestamp match between topics, down or upssampling
#TODO: Duration mismatch between different log files
#TODO: Remove mission mode filter or add other mode filterings
#TODO: do not add each topic and its attributes one by one and iterate over full dataset


class MissionData(TypedDict):
    dataset: str
    attr: str
    timestamp: np.ndarray[np.int32]
    values: np.ndarray[np.float32]


params = {
    "vehicle_attitude": [
        "roll",
        "pitch", 
        "yaw",
        "roll_d",
        "pitch_d",
        "yaw_d",
        "rollspeed",
        "pitchspeed",
        "yawspeed"
    ],
    "vehicle_attitude_setpoint": [
        "roll_d",
        "pitch_d",
        "yaw_d", 
        "roll_body",
        "pitch_body",
        "yaw_body",
        "q[0]",
        "q[1]",
        "q[2]",
        "q[3]"
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
        "az"
    ],
    "vehicle_local_position_setpoint": [
        "x",
        "y",
        "z", 
        "yaw",
        "vx",
        "vy",
        "vz"
    ],
    "sensor_combined": [
        "accelerometer_m_s2[0]",
        "accelerometer_m_s2[1]",
        "accelerometer_m_s2[2]",
        "baro_alt_meter",
        "gyro_rad[0]",
        "gyro_rad[1]",
        "gyro_rad[2]",
        "magnetometer_ga[0]",
        "magnetometer_ga[1]",
        "magnetometer_ga[2]",
        "alt"
    ],
    "vehicle_magnetometer": [
        "magnetometer_ga[0]",
        "magnetometer_ga[1]",
        "magnetometer_ga[2]",
    ],
    "vehicle_air_data": [
        "baro_alt_meter",
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
    #         "alt"
    #     ]
    # ],
    "actuator_controls_0": [
        "thrust",
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
        "vx",
        "vy",
        "vz",
        "roll",
        "pitch",
        "yaw",
        "latency"
    ],
    "vehicle_magnetometer": [
        "magnetometer_ga[0]",
        "magnetometer_ga[1]",
        "magnetometer_ga[2]",
    ],
    "sensor_combined": [
        "magnetometer_ga[0]",
        "magnetometer_ga[1]",
        "magnetometer_ga[2]",
    ],
    "rate_ctrl_status": [
        "rollspeed",
        "pitchspeed",
        "yawspeed"
    ],
    "battery_status": [
        "voltage_v",
        "current_a",
        "discharged_mah",
        "remaining"
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
        "vehicle_land_detected"
    ],
    "manual_control_setpoint": [
        "x",
        "y",
        "r",
        "z"
    ],
    "estimator_status": [
        "vibe[2]",
        "time_slip",
    
    ],
    "vehicle_angular_acceleration": [
        "xyz[0]",
        "xyz[1]",
        "xyz[2]"
    ],
    "input_rc": [
        "rssi",
        "rc_lost"
    ],
    "sensor_baro": [
        "temperature"
    ],
    "sensor_accel": [
        "temperature"
    ],
    "cpuload": [
        "load",
        "ram_usage"
    ],
    "ekf2_innovations": [
        "mag_innov",
        "mag_innov_var",
        "vel_innov",
        "vel_innov_var",
        "pos_innov",
        "pos_innov_var",
        "hagl_innov",
        "hagl_innov_var"
    ],
    "vehicle_gps_position": [
        "lat",
        "lon",
        "alt"
    ]
}


def extract_topics(ulog) -> List[MissionData] | str:
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

filter = [k for k in params.keys()] + ["vehicle_status"]

output_csv_dir = os.path.join(cwd, "../data/csv_files")

# make sure output csv dir exist
if not os.path.isdir(output_csv_dir):
    os.makedirs(output_csv_dir)

for i, ulog_path in enumerate(ulg_paths):
    csv_loc = os.path.join(output_csv_dir, os.path.basename(ulog_path)[:-4] + ".csv")

    # if os.path.exists(csv_loc):
    #     print(f"{i+1} | File {csv_loc} already processed, skipping...")
    #     continue

    ulog = ULog(ulog_path, filter)
    px4ulog = PX4ULog(ulog)
    px4ulog.add_roll_pitch_yaw()

    cols = extract_topics(ulog)
    if isinstance(cols, str):
        print(f"{i+1} | Skipping {ulog_path}, missing dataset {cols}")
        continue
    if min(map(lambda x: len(x["timestamp"]), cols)) < 20:
        print(f"{i+1} | Mission mode in file {csv_loc} too short, skipping...")
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
