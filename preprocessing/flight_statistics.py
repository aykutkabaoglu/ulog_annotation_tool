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
distance_sensor_duration = 0
baro_alt_duration = 0

# Initialize additional counters for annotated files
annotated_total_duration = 0
annotated_vision_position_duration = 0 
annotated_global_position_duration = 0
annotated_gps_position_duration = 0
annotated_vision_odometry_duration = 0
annotated_distance_sensor_duration = 0
annotated_baro_alt_duration = 0

# Initialize overlap counters
global_gps_overlap_duration = 0
vision_odometry_overlap_duration = 0

# Initialize annotated overlap counters
annotated_global_gps_overlap_duration = 0
annotated_vision_odometry_overlap_duration = 0

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

                # Check for distance sensor data
                distance_sensor_columns = [col for col in df.columns if 'distance_sensor' in col]
                if distance_sensor_columns:
                    if not df[distance_sensor_columns].isna().all().all() and not (df[distance_sensor_columns] == 0).all().all():
                        if is_annotated:
                            annotated_distance_sensor_duration += duration
                        distance_sensor_duration += duration

                # Check for barometer altitude data
                baro_alt_columns = [col for col in df.columns if 'vehicle_air_data.baro_alt_meter' in col]
                if baro_alt_columns:
                    if not df[baro_alt_columns].isna().all().all() and not (df[baro_alt_columns] == 0).all().all():
                        if is_annotated:
                            annotated_baro_alt_duration += duration
                        baro_alt_duration += duration

                # --- Overlap statistics ---
                # Global+GPS overlap
                if global_pos_columns and gps_pos_columns:
                    global_gps_overlap_duration += duration
                    if is_annotated:
                        annotated_global_gps_overlap_duration += duration

                # Vision+Odometry overlap
                if vision_pos_columns and vision_odometry_columns:
                    vision_odometry_overlap_duration += duration
                    if is_annotated:
                        annotated_vision_odometry_overlap_duration += duration

            except Exception as e:
                print(f"Error processing {filepath}: {e}")



print(f"Total flight duration: {format_duration(total_duration)} ({total_duration:.2f} seconds)")
print(f"Vision position duration: {format_duration(vision_position_duration)} ({vision_position_duration:.2f} seconds)")
print(f"Global position duration: {format_duration(global_position_duration)} ({global_position_duration:.2f} seconds)")
print(f"GPS position duration: {format_duration(gps_position_duration)} ({gps_position_duration:.2f} seconds)")
print(f"Vision odometry duration: {format_duration(vision_odometry_duration)} ({vision_odometry_duration:.2f} seconds)")
print(f"Distance sensor duration: {format_duration(distance_sensor_duration)} ({distance_sensor_duration:.2f} seconds)")
print(f"Barometer altitude duration: {format_duration(baro_alt_duration)} ({baro_alt_duration:.2f} seconds)")

# Print overlap statistics
print(f"\nGlobal+GPS overlap duration: {format_duration(global_gps_overlap_duration)} ({global_gps_overlap_duration:.2f} seconds)")
print(f"Vision+Odometry overlap duration: {format_duration(vision_odometry_overlap_duration)} ({vision_odometry_overlap_duration:.2f} seconds)")

# Print annotated statistics
print("\nAnnotated Files Statistics:")
print(f"Annotated flight duration: {format_duration(annotated_total_duration)} ({annotated_total_duration:.2f} seconds)")
print(f"Annotated vision position duration: {format_duration(annotated_vision_position_duration)} ({annotated_vision_position_duration:.2f} seconds)")
print(f"Annotated global position duration: {format_duration(annotated_global_position_duration)} ({annotated_global_position_duration:.2f} seconds)")
print(f"Annotated gps position duration: {format_duration(annotated_gps_position_duration)} ({annotated_gps_position_duration:.2f} seconds)")
print(f"Annotated vision odometry duration: {format_duration(annotated_vision_odometry_duration)} ({annotated_vision_odometry_duration:.2f} seconds)")
print(f"Annotated distance sensor duration: {format_duration(annotated_distance_sensor_duration)} ({annotated_distance_sensor_duration:.2f} seconds)")
print(f"Annotated barometer altitude duration: {format_duration(annotated_baro_alt_duration)} ({annotated_baro_alt_duration:.2f} seconds)")

# Print annotated overlap statistics
print(f"\nAnnotated Global+GPS overlap duration: {format_duration(annotated_global_gps_overlap_duration)} ({annotated_global_gps_overlap_duration:.2f} seconds)")
print(f"Annotated Vision+Odometry overlap duration: {format_duration(annotated_vision_odometry_overlap_duration)} ({annotated_vision_odometry_overlap_duration:.2f} seconds)")

# Calculate annotation durations from mapping.json timestamps
print("\nAnnotation Timestamps Statistics (from mapping.json):")
annotation_class_durations = {}
annotation_class_full_duration = {}

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

        # Get the full CSV file duration
        try:
            full_filepath = os.path.join(csv_dir, file_path + '.csv')
            df = pd.read_csv(full_filepath)
            start_time = df.iloc[0]['timestamp']
            end_time = df.iloc[-1]['timestamp'] 
            file_duration = (end_time - start_time) / 1e6  # Convert microseconds to seconds
            
            # Add duration to each annotation class present in this file
            for annotation in file_data.get('annotations', []):
                annotation_class = annotation['class']
                if annotation_class not in annotation_class_full_duration:
                    annotation_class_full_duration[annotation_class] = 0
                annotation_class_full_duration[annotation_class] += file_duration
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

# Print full file duration statistics by annotation class
print("\nFull file duration statistics by annotation class:")
total_full_duration = sum(annotation_class_full_duration.values())
print(f"\nTotal duration of files with annotations: {format_duration(total_full_duration)} ({total_full_duration:.2f} seconds)")
print("\nBy annotation class (full files):")
for class_name, duration in sorted(annotation_class_full_duration.items()):
    print(f"{class_name}: {format_duration(duration)} ({duration:.2f} seconds)")
    print(f"Percentage of total annotated time: {(duration/total_full_duration)*100:.2f}%")

# Print annotation statistics from mapping.json timestamps
total_annotated_time = sum(annotation_class_durations.values())
print(f"\nTotal time covered by annotations: {format_duration(total_annotated_time)} ({total_annotated_time:.2f} seconds)")
print("\nBy annotation class:")
for class_name, duration in sorted(annotation_class_durations.items()):
    print(f"{class_name}: {format_duration(duration)} ({duration:.2f} seconds)")
    print(f"Percentage of total flight time: {(duration/total_annotated_time)*100:.2f}%")
