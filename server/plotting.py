from typing import Any
import numpy as np
import pandas as pd
import itertools
from bokeh.plotting import figure
from bokeh.models import CustomJS, Model, BoxAnnotation
from bokeh.palettes import Dark2_5 as palette

#TODO: create plots according to csv files' contents and do not provide topic names and attributes

figures = [
    {
        "title": "Attitude.Pitch",
        "plots": [
            {"col": "vehicle_attitude.pitch", "label": "Pitch"},
            {"col": "vehicle_attitude_setpoint.pitch_d", "label": "Pitch Setpoint"},
            {"col": "vehicle_attitude.pitchspeed", "label": "Pitch Speed"},
            {"col": "vehicle_attitude_setpoint.pitch_body", "label": "Pitch Body"},
        ],
    },
    {
        "title": "Attitude.Roll",
        "plots": [
            {"col": "vehicle_attitude.roll", "label": "Roll"},
            {"col": "vehicle_attitude_setpoint.roll_d", "label": "Roll Setpoint"},
            {"col": "vehicle_attitude.rollspeed", "label": "Roll Speed"},
            {"col": "vehicle_attitude_setpoint.roll_body", "label": "Roll Body"},
        ],
    },
    {
        "title": "Attitude.Yaw",
        "plots": [
            {"col": "vehicle_attitude.yaw", "label": "Yaw"},
            {"col": "vehicle_attitude_setpoint.yaw_d", "label": "Yaw Setpoint"},
            {"col": "vehicle_attitude.yawspeed", "label": "Yaw Speed"},
            {"col": "vehicle_attitude_setpoint.yaw_body", "label": "Yaw Body"},
            {"col": "vehicle_local_position.yaw", "label": "Local Yaw"},
            {"col": "vehicle_local_position_setpoint.yaw", "label": "Local Setpoint Yaw"},
        ],
    },
    {
        "title": "Position.X",
        "plots": [
            {"col": "vehicle_local_position.x", "label": "X"},
            {"col": "vehicle_local_position_setpoint.x", "label": "X Setpoint"},
        ],
    },
    {
        "title": "Position.Y",
        "plots": [
            {"col": "vehicle_local_position.y", "label": "Y"},
            {"col": "vehicle_local_position_setpoint.y", "label": "Y Setpoint"},
        ],
    },
    {
        "title": "Position.Z",
        "plots": [
            {"col": "vehicle_local_position.z", "label": "Z"},
            {"col": "vehicle_local_position_setpoint.z", "label": "Z Setpoint"},
            {"col": "vehicle_air_data.baro_alt_meter", "label": "Altitude(m)"},
            {"col": "distance_sensor.current_distance", "label": "Distance Sensor"},
        ],
    },
    {
        "title": "Raw Acceleration",
        "plots": [
            {"col": "sensor_combined.accelerometer_m_s2[0]", "label": "X"},
            {"col": "sensor_combined.accelerometer_m_s2[1]", "label": "Y"},
            {"col": "sensor_combined.accelerometer_m_s2[2]", "label": "Z"},
        ],
    },
    {
        "title": "Acceleration",
        "plots": [
            {"col": "vehicle_local_position.ax", "label": "ax"},
            {"col": "vehicle_local_position.ay", "label": "ay"},
            {"col": "vehicle_local_position.az", "label": "az"},
        ],
    },
    {
        "title": "Gyroscope",
        "plots": [
            {"col": "sensor_combined.gyro_rad[0]", "label": "gx"},
            {"col": "sensor_combined.gyro_rad[1]", "label": "gy"},
            {"col": "sensor_combined.gyro_rad[2]", "label": "gz"},
        ],
    },    
    {
        "title": "Magnetometer",
        "plots": [
            {"col": "vehicle_magnetometer.magnetometer_ga[0]", "label": "X"},
            {"col": "vehicle_magnetometer.magnetometer_ga[1]", "label": "Y"},
            {"col": "vehicle_magnetometer.magnetometer_ga[2]", "label": "Z"},
        ],
    },
    {
        "title": "Magnetometer",
        "plots": [
            {"col": "sensor_combined.magnetometer_ga[0]", "label": "X"},
            {"col": "sensor_combined.magnetometer_ga[1]", "label": "Y"},
            {"col": "sensor_combined.magnetometer_ga[2]", "label": "Z"},
        ],
    },    
    {
        "title": "Velocity",
        "plots": [
            {"col": "vehicle_local_position.vx", "label": "Vx"},
            {"col": "vehicle_local_position_setpoint.vx", "label": "Vx Setpoint"},
            {"col": "vehicle_local_position.vy", "label": "Vy"},
            {"col": "vehicle_local_position_setpoint.vy", "label": "Vy Setpoint"},
            {"col": "vehicle_local_position.vz", "label": "Vz"},
            {"col": "vehicle_local_position_setpoint.vz", "label": "Vz Setpoint"},
        ],
    },
    {
        "title": "Altitude",
        "plots": [
            {"col": "vehicle_air_data.baro_alt_meter", "label": "baro_alt_meter"},
            {"col": "gps_position.alt", "label": "GPS Alt"},
            {"col": "sensor_combined.alt", "label": "Sensor Alt"},
            {"col": "vehicle_global_position.alt", "label": "Global Position Alt"},
            #{"col": "position_setpoint_triplet.current.alt", "label": "Sensor Alt"},
        ],
    },
    {
        "title": "Actuator Controls",
        "plots": [
            {"col": "actuator_controls.thrust", "label": "thrust"},
            {"col": "actuator_controls.control[0]", "label": "Ctrl 0"},
            {"col": "actuator_controls.control[1]", "label": "Ctrl 1"},
            {"col": "actuator_controls.control[2]", "label": "Ctrl 2"},
            {"col": "actuator_controls.control[3]", "label": "Ctrl 3"},
        ],
    },
    {
        "title": "Actuator Outputs",
        "plots": [
            {"col": "actuator_outputs.output[0]", "label": "Output 0"},
            {"col": "actuator_outputs.output[1]", "label": "Output 1"},
            {"col": "actuator_outputs.output[2]", "label": "Output 2"},
            {"col": "actuator_outputs.output[3]", "label": "Output 3"},
            {"col": "actuator_outputs.output[4]", "label": "Output 4"},
            {"col": "actuator_outputs.output[5]", "label": "Output 5"},
            {"col": "actuator_outputs.output[6]", "label": "Output 6"},
            {"col": "actuator_outputs.output[7]", "label": "Output 7"},
        ],
    },    
]


def plot_df(df: pd.DataFrame, models: Model = None, highlight: bool = True):
    alpha = 0.7
    colors = itertools.cycle(palette)

    for i, f in enumerate(figures):
        if not models:
            f["model"] = figure(width=1000, height=500, title=f["title"])
        else:
            f["model"] = models[i]
        for p in f["plots"]:
            try:
                y = df[p["col"]]
                x = np.arange(y.shape[0])
                f["model"].line(
                    x,
                    y,
                    color=next(colors),
                    legend_label=p["label"],
                    line_width=2,
                    alpha=alpha,
                )
            except:
                print("Couldn't find", p["col"])
        if not models:
            f["model"].legend.click_policy = "hide"
            if highlight:
                enable_highlight(f["model"], figname=f["title"])

    return [f["model"] for f in figures]


def enable_highlight(fig: Model, figname: str):
    # JavaScript to manage the box drawing
    callback = CustomJS(
        args=dict(fig=fig, figname=figname),
        code="""
        const tools = fig.toolbar.tools
        const activeTool = tools.find(tool => tool.active)
        if (activeTool) return

        if (!window.boxes) {
            window.boxes = []
        }

        if (cb_obj.event_name === 'panstart') {
            // Create a new BoxAnnotation
            const BoxAnnotation = Bokeh.Models._known_models.get('BoxAnnotation')
            const box = new BoxAnnotation({
                left: cb_obj.x, right: cb_obj.x,
                fill_alpha: 0.5, fill_color: 'green'
            })

            // Add this annotation to the plot
            fig.add_layout(box)
            window.boxes.push({ fig: fig, name: figname, box })
        } else if (cb_obj.event_name === 'pan') {
            const box = window.boxes.at(-1).box
            if (!box) return
            box.right = cb_obj.x
        }
    """,
    )

    fig.toolbar.active_drag = None
    fig.js_on_event("panstart", callback)
    fig.js_on_event("pan", callback)
    fig.js_on_event("panend", callback)


def annotate_plot(df: pd.DataFrame, models: Any):
    anomaly_cols = ["anomaly." + f["title"] for f in figures]
    for i, anomaly_col in enumerate(anomaly_cols):
        if df.get(anomaly_col) is None:
            continue
        arr = df[anomaly_col].to_numpy()
        diff = np.diff(arr.astype(int))
        start = (np.where(diff == 1)[0] + 1).tolist()
        end = (np.where(diff == -1)[0] + 1).tolist()
        if arr[0] == 1:
            start = [0] + start  # start with True
        if arr[-1] == 1:
            end = end + [len(arr)]  # ends with True
        for left, right in zip(start, end):
            box = BoxAnnotation(
                left=left, right=right - 1, fill_alpha=0.5, fill_color="green"
            )
            models[i].add_layout(box)


def add_annotation(df: pd.DataFrame, data: Any):
    anomaly = np.zeros(df.shape[0], dtype=bool)
    for name, ranges in data:
        sub_anomaly = np.zeros(df.shape[0], dtype=bool)
        for xmin, xmax in ranges:
            xmin = max(0, xmin)
            xmax = min(xmax, df.shape[0] - 1)
            sub_anomaly[xmin : xmax + 1] = True
            anomaly[xmin : xmax + 1] = True
        df["anomaly." + name] = sub_anomaly
    df["anomaly"] = anomaly
