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
    {
        "title": "RPY Rate",
        "plots": [
            {"col": "vehicle_rates_setpoint.roll", "label": "Roll Rate Setpoint"},
            {"col": "vehicle_rates_setpoint.pitch", "label": "Pitch Rate Setpoint"},
            {"col": "vehicle_rates_setpoint.yaw", "label": "Yaw Rate Setpoint"},
            {"col": "rate_ctrl_status.rollspeed_integ", "label": "Roll Speed Integ"},
            {"col": "rate_ctrl_status.pitchspeed_integ", "label": "Pitch Speed Integ"}, 
            {"col": "rate_ctrl_status.yawspeed_integ", "label": "Yaw Speed Integ"},
        ],
    },
    {
        "title": "Vibration",
        "plots": [
            {"col": "estimator_status.vibe", "label": "Vibration"},
        ],
    },
    {
        "title": "Manual Control",
        "plots": [
            {"col": "manual_control_setpoint.roll", "label": "Manual Roll"},
            {"col": "manual_control_setpoint.pitch", "label": "Manual Pitch"},
            {"col": "manual_control_setpoint.yaw", "label": "Manual Yaw"},
            {"col": "manual_control_setpoint.throttle", "label": "Manual Throttle"},
        ],
    },
    {
        "title": "Battery",
        "plots": [
            {"col": "battery_status.voltage_v", "label": "Voltage"},
            {"col": "battery_status.current_a", "label": "Current"},
            {"col": "battery_status.remaining", "label": "Remaining"},
            {"col": "battery_status.temperature", "label": "Temperature"},
        ],
    },
    {
        "title": "Visual Odometry Position",
        "plots": [
            {"col": "vehicle_visual_odometry.x", "label": "X"},
            {"col": "vehicle_visual_odometry.y", "label": "Y"},
            {"col": "vehicle_visual_odometry.z", "label": "Z"},
        ],
    },
    {
        "title": "Visual Odometry Velocity",
        "plots": [
            {"col": "vehicle_visual_odometry.vx", "label": "Vx"},
            {"col": "vehicle_visual_odometry.vy", "label": "Vy"},
            {"col": "vehicle_visual_odometry.vz", "label": "Vz"},
        ],
    },
    {
        "title": "Visual Odometry Orientation",
        "plots": [
            {"col": "vehicle_visual_odometry.roll", "label": "Roll"},
            {"col": "vehicle_visual_odometry.pitch", "label": "Pitch"},
            {"col": "vehicle_visual_odometry.yaw", "label": "Yaw"},
        ],
    },
    {
        "title": "Vehicle Angular Velocity",
        "plots": [
            {"col": "vehicle_angular_velocity.x", "label": "X"},
            {"col": "vehicle_angular_velocity.y", "label": "Y"},
            {"col": "vehicle_angular_velocity.z", "label": "Z"},
        ],
    },
    {
        "title": "Trajectory Setpoint",
        "plots": [
            {"col": "trajectory_setpoint.x", "label": "X"},
            {"col": "trajectory_setpoint.y", "label": "Y"},
            {"col": "trajectory_setpoint.z", "label": "Z"},
            {"col": "trajectory_setpoint.yaw", "label": "Yaw"},
        ],
    }
]

# Plot the dataframe with the given models, highlight the anomalies and return the models
def plot_df(df: pd.DataFrame, mapping: dict = None, file_name: str = None):
    alpha = 0.7
    colors = itertools.cycle(palette)

    for i, f in enumerate(figures):
        f["model"] = figure(
            width=1000, 
            height=500, 
            title=f["title"]
        )
        # Apply theme
        apply_plot_theme(f["model"])
        
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
                # Check if we have annotations for this file in mapping
                if mapping and file_name and file_name[:-4] in mapping:
                    file_annotations = mapping[file_name[:-4]]["annotations"]

                    box, label = get_annotation_box_and_label(file_annotations, f["title"])
                    f["model"].add_layout(box)
                    f["model"].add_layout(label)
            except Exception as e:
                #print("Couldn't find", p["col"])
                pass

        enable_highlight(f["model"], figname=f["title"])

    return [f["model"] for f in figures]

def get_annotation_box_and_label(file_annotations, plot_title):
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
    return box, label


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
