from typing import Any
import numpy as np
import pandas as pd
import itertools
from bokeh.plotting import figure
from bokeh.models import CustomJS, Model, BoxAnnotation, Label
from bokeh.palettes import Dark2_5 as palette
from css import apply_plot_theme

figures = [
    {
        "title": "Position.X",
        "plots": [
            {"col": "vehicle_local_position.x", "label": "X"},
            {"col": "vehicle_local_position_setpoint.x", "label": "X Setpoint"},
            {"col": "vehicle_visual_odometry.x", "label": "VO X"},
        ],
    },
    {
        "title": "Actuator Pitch",
        "plots": [
            {"col": "actuator_controls_0.control[1]", "label": "Actuator Pitch"},
        ],
    },
    {
        "title": "Position.Y",
        "plots": [
            {"col": "vehicle_local_position.y", "label": "Y"},
            {"col": "vehicle_local_position_setpoint.y", "label": "Y Setpoint"},
            {"col": "vehicle_visual_odometry.y", "label": "VO Y"},
        ],
    },
    {
        "title": "Actuator Roll",
        "plots": [
            {"col": "actuator_controls_0.control[0]", "label": "Actuator Roll"},
        ],
    },
    {
        "title": "Position.Z",
        "plots": [
            {"col": "vehicle_local_position.z", "label": "Z"}, # invert the data
            {"col": "vehicle_local_position_setpoint.z", "label": "Z Setpoint"}, # invert the data
            {"col": "vehicle_air_data.baro_alt_meter", "label": "Altitude(m)"},
            {"col": "distance_sensor.current_distance", "label": "Distance Sensor"},
            {"col": "vehicle_visual_odometry.z", "label": "VO Z"},
            {"col": "gps_position.alt", "label": "GPS Alt"},
            {"col": "sensor_combined.alt", "label": "Sensor Alt"},
            {"col": "vehicle_global_position.alt", "label": "Global Position Alt"},
        ],
    },
    {
        "title": "Actuator Thrust",
        "plots": [
            {"col": "actuator_controls_0.control[3]", "label": "Actuator Thrust"},
        ],
    },
    {
        "title": "Global Position",
        "plots": [
            {"col": "vehicle_global_position.lat", "label": "Latitude"},
            {"col": "vehicle_global_position.lon", "label": "Longitude"},
            {"col": "vehicle_global_position.alt", "label": "Altitude"},
            {"col": "vehicle_gps_position.lat", "label": "GPS Latitude"},
            {"col": "vehicle_gps_position.lon", "label": "GPS Longitude"},
            {"col": "vehicle_gps_position.alt", "label": "GPS Altitude"},   
        ],
    },
    {
        "title": "Attitude.Roll",
        "plots": [
            {"col": "actuator_controls_0.control[0]", "label": "Actuator Roll"},
            {"col": "vehicle_attitude.q[0]", "label": "q[0]"}, # convert to roll
            {"col": "vehicle_attitude_setpoint.q_d[0]", "label": "q_d[0]"},
        ],
    },
    {
        "title": "Attitude.Pitch",
        "plots": [
            {"col": "actuator_controls_0.control[1]", "label": "Actuator Pitch"},
            {"col": "vehicle_attitude.q[0]", "label": "q[0]"}, # convert to pitch
            {"col": "vehicle_attitude_setpoint.q_d[0]", "label": "q_d[0]"},
        ],
    },
    {
        "title": "Attitude.Yaw",
        "plots": [
            {"col": "vehicle_local_position.yaw", "label": "Local Yaw"},
            {"col": "vehicle_local_position_setpoint.yaw", "label": "Local Setpoint Yaw"},
            {"col": "actuator_controls_0.control[2]", "label": "Actuator Yaw"},
        ],
    },
    {
        "title": "Roll Rate",
        "plots": [
            {"col": "vehicle_rates_setpoint.roll", "label": "Roll Rate Setpoint"},
            {"col": "actuator_controls_0.control[0]", "label": "Actuator Roll"},
            {"col": "rate_ctrl_status.rollspeed_integ", "label": "Roll Speed Integral"},
        ],
    },
    {
        "title": "Pitch Rate",
        "plots": [
            {"col": "vehicle_rates_setpoint.pitch", "label": "Pitch Rate Setpoint"},
            {"col": "actuator_controls_0.control[1]", "label": "Actuator Pitch"},
            {"col": "rate_ctrl_status.pitchspeed_integ", "label": "Pitch Speed Integral"},
        ],
    },
    {
        "title": "Yaw Rate",
        "plots": [
            {"col": "vehicle_rates_setpoint.yaw", "label": "Yaw Rate Setpoint"},
            {"col": "actuator_controls_0.control[2]", "label": "Actuator Yaw"},
            {"col": "rate_ctrl_status.yawspeed_integ", "label": "Yaw Speed Integral"},
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
        "title": "Vehicle Angular Velocity",
        "plots": [
            {"col": "vehicle_angular_velocity.xyz[0]", "label": "X"},
            {"col": "vehicle_angular_velocity.xyz[1]", "label": "Y"},
            {"col": "vehicle_angular_velocity.xyz[2]", "label": "Z"},
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
            {"col": "battery_status.current_a", "label": "Current"},
            {"col": "actuator_controls_0.control[3]", "label": "Thrust"},
        ],
    },
    {
        "title": "Actuator Controls",
        "plots": [
            {"col": "actuator_controls_0.control[0]", "label": "Roll"},
            {"col": "actuator_controls_0.control[1]", "label": "Pitch"},
            {"col": "actuator_controls_0.control[2]", "label": "Yaw"},
            {"col": "actuator_controls_0.control[3]", "label": "Thrust"},
        ],
    },
    {
        "title": "Actuator Outputs",
        "plots": [
            {"col": "actuator_outputs.output[0]", "label": "Output 0"},
            {"col": "actuator_outputs.output[1]", "label": "Output 1"},
            {"col": "actuator_outputs.output[2]", "label": "Output 2"},
            {"col": "actuator_outputs.output[3]", "label": "Output 3"},
        ],
    },
    {
        "title": "Manual Control",
        "plots": [
            {"col": "manual_control_setpoint.x", "label": "Manual Roll"},
            {"col": "manual_control_setpoint.y", "label": "Manual Pitch"},
            {"col": "manual_control_setpoint.r", "label": "Manual Yaw"},
            {"col": "manual_control_setpoint.z", "label": "Manual Throttle"},
            {"col": "manual_control_setpoint.kill_switch", "label": "Kill Switch"},
        ],
    },
    {
        "title": "Vibration",
        "plots": [
            {"col": "estimator_status.vibe[0]", "label": "Vibration X"},
            {"col": "estimator_status.vibe[1]", "label": "Vibration Y"},
            {"col": "estimator_status.vibe[2]", "label": "Vibration Z"},
        ],
    },
    {
        "title": "Battery",
        "plots": [
            {"col": "battery_status.voltage_v", "label": "Voltage"},
            {"col": "battery_status.current_a", "label": "Current"},
            {"col": "battery_status.remaining", "label": "Remaining"},
        ],
    },
]

def quaternion_to_euler(q0, q1, q2, q3):
    """Convert quaternion to Euler angles (roll, pitch, yaw)"""
    # Roll (x-axis rotation)
    sinr_cosp = 2 * (q0 * q1 + q2 * q3)
    cosr_cosp = 1 - 2 * (q1 * q1 + q2 * q2)
    roll = np.arctan2(sinr_cosp, cosr_cosp)

    # Pitch (y-axis rotation)
    sinp = 2 * (q0 * q2 - q3 * q1)
    pitch = np.where(abs(sinp) >= 1,
                    np.sign(sinp) * np.pi / 2,
                    np.arcsin(sinp))

    # Yaw (z-axis rotation)
    siny_cosp = 2 * (q0 * q3 + q1 * q2)
    cosy_cosp = 1 - 2 * (q2 * q2 + q3 * q3)
    yaw = np.arctan2(siny_cosp, cosy_cosp)

    return roll, pitch, yaw
    

def check_quaternion_plot(df, columns):
    if "vehicle_attitude.q[" in columns:
        q0 = df["vehicle_attitude.q[0]"]
        q1 = df["vehicle_attitude.q[1]"]
        q2 = df["vehicle_attitude.q[2]"]
        q3 = df["vehicle_attitude.q[3]"]
        label = ""

    elif "vehicle_attitude_setpoint.q_d[" in columns:
        q0 = df["vehicle_attitude_setpoint.q_d[0]"]
        q1 = df["vehicle_attitude_setpoint.q_d[1]"]
        q2 = df["vehicle_attitude_setpoint.q_d[2]"]
        q3 = df["vehicle_attitude_setpoint.q_d[3]"]
        label = "Setpoint"

    roll, pitch, yaw = quaternion_to_euler(q0, q1, q2, q3)
    
    return roll, pitch, yaw, label

# Plot the dataframe with the given models, highlight the anomalies and return the models
def plot_df(df: pd.DataFrame, mapping: dict = None, file_name: str = None):
    alpha = 0.7
    colors = itertools.cycle(palette)

    # Check if we have annotations for this file in mapping
    if mapping and file_name and file_name[:-4] in mapping:
        file_annotations = mapping[file_name[:-4]]["annotations"]
    else:
        file_annotations = []

    for i, f in enumerate(figures):
        f["model"] = figure(
            width=1000, 
            height=500, 
            title=f["title"]
        )
        
        for p in f["plots"]:
            try:
                # Normal plotting for non-quaternion data
                y = df[p["col"]]
                x = df['timestamp']

                # Check if this is a quaternion plot
                if f["title"] == "Attitude.Roll":
                    y, _, _, label = check_quaternion_plot(df, p["col"])
                    label = "Roll " + label
                elif f["title"] == "Attitude.Pitch":
                    _, y, _, label = check_quaternion_plot(df, p["col"])
                    label = "Pitch " + label
                else:
                    label = p["label"]

                f["model"].line(
                    x, y,
                    color=next(colors),
                    legend_label=label,
                    line_width=2,
                    alpha=alpha
                )
            except Exception as e:
                #print("Couldn't find", p["col"])
                pass
                
        box_and_labels = get_annotation_box_and_label(file_annotations, f["title"])
        for box, label in box_and_labels:
            f["model"].add_layout(box)
            f["model"].add_layout(label)

        # Apply theme
        apply_plot_theme(f["model"])
        enable_highlight(f["model"], figname=f["title"])

    return [f["model"] for f in figures]

def get_annotation_box_and_label(file_annotations, plot_title):
    box_and_labels = []
    for annotation in file_annotations:
        # Get the class and ranges for this annotation
        anomaly_class = annotation["class"]
        ranges = annotation["ranges"]
        # Find ranges that match this plot's column
        for col, col_ranges in ranges:
            if col == plot_title:
                # Create box annotations for each range
                for start, end in col_ranges:
                    box = BoxAnnotation(
                        left=start,
                        right=end,
                        fill_alpha=0.2,
                        fill_color='red',
                        level='overlay'
                    )

                    # Add label at the top of the box
                    label = Label(
                        x= (start+end)/2,
                        y= 0,  # Position at bottom instead of top
                        text=anomaly_class,
                        text_color='white',  # White text
                        text_font_size='12pt',  # Larger font
                        text_font_style='bold',
                        background_fill_color='rgba(0,0,0,0.7)',  # Semi-transparent black background
                        background_fill_alpha=0.7,
                        text_align='center',
                        border_line_color='green',  # White border
                        border_line_alpha=0.7,
                    )
                    box_and_labels.append((box, label))
    return box_and_labels


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
