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
cwd = os.path.dirname(os.path.abspath(__file__))
csv_dir = os.path.join(cwd, "../data/csv_files")
output_csv_dir = os.path.join(cwd, "../data/annotated_csv_files")
mapping_file = os.path.join(cwd, "../data/annotated_csv_files/mapping.json")

# make sure files and dirs exist
if not os.path.isdir(csv_dir):
    os.makedirs(csv_dir)
if not os.path.isdir(output_csv_dir):
    os.makedirs(output_csv_dir)

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

labeled_files = []
for root, _, files in os.walk(output_csv_dir):
    for file in files:
        if file.endswith('.csv'):
            # Get path relative to output_csv_dir
            rel_path = os.path.relpath(root, output_csv_dir)
            if rel_path == '.':
                rel_file = file
            else:
                rel_file = os.path.join(rel_path, file)
            labeled_files.append(rel_file)

# Sort all_files to ensure consistent order
all_files.sort()

# Find first unannotated file for initial load
current_idx = 0
for idx, file in enumerate(all_files):
    if file not in labeled_files:
        current_idx = idx
        break

def main_app(doc: Document):  
    # Customize your classes  
    anomaly_classes = ['Uncategorized', 'Normal','Mechanical', 'Altitude', 'External Position', 
                       'Heading', 'Global Position', 'Electrical']  
        
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

    # Update the header layout to include the loader
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
                    bclear,  # Add clear button
                    css_classes=["controls"],
                    styles={"align-items": "center"}
                ),
            ),
            css_classes=["controls"]
        ),
        css_classes=["nav"],
        styles={"align-items": "center"}  # Center align all items in header
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
        
        # Find next unannotated file
        next_idx = (current_idx + 1) % len(all_files)
        while next_idx != current_idx:
            if all_files[next_idx] not in labeled_files:
                break
            next_idx = (next_idx + 1) % len(all_files)
        
        current_idx = next_idx
        load_file(all_files[current_idx])
        update_single_button(all_files[current_idx])

    def on_prev_click():
        global current_idx
        # Show loader and remove plots while loading
        main_content.children = [header] + [loader]

        # Find previous unannotated file
        prev_idx = (current_idx - 1) % len(all_files)
        while prev_idx != current_idx:
            if all_files[prev_idx] not in labeled_files:
                break
            prev_idx = (prev_idx - 1) % len(all_files)
        
        current_idx = prev_idx
        load_file(all_files[current_idx])
        update_single_button(all_files[current_idx])

    def add_annotation_to_dataframe(df: pd.DataFrame, ranges: list, anomaly_class: str):
        """
        Add annotation to dataframe
        
        Args:
            df: DataFrame to annotate
            ranges: List of [start, end] ranges for anomalies
            anomaly_class: Class label for the anomaly
        """
        if "anomaly" not in df.columns:
            df["anomaly"] = 0
            df["anomaly_class"] = ""

        for _, range_data in ranges:
            for start, end in range_data:
                df.loc[start:end, "anomaly"] = 1
                df.loc[start:end, "anomaly_class"] = anomaly_class

    def update_single_button(fname):
        if fname not in buttons_by_file:
            return
        
        btn = buttons_by_file[fname]
        props = get_button_properties(fname)
        
        btn.label = props["label"]
        btn.button_type = props["button_type"]
        btn.css_classes = props["css_classes"]

    # Modify the update_data_callback to update single button
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
            
            # Print the data being saved
            print(f"Class: {selected_class}")  # Debug print
            
            annotation = {
                "class": selected_class,
                "note": note or "",
                "timestamp": pd.Timestamp.now().isoformat(),
                "ranges": new["data"]
            }
            current_annotations["annotations"].append(annotation)
            
            # Save annotations to DataFrame
            add_annotation_to_dataframe(df, new["data"], selected_class)
            
            # Save annotated CSV
            output_file = os.path.join(output_csv_dir, current_file)
            
            annotation_subfoler = os.path.dirname(output_file)
            if not os.path.isdir(annotation_subfoler):
                os.makedirs(annotation_subfoler)
            
            print(f"Saving annotated file to {output_file}")  # Debug print
            df.to_csv(output_file, index=False)
            
            # Update mapping
            mapping[file_base] = current_annotations
            labeled_files.append(current_file)
            
            # Save all mappings to file
            with open(mapping_file, "w") as f:
                json.dump(mapping, f, indent=2)

            print(f"Updated annotations for {file_base}")
            
            # Update only the current file's button
            update_single_button(current_file)
            
            # After saving, automatically move to next file
            on_next_click()
    # Modify on_clear_click to update single button
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
        
        # Remove the annotated file if it exists
        output_file = os.path.join(output_csv_dir, relative_name)
        if os.path.exists(output_file):
            os.remove(output_file)
        
        # Clear note and reset class selector
        note.value = ""
        class_select.value = anomaly_classes[0]
        
        # Update only the cleared file's button
        update_single_button(relative_name)
        
        # Reload the current file to clear annotations from plot
        load_file(relative_name)


    

    # Initialize file list
    file_items, buttons_by_file = create_file_list()
    file_list = column(
        file_list_title,
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