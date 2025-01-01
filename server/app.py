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
    Select,
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

# only include files which haven't been annotated
csv_paths = [
    os.path.join(csv_dir, csv_file_name)
    for csv_file_name in set(os.listdir(csv_dir)).difference(os.listdir(output_csv_dir))
]


def main_app(doc: Document):

    # Customize your classes  
    anomaly_classes = ['Mechanical', 'Altitude', 'External Position', 
                       'Heading', 'Global Position', 'Electrical']  
        
    bokeh_models = []  # Initialize empty list for models
    
    title = Div(
        text="Annotate anomalies in log file",
        visible=True,
        css_classes=["title"],
        width_policy="max"
    )

    loader = Div(
        text="<div></div>",  # Empty div that will get the loader style
        width=20,
        height=20,
        visible=True,  # Set to True initially
        css_classes=["loader"],
        styles={"display": "inline-block"}
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
        width_policy="max"
    )

    # Create file list panel
    file_list_title = Div(
        text="Files in Directory",
        css_classes=["file-list-title"]
    )

    # Add clear button in the header section where other buttons are defined
    bclear = Button(label="Clear", button_type="danger")

    # Update the header layout to include the clear button
    header = column(
        row(title, sizing_mode="stretch_width"),
        row(filename_display, sizing_mode="stretch_width"),
        row(
            note,
            class_select,
            bundo,
            bprev,
            bnext,
            bsave,
            bclear,  # Add clear button
            css_classes=["controls"],
            sizing_mode="stretch_width"
        ),
        css_classes=["nav"],
        sizing_mode="stretch_width"
    )

    main_content = column(
        header,
        *bokeh_models,
        sizing_mode="stretch_width",
        styles={"align-items": "center"},
        css_classes=["main-content"]
    )

    def create_file_list():
        all_files = set(os.listdir(csv_dir))
        labeled_files = set(os.listdir(output_csv_dir))
        
        file_items = []
        
        for fname in sorted(all_files):
            if fname.endswith('.csv'):
                is_labeled = fname in labeled_files
                file_info = mapping.get(fname[:-4], {"annotations": []})
                annotations = file_info.get("annotations", [])
                
                # Create toggle button for each file
                button_type = "success" if is_labeled else "light"
                
                if is_labeled and annotations:
                    classes = ", ".join(set(ann["class"] for ann in annotations))
                    annotation_count = len(annotations)
                    label = f"✓ {fname}\nClasses: {classes}\nAnnotations: {annotation_count}"
                else:
                    label = f"○ {fname}"
                
                btn = Button(
                    label=label,
                    button_type=button_type,
                    css_classes=["file-item", "file-labeled" if is_labeled else "file-unlabeled"],
                    width=200
                )
                
                # Add click handler
                btn.js_on_click(CustomJS(
                    args=dict(
                        fname=fname,
                        source=source,
                        loader=loader
                    ),
                    code="""
                        loader.visible = true;
                        source.data = {
                            'data': ['load_file', fname]
                        };
                        source.change.emit();
                    """
                ))
                
                file_items.append(btn)
        
        return file_items


    # Add new function to handle file navigation
    def load_file(file_path):
        global csv_path, df
        nonlocal bokeh_models, main_content
        if file_path and os.path.exists(file_path):
            # Load the new file
            csv_path = file_path
            df = pd.read_csv(csv_path)
            
            # Update filename display
            filename_display.text = f"Current file: {os.path.basename(csv_path)}"
            
            # Create new bokeh models or update existing models with new data
            bokeh_models = plot_df(df, mapping, os.path.basename(csv_path))
            
            # Update main_content with models
            main_content.children = [header] + bokeh_models
            
            return True
        return False

    # Add click handlers for next/previous buttons
    def get_file_list():
        return sorted([os.path.join(csv_dir, f) for f in os.listdir(csv_dir) if f.endswith('.csv')])

    def update_file_list():
        file_list.children = [file_list_title] + create_file_list()

    def on_next_click():
        files = get_file_list()
        if not files:
            return
        update_file_list()
        try:
            current_idx = files.index(csv_path)
            next_idx = (current_idx + 1) % len(files)
            load_file(files[next_idx])
        except ValueError:
            # If current file not found in list, load first file
            load_file(files[0])

    def on_prev_click():
        files = get_file_list()
        if not files:
            return
        update_file_list()
        try:
            current_idx = files.index(csv_path)
            prev_idx = (current_idx - 1) % len(files)
            load_file(files[prev_idx])
        except ValueError:
            # If current file not found in list, load last file
            load_file(files[-1])

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

    # Update receive_box_data to handle only save and load_file actions
    def receive_box_data(attr, old, new):
        if new.get("data") is None or len(new["data"]) == 0:
            return

        action = new["data"][0]
        
        if action == "load_file":
            # Load the selected file
            filename = new["data"][1]
            new_path = os.path.join(csv_dir, filename)
            loader.visible = True
            print(f"Loading file: {new_path}")

            # Use the existing load_file function to handle file loading, plotting, and annotations
            load_file(new_path)
            
            loader.visible = False
            return
        
        # Handle save action
        new["data"].pop()  # remove dummy entry
        save = new["data"].pop()  # second last entry indicates whether to save
        
        if save and len(new["data"]) >= 2:
            note = new["data"].pop()
            selected_class = new["data"].pop()
            
            # Get the current file name from the actual loaded file path
            current_file = os.path.basename(csv_path)
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
            print(f"Saving annotated file to {output_file}")  # Debug print
            df.to_csv(output_file, index=False)
            
            # Update mapping
            mapping[file_base] = current_annotations
            
            # Save all mappings to file
            with open(mapping_file, "w") as f:
                json.dump(mapping, f, indent=2)

            print(f"Updated annotations for {file_base}")
            
            # After saving, automatically move to next file
            on_next_click()
        
        loader.visible = False

    def on_session_destroyed(session_context):
        csv_loc = os.path.join(output_csv_dir, os.path.basename(csv_path))
        if os.path.exists(csv_loc):
            return
        # user didn't save annotated file, so add the file back to the list
        csv_paths.append(csv_path)

    # Add clear function
    def on_clear_click():
        current_file = os.path.basename(csv_path)
        file_base = current_file[:-4]
        
        # Remove from mapping
        if file_base in mapping:
            del mapping[file_base]
            
            # Save updated mapping
            with open(mapping_file, "w") as f:
                json.dump(mapping, f, indent=2)
        
        # Remove the annotated file if it exists
        output_file = os.path.join(output_csv_dir, current_file)
        if os.path.exists(output_file):
            os.remove(output_file)
        
        # Clear note and reset class selector
        note.value = ""
        class_select.value = anomaly_classes[0]
        
        # Reload the current file to clear annotations from plot
        load_file(csv_path)
        
        # Update file list to reflect changes
        file_list.children = [file_list_title] + create_file_list()

    # Add click handler for clear button
    bclear.on_click(on_clear_click)

    file_list = column(
        file_list_title,
        *create_file_list(),
        css_classes=["file-list-panel"],
        width=250,
        height_policy="fit",
        sizing_mode="stretch_height"
    )

    # Initialize with first file
    load_file(csv_paths[0])

    ##### PAGE LAYOUT #####

    # Add the button click handlers
    bnext.on_click(on_next_click)
    bprev.on_click(on_prev_click)
    # add listeners
    source.on_change("data", receive_box_data)
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
                loader.visible = true
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
            """,
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
    doc.on_session_destroyed(on_session_destroyed)



if __name__ == "__main__":
    from bokeh.util.browser import view


    server = Server(
    {"/": main_app},
    num_procs=1
    )
    server.io_loop.add_callback(view, "http://localhost:5006/")
    server.io_loop.start()

def get_file_base(file_path):
    """Get the base name of the file without extension"""
    return os.path.basename(file_path)[:-4]

def get_output_file_path(file_path):
    """Get the path for the annotated output file"""
    return os.path.join(output_csv_dir, os.path.basename(file_path))

def save_mapping():
    """Save mapping to JSON file"""
    with open(mapping_file, "w") as f:
        json.dump(mapping, f, indent=2)

def get_latest_annotation(file_base):
    """Get the most recent annotation for a file"""
    if file_base in mapping and mapping[file_base]["annotations"]:
        return mapping[file_base]["annotations"][-1]
    return None
