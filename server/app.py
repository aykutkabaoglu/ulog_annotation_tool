#!/usr/bin/env python3

from bokeh.layouts import row, column
from bokeh.plotting import Document
from bokeh.server.server import Server
from plotting import plot_df
from bokeh.models import (
    CustomJS,
    ColumnDataSource,
    Button,
    Div,
    TextInput,
    Select
)
from css import LAYOUT_SETTINGS

import os
import json
import pandas as pd
import numpy as np
cwd = os.path.dirname(os.path.abspath(__file__))
csv_dir = os.path.join(cwd, "../data/csv_files")
mapping_file = os.path.join(cwd, "../data/mapping.json")

# make sure files and dirs exist
if not os.path.isdir(csv_dir):
    os.makedirs(csv_dir)

mapping = {}
if os.path.exists(mapping_file):
    with open(mapping_file, "r") as f:
        mapping = json.load(f)

all_files = []
for root, _, files in os.walk(csv_dir):
    for file in files:
        if file.endswith('.csv'):
            # Get path relative to csv_dir
            rel_path = os.path.relpath(root, csv_dir)
            if rel_path == '.':
                rel_file = file
            else:
                rel_file = os.path.join(rel_path, file)
            all_files.append(rel_file)

labeled_files = [f"{key}.csv" for key in mapping.keys()]

# Sort all_files to ensure consistent order
all_files.sort()

# Find first unannotated file for initial load
current_idx = 0
for idx, file in enumerate(all_files):
    if file[:-4] not in mapping:  # Remove .csv extension when checking mapping
        current_idx = idx
        break

def main_app(doc: Document):  
    # Customize your classes  
    anomaly_classes = ['Uncategorized', 'Normal','Mechanical', 'Altitude', 'External Position', 
                       'Heading', 'Global Position', 'Electrical']  
    
    # Calculate statistics
    total_files = len(all_files)
    labeled_count = len(labeled_files)
    unlabeled_count = total_files - labeled_count
    
    # Count files by class
    class_counts = {cls: 0 for cls in anomaly_classes}
    for file_base, file_data in mapping.items():
        file_classes = set()
        for annotation in file_data.get("annotations", []):
            file_classes.add(annotation["class"])
        for cls in file_classes:
            class_counts[cls] = class_counts.get(cls, 0) + 1
    
    # Create statistics display
    stats_text = f"""
        <div style="font-size: 14px; color: #FFFFFF; text-align: left; padding: 10px;">
            <h3 style="color: #909090; margin-bottom: 10px;">File Statistics:</h3>
            <p>Total Files: {total_files}</p>
            <p>Labeled Files: {labeled_count}</p>
            <p>Unlabeled Files: {unlabeled_count}</p>
            <h4 style="color: #909090; margin: 10px 0;">Classifications:</h4>
            {''.join(f'<p>{cls}: {count}</p>' for cls, count in class_counts.items() if count > 0)}
        </div>
    """
    
    stats_display = Div(
        text=stats_text,
        css_classes=["stats-display"],
        styles={
            "background": "rgba(32, 32, 32, 0.8)",
            "border-radius": "5px",
            "padding": "10px",
            "margin-bottom": "20px"
        }
    )
        
    bokeh_models = []  # Initialize empty list for models
    
    title = Div(
        text="Annotate anomalies in log file",
        visible=True,
        css_classes=["title"],
        styles={"text-align": "center",
                "font-size": "36px",
                "font-weight": "bold",
                "margin": "20px 0",
                "padding": "10px",
                "color": "#909090"
                }
    )

    loader = Div(
        text="""
            <div class="loading-spinner">
                <div class="spinner"></div>
                <div class="loading-text">Loading...</div>
            </div>
        """,
        width=200,
        height=200,
        visible=True,
        css_classes=["loader-container"],
        styles={
            "z-index": "9999",
            "background-color": "rgba(32, 32, 32, 0.8)",  # Semi-transparent dark background
            "padding": "10px",
            "border-radius": "10px",
            "text-align": "center",
            "font-size": "36px",
        }
    )
    bprev = Button(label="Previous", button_type="primary")
    bnext = Button(label="Next", button_type="primary")
    bsave = Button(label="Save", button_type="primary")
    bundo = Button(label="Undo", button_type="primary")
    note = TextInput(title="Note", placeholder="Add a note for this annotation")

    # Source to receive value passed by button
    source = ColumnDataSource(data=dict(data=[]))

    # Add class selector
    class_select = Select(
        title="Anomaly Class:",
        value=anomaly_classes[0],
        options=anomaly_classes
    )

    # Add filename display
    filename_display = Div(
        text="Current file: None",
        css_classes=["filename"],
        width_policy="max",
        styles={"font-size": "24px",
                "color": "#FFFFFF",
                "text-align": "center"}
    )

    # Add anomaly classes display
    anomaly_classes_display = Div(
        text="",
        css_classes=["anomaly-classes"],
        width_policy="max",
        styles={"font-size": "18px",
                "color": "#909090",
                "text-align": "center",
                "margin-top": "5px"}
    )

    # Create file list panel
    file_list_title = Div(
        text="Files in Directory",
        css_classes=["file-list-title"],
        styles={"font-size": "24px",
                "color": "#FFFFFF",
                "text-align": "center"}
    )

    # Add clear button in the header section where other buttons are defined
    bclear = Button(label="Clear", button_type="danger")

    # Update the header layout to include the loader and stats
    header = column(
        row(title),
        row(filename_display),
        row(anomaly_classes_display),
        row(
            column(
                row(
                    note,
                    class_select,
                    styles={"align-items": "center"}
                ),
                row(
                    bundo,
                    bprev,
                    bnext,
                    bsave,
                    bclear,
                    css_classes=["controls"],
                    styles={"align-items": "center"}
                ),
            ),
            css_classes=["controls"]
        ),
        css_classes=["nav"],
        styles={"align-items": "center"}
    )

    main_content = column(
        header,
        loader,
        *bokeh_models,
        sizing_mode="stretch_width",
        styles={
            "align-items": "center", 
            "min-height": "100%",
            "flex": "0.75"  # Take up 85% of the space
        },
        css_classes=["main-content"]
    )

    def create_file_list():
        file_items = []
        
        # Group files by directory
        files_by_dir = {}
        for fname in all_files:
            dir_path = os.path.dirname(fname)
            if dir_path == '':
                dir_path = '.'
            if dir_path not in files_by_dir:
                files_by_dir[dir_path] = []
            files_by_dir[dir_path].append(fname)
        
        # Create folder structure
        buttons_by_file = {}  # Store buttons for later updates
        for dir_path, files in sorted(files_by_dir.items()):
            # Add folder header if not in root
            if dir_path != '.':
                folder_header = Div(
                    text=f"📁 {dir_path}",
                    styles={
                        "font-size": "18px",
                        "font-weight": "bold",
                        "color": "#FFFFFF",
                        "padding": "10px 5px 5px 5px",
                        "margin-top": "10px",
                        "border-bottom": "1px solid #555555"
                    }
                )
                file_items.append(folder_header)
            
            # Add files in the current directory
            for fname in sorted(files):
                btn = create_file_button(fname)
                buttons_by_file[fname] = btn
                file_items.append(btn)
        
        return file_items, buttons_by_file

    def get_button_properties(fname):
        """Helper function to determine button type and label based on file annotations"""
        is_labeled = fname in labeled_files
        file_info = mapping.get(fname[:-4], {"annotations": []})
        annotations = file_info.get("annotations", [])
        display_name = os.path.basename(fname)
        
        # Default values for unlabeled files
        button_type = "light"
        label = f"○ {display_name}"
        
        if is_labeled and annotations:
            classes = set(ann["class"] for ann in annotations)
            if all(c == "Normal" for c in classes):
                button_type = "primary"  # Blue for Normal
            elif all(c == "Uncategorized" for c in classes):
                button_type = "warning"  # Orange for Uncategorized
            else:
                button_type = "success"  # Green for other anomalies
            
            classes_str = ", ".join(classes)
            annotation_count = len(annotations)
            label = f"✓ {display_name}\nClasses: {classes_str}\nAnnotations: {annotation_count}"
        
        return {
            "button_type": button_type,
            "label": label,
            "css_classes": ["file-item", "file-labeled" if is_labeled else "file-unlabeled"]
        }

    def create_file_button(fname):
        props = get_button_properties(fname)
        
        btn = Button(
            label=props["label"],
            button_type=props["button_type"],
            css_classes=props["css_classes"],
            styles={
                "margin-left": "15px" if os.path.dirname(fname) != '.' else "0px"
            }
        )
        
        btn.js_on_click(CustomJS(
            args=dict(fname=fname, source=source, loader=loader),
            code="""
                source.data = {
                    'data': ['load_file', fname]
                };
                source.change.emit();
            """
        ))
        
        return btn

    def convert_global_position(df):
        # Calculate relative global positions
        if 'vehicle_global_position.lat' in df.columns:
            # Convert to degrees first
            df['vehicle_global_position.lat'] = df['vehicle_global_position.lat']
            df['vehicle_global_position.lon'] = df['vehicle_global_position.lon']
            df['vehicle_global_position.alt'] = df['vehicle_global_position.alt']
            # Convert lat/lon differences to approximate meters
            # Using simple approximation: 1 degree = 111,111 meters at the equator
            df['vehicle_global_position.x'] = (df['vehicle_global_position.lon'] - df['vehicle_global_position.lon'].iloc[0]) * 111111 * np.cos(np.radians(df['vehicle_global_position.lat'].iloc[0]))
            df['vehicle_global_position.y'] = (df['vehicle_global_position.lat'] - df['vehicle_global_position.lat'].iloc[0]) * 111111
            df['vehicle_global_position.z'] = df['vehicle_global_position.alt'] - df['vehicle_global_position.alt'].iloc[0]

        if 'vehicle_gps_position.lat' in df.columns:
            # Convert to degrees first
            df['vehicle_gps_position.lat'] = df['vehicle_gps_position.lat'] * 1e-7
            df['vehicle_gps_position.lon'] = df['vehicle_gps_position.lon'] * 1e-7
            df['vehicle_gps_position.alt'] = df['vehicle_gps_position.alt'] * 1e-3

            # Convert lat/lon differences to approximate meters
            df['vehicle_gps_position.x'] = (df['vehicle_gps_position.lon'] - df['vehicle_gps_position.lon'].iloc[0]) * 111111 * np.cos(np.radians(df['vehicle_gps_position.lat'].iloc[0]))
            df['vehicle_gps_position.y'] = (df['vehicle_gps_position.lat'] - df['vehicle_gps_position.lat'].iloc[0]) * 111111
            df['vehicle_gps_position.z'] = df['vehicle_gps_position.alt'] - df['vehicle_gps_position.alt'].iloc[0]

    def invert_z_position(df):
        if 'vehicle_local_position.z' in df.columns:
            df['vehicle_local_position.z'] = -df['vehicle_local_position.z']
        if 'vehicle_local_position_setpoint.z' in df.columns:
            df['vehicle_local_position_setpoint.z'] = -df['vehicle_local_position_setpoint.z']
        if 'vehicle_visual_odometry.z' in df.columns:
            df['vehicle_visual_odometry.z'] = -df['vehicle_visual_odometry.z']
        if 'vehicle_vision_position.z' in df.columns:
            df['vehicle_vision_position.z'] = -df['vehicle_vision_position.z']

    # Add new function to handle file navigation
    def load_file(relative_name):
        global csv_path, df, current_idx
        nonlocal bokeh_models, main_content
        
        # Update current_idx to match the loaded file
        current_idx = all_files.index(relative_name)
        
        # Update anomaly classes display
        file_base = relative_name[:-4]
        if file_base in mapping:
            classes = set()
            for annotation in mapping[file_base]["annotations"]:
                classes.add(annotation["class"])
            classes_text = ", ".join(sorted(classes))
            anomaly_classes_display.text = f"Annotated classes: {classes_text}"
        else:
            anomaly_classes_display.text = "No annotations"
        
        csv_path = os.path.join(csv_dir, relative_name)
        if csv_path and os.path.exists(csv_path):
            # Load the new file
            df = pd.read_csv(csv_path)

            convert_global_position(df)
            invert_z_position(df)
            
            # Update filename display
            filename_display.text = f"Current file: {relative_name}"  # Show full relative path
            
            # Create new bokeh models or update existing models with new data
            bokeh_models = plot_df(df, mapping, relative_name)
            
            # Update main_content with models and hide loader
            main_content.children = [header] + bokeh_models
            
            return True
        return False

    def on_next_click():
        global current_idx
        # Show loader and remove plots while loading
        main_content.children = [header] + [loader]
        
        # Find next file, allowing both annotated and unannotated files
        next_idx = (current_idx + 1) % len(all_files)
        current_idx = next_idx
        load_file(all_files[current_idx])
        update_single_button(all_files[current_idx])

    def on_prev_click():
        global current_idx
        # Show loader and remove plots while loading
        main_content.children = [header] + [loader]

        # Find previous file, allowing both annotated and unannotated files
        prev_idx = (current_idx - 1) % len(all_files)
        current_idx = prev_idx
        load_file(all_files[current_idx])
        update_single_button(all_files[current_idx])

    def update_single_button(fname):
        if fname not in buttons_by_file:
            return
        
        btn = buttons_by_file[fname]
        props = get_button_properties(fname)
        
        btn.label = props["label"]
        btn.button_type = props["button_type"]
        btn.css_classes = props["css_classes"]

    # Update the stats when saving annotations
    def update_stats_display():
        nonlocal stats_display
        labeled_count = len(labeled_files)
        unlabeled_count = len(all_files) - labeled_count
        
        # Recount files by class
        class_counts = {cls: 0 for cls in anomaly_classes}
        for file_base, file_data in mapping.items():
            file_classes = set()
            for annotation in file_data.get("annotations", []):
                file_classes.add(annotation["class"])
            for cls in file_classes:
                class_counts[cls] = class_counts.get(cls, 0) + 1
        
        stats_text = f"""
            <div style="font-size: 14px; color: #FFFFFF; text-align: left; padding: 10px;">
                <h3 style="color: #909090; margin-bottom: 10px;">File Statistics:</h3>
                <p>Total Files: {len(all_files)}</p>
                <p>Labeled Files: {labeled_count}</p>
                <p>Unlabeled Files: {unlabeled_count}</p>
                <h4 style="color: #909090; margin: 10px 0;">Classifications:</h4>
                {''.join(f'<p>{cls}: {count}</p>' for cls, count in class_counts.items() if count > 0)}
            </div>
        """
        stats_display.text = stats_text

    # Modify the update_data_callback to update single button and refresh stats
    def update_data_callback(attr, old, new):
        global current_idx
        if new.get("data") is None or len(new["data"]) == 0:
            return

        action = new["data"][0]

        # Show loader and remove plots while loading
        main_content.children = [header] + [loader]
        
        if action == "load_file":
            main_content.children = [header] + [loader]
            filename = new["data"][1]
            current_idx = all_files.index(filename)
            new_path = os.path.join(csv_dir, filename)
            print(f"Loading file: {new_path}")
            load_file(filename)
            return
        
        # Handle save action
        new["data"].pop()  # remove dummy entry
        save = new["data"].pop()  # second last entry indicates whether to save
        
        if save and len(new["data"]) >= 2:
            note = new["data"].pop()
            selected_class = new["data"].pop()
            
            # Get the current file name from the actual loaded file path
            current_file = all_files[current_idx]
            file_base = current_file[:-4]  # Remove .csv extension
            
            print(f"Saving annotation for file: {current_file}")  # Debug print
            
            current_annotations = mapping.get(file_base, {
                "annotations": []
            })
            
            # Convert datetime to timestamp using DataFrame indices
            ranges = new["data"]
            for name, range_data in ranges:
                for i, (start, end) in enumerate(range_data):
                    epoch_start = start * 1e3 # we lose ms precision because of javascript Date object
                    epoch_end = end * 1e3
                    range_data[i] = [int(epoch_start), int(epoch_end)]
            
            annotation = {
                "class": selected_class,
                "note": note or "",
                "timestamp": pd.Timestamp.now().isoformat(),
                "ranges": ranges
            }
            current_annotations["annotations"].append(annotation)
            
            # Update mapping
            mapping[file_base] = current_annotations
            labeled_files.append(current_file)
            
            # Save all mappings to file
            with open(mapping_file, "w") as f:
                json.dump(mapping, f, indent=2)

            print(f"Updated annotations for {file_base}")
            
            # Update only the current file's button
            update_single_button(current_file)
            
            # Update statistics display
            update_stats_display()
            
            # After saving, automatically move to next file
            on_next_click()

    # Modify on_clear_click to update single button and refresh stats
    def on_clear_click():
        global current_idx
        relative_name = all_files[current_idx]
        
        # Remove from mapping
        file_base = relative_name[:-4]  # Remove .csv extension
        if file_base in mapping:
            del mapping[relative_name[:-4]]
            
            # Save updated mapping
            with open(mapping_file, "w") as f:
                json.dump(mapping, f, indent=2)
        
        # Remove from labeled_files if present
        if relative_name in labeled_files:
            labeled_files.remove(relative_name)

        # Clear note and reset class selector
        note.value = ""
        class_select.value = anomaly_classes[0]
        
        # Update only the cleared file's button
        update_single_button(relative_name)
        
        # Update statistics display
        update_stats_display()
        
        # Reload the current file to clear annotations from plot
        load_file(relative_name)


    

    # Initialize file list with stats at the bottom
    file_items, buttons_by_file = create_file_list()
    file_list = column(
        file_list_title,
        stats_display,
        *file_items,
        css_classes=["file-list-panel"],
        styles={
            "overflow-y": "auto",
            "height": "100vh",
            "flex": "0.25"
        }
    )

    # Initialize with first file
    load_file(all_files[current_idx])

    ##### PAGE LAYOUT #####
    # Add click handler for clear button
    bclear.on_click(on_clear_click)
    # Add the button click handlers
    bnext.on_click(on_next_click)
    bprev.on_click(on_prev_click)
    # add listeners
    source.on_change("data", update_data_callback)
    bsave.js_on_click(
        CustomJS(
            args=dict(loader=loader, source=source, class_select=class_select, name=note),
            code="""
                if (!window.boxes) {
                    window.boxes = []
                }
                const ranges = new Map()
                boxes.forEach(
                    ({ name, box }) => {
                        if (!ranges.has(name)) ranges.set(name, [])
                        const range = ranges.get(name)
                        range.push([Math.round(box.left), Math.round(box.right)].sort((a, b) => a - b))
                    }
                )
                const data = Array.from(ranges.entries())
                data.push(class_select.value)  // Add selected class
                data.push(name.value)  // Add note
                data.push(true) // for saving
                data.push(Math.random()) // ensuring on_change gets triggered
                source.data = {
                    data
                }
                source.change.emit()
                window.boxes.forEach(({ fig, box }) => {
                    fig.remove_layout(box)
                    box.visible = false
                })
                window.boxes = []
            """,
        )
    )
    bundo.js_on_click(
        CustomJS(
            args=dict(),
            code="""
                if (!window.boxes || !window.boxes.length) return
                const { name, box } = window.boxes.pop()
                box.visible = false
            """
        )
    )

    # Create layout with main content and file list
    layout = row(
        main_content,
        file_list,
        **LAYOUT_SETTINGS
    )

    # Update theme assignment
    doc.add_root(layout)


if __name__ == "__main__":
    from bokeh.util.browser import view


    server = Server(
    {"/": main_app},
    num_procs=1
    )
    server.io_loop.add_callback(view, "http://localhost:5006/")
    server.io_loop.start()