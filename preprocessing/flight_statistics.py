import os
import json
import pandas as pd
import numpy as np
from datetime import datetime

# Paths
csv_dir = 'data/csv_files'
mapping_file = 'data/mapping.json'

total_duration = 0
vision_position_duration = 0 
global_position_duration = 0
gps_position_duration = 0
vision_odometry_duration = 0

# Initialize additional counters for annotated files
annotated_total_duration = 0
annotated_vision_position_duration = 0 
annotated_global_position_duration = 0
annotated_gps_position_duration = 0
annotated_vision_odometry_duration = 0

# Convert durations to hours, minutes, seconds format
def format_duration(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours}h {minutes}m {seconds}s"

# Load mapping file to identify annotated files
with open(mapping_file, 'r') as f:
    mapping_data = json.load(f)

# Get list of annotated files
annotated_files = set(mapping_data.keys())

# Process each CSV file recursively through all subdirectories
for root, _, files in os.walk(csv_dir):
    for filename in files:
        if filename.endswith('.csv'):
            filepath = os.path.join(root, filename)
            # Get path relative to csv_dir
            rel_path = os.path.relpath(root, csv_dir)
            if rel_path == '.':
                rel_file = filename
            else:
                rel_file = os.path.join(rel_path, filename)

            try:
                df = pd.read_csv(filepath)
                
                # Get flight duration from timestamps
                start_time = df.iloc[0]['timestamp'] 
                end_time = df.iloc[-1]['timestamp']
                duration = (end_time - start_time) / 1e6  # Convert microseconds to seconds

                # Check if file is annotated
                is_annotated = rel_file[:-4] in annotated_files
                
                # Update appropriate counters
                if is_annotated:
                    annotated_total_duration += duration
                total_duration += duration

                # Check for global position data
                global_pos_columns = [col for col in df.columns if 'vehicle_global_position' in col]
                if global_pos_columns:
                    if not df[global_pos_columns].isna().all().all() and not (df[global_pos_columns] == 0).all().all():
                        if is_annotated:
                            annotated_global_position_duration += duration
                        global_position_duration += duration

                # Check for gps position data
                gps_pos_columns = [col for col in df.columns if 'vehicle_gps_position' in col]
                if gps_pos_columns:
                    if not df[gps_pos_columns].isna().all().all() and not (df[gps_pos_columns] == 0).all().all():
                        if is_annotated:
                            annotated_gps_position_duration += duration
                        gps_position_duration += duration

                # Check for vision position data
                vision_pos_columns = [col for col in df.columns if 'vehicle_vision_position' in col]
                if vision_pos_columns:
                    if not df[vision_pos_columns].isna().all().all() and not (df[vision_pos_columns] == 0).all().all():
                        if is_annotated:
                            annotated_vision_position_duration += duration
                        vision_position_duration += duration

                # Check for vision odometry data
                vision_odometry_columns = [col for col in df.columns if 'vehicle_visual_odometry' in col]
                if vision_odometry_columns:
                    if not df[vision_odometry_columns].isna().all().all() and not (df[vision_odometry_columns] == 0).all().all():
                        if is_annotated:
                            annotated_vision_odometry_duration += duration
                        vision_odometry_duration += duration

            except Exception as e:
                print(f"Error processing {filepath}: {e}")



print(f"Total flight duration: {format_duration(total_duration)} ({total_duration:.2f} seconds)")
print(f"Vision position duration: {format_duration(vision_position_duration)} ({vision_position_duration:.2f} seconds)")
print(f"Global position duration: {format_duration(global_position_duration)} ({global_position_duration:.2f} seconds)")
print(f"GPS position duration: {format_duration(gps_position_duration)} ({gps_position_duration:.2f} seconds)")
print(f"Vision odometry duration: {format_duration(vision_odometry_duration)} ({vision_odometry_duration:.2f} seconds)")

# Print annotated statistics
print("\nAnnotated Files Statistics:")
print(f"Annotated flight duration: {format_duration(annotated_total_duration)} ({annotated_total_duration:.2f} seconds)")
print(f"Annotated vision position duration: {format_duration(annotated_vision_position_duration)} ({annotated_vision_position_duration:.2f} seconds)")
print(f"Annotated global position duration: {format_duration(annotated_global_position_duration)} ({annotated_global_position_duration:.2f} seconds)")
print(f"Annotated gps position duration: {format_duration(annotated_gps_position_duration)} ({annotated_gps_position_duration:.2f} seconds)")
print(f"Annotated vision odometry duration: {format_duration(annotated_vision_odometry_duration)} ({annotated_vision_odometry_duration:.2f} seconds)")

# Calculate annotation durations from mapping.json timestamps
print("\nAnnotation Timestamps Statistics (from mapping.json):")
annotation_class_durations = {}

# Process annotations from mapping.json
for file_path, file_data in mapping_data.items():
    for annotation in file_data.get('annotations', []):
        annotation_class = annotation['class']
        if annotation_class not in annotation_class_durations:
            annotation_class_durations[annotation_class] = 0
            
        # Sum up all ranges for this annotation
        for _, ranges in annotation['ranges']:
            for start, end in ranges:
                duration = (end - start) / 1e6  # Convert microseconds to seconds
                annotation_class_durations[annotation_class] += duration

# Print annotation statistics from mapping.json timestamps
total_annotated_time = sum(annotation_class_durations.values())
print(f"\nTotal time covered by annotations: {format_duration(total_annotated_time)} ({total_annotated_time:.2f} seconds)")
print("\nBy annotation class:")
for class_name, duration in sorted(annotation_class_durations.items()):
    print(f"{class_name}: {format_duration(duration)} ({duration:.2f} seconds)")
    print(f"Percentage of total flight time: {(duration/annotated_total_duration)*100:.2f}%")
