#!/usr/bin/env python3

#TODO: add multi-class anomaly classification feature

from tornado.web import RequestHandler

from bokeh.layouts import row, column
from bokeh.plotting import Document
from bokeh.server.server import Server
from plotting import add_annotation, annotate_plot, plot_df
from bokeh.models import (
    CustomJS,
    ColumnDataSource,
    Button,
    Div,
    TextInput,
    InlineStyleSheet,
    Paragraph,
    Select,
)

import os
import json
import numpy as np
import pandas as pd
from typing import Optional, Tuple

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


def rand_df_from_csv() -> Tuple[Optional[pd.DataFrame], str]:
    if len(csv_paths) == 0:
        return None, ""
    rand_idx = np.random.randint(len(csv_paths))
    # remove from list
    csv_path = csv_paths.pop(rand_idx)
    df = pd.read_csv(csv_path)
    print(f"Opened {csv_path} for annotation")
    return df, csv_path


class IndexHandler(RequestHandler):
    def get(self):
        self.write("Here have a cookie, 🍪")


def annotate(doc: Document):
    stylesheet = InlineStyleSheet(
        css="""
        .title {
          font-size: 1.8rem;
          font-weight: bold;
          margin: 10px 30px;
          color: #3498db;
          display: block;
          width: 100%;
        }

        .nav {
            display: flex;
            flex-direction: column;
            gap: 15px;
            padding: 10px 0;
            margin-bottom: 10px;
            background: #fff;
            width: 100%;
            border-bottom: 1px solid #eee;
        }

        .nav .bk-row {
            margin-bottom: 10px;
        }

        .filename {
            font-size: 1.2rem;
            font-weight: bold;
            color: #666;
            margin: 10px 30px;
            display: block;
            width: 100%;
        }

        .controls {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 30px;
            background: #fff;
            width: 100%;
        }

        .loader {
          border: 4px solid #e3e3e3;
          border-top: 4px solid #3498db;
          border-radius: 50%;
          width: 20px;
          height: 20px;
          animation: spin 1s linear infinite;
        }

        .bk-btn-group .bk-btn {
            font-size: 1rem;
            color: #222;
            padding: 0;
            border: 0;
            margin-left: 30px;
            outline: none;
            text-decoration: underline;

            &:hover {
                cursor: pointer;
                background: #fff;
            }
            &:active {
                cursor: pointer;
                background: #fff;
                box-shadow: none;
                outline: none;
            }
        }

        @keyframes spin {
          0% {
            transform: rotate(0deg);
          }

          100% {
            transform: rotate(360deg);
          }
        }

        .file-list-panel {
            width: 250px;
            background: #f5f5f5;
            padding: 15px;
            border-left: 1px solid #ddd;
            height: 100vh;
            overflow-y: auto;
            position: fixed;
            right: 0;
            top: 0;
        }

        .file-list-title {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 15px;
            color: #3498db;
        }

        .file-item {
            padding: 8px;
            margin: 4px 0;
            border-radius: 4px;
            font-size: 0.9rem;
        }

        .file-labeled {
            background: #e1f5e1;
            color: #2c662d;
        }

        .file-unlabeled {
            background: #fff;
            color: #666;
        }

        .main-content {
            margin-right: 250px;
        }
    """
    )
    title = Div(
        text="Annotate anomalies in log file",
        visible=True,
        css_classes=["title"],
        width_policy="max"
    )

    loader = Div(text="", width=20, height=20, visible=False, css_classes=["loader"])
    bskip = Button(label="Skip", button_type="primary")
    bsave = Button(label="Save", button_type="primary")
    bundo = Button(label="Undo", button_type="primary")
    note = TextInput(title="Note", placeholder="Add a note for this annotation")

    # Source to receive value passed by button
    source = ColumnDataSource(data=dict(data=[]))

    df, csv_path = rand_df_from_csv()
    if df is None:
        title.text = "All files have been annotated. Thank you for contributing"
        title.styles = {"flex-grow": "0"}
        doc.add_root(
            row(
                title,
                sizing_mode="scale_width",
                styles={"justify-content": "center"},
                stylesheets=[stylesheet],
            )
        )
        return
    models = plot_df(df)

    # Add class selector
    anomaly_classes = ['Mechanical', 'Altitude', 'External Position', 
                       'Heading', 'Global Position', 'Electrical']  # Customize your classes    
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

    def create_file_list():
        all_files = set(os.listdir(csv_dir))
        labeled_files = set(os.listdir(output_csv_dir))
        
        file_items = []
        
        # Process all files
        for fname in sorted(all_files):  # Sort files for consistent display
            if fname.endswith('.csv'):
                is_labeled = fname in labeled_files
                file_info = mapping.get(fname[:-4], {"annotations": []})
                annotations = file_info.get("annotations", [])
                
                if is_labeled and annotations:
                    # Show file with its annotations
                    classes = ", ".join(set(ann["class"] for ann in annotations))
                    annotation_count = len(annotations)
                    text = f"✓ {fname}<br><small>Classes: {classes}<br>Annotations: {annotation_count}</small>"
                    div = Div(text=text, css_classes=["file-item", "file-labeled"])
                else:
                    # Show unlabeled file
                    div = Div(text=f"○ {fname}", css_classes=["file-item", "file-unlabeled"])
                file_items.append(div)
        
        return file_items

    file_list = column(
        file_list_title,
        *create_file_list(),
        css_classes=["file-list-panel"]
    )

    # Update the layout structure with more explicit containers
    header = column(
        row(title, sizing_mode="stretch_width"),
        row(filename_display, sizing_mode="stretch_width"),
        row(
            note,
            class_select,
            bundo,
            bskip,
            bsave,
            css_classes=["controls"],
            sizing_mode="stretch_width"
        ),
        css_classes=["nav"],
        sizing_mode="stretch_width"
    )

    main_content = column(
        header,
        *models,
        sizing_mode="stretch_width",
        styles={"align-items": "center"},
        css_classes=["main-content"]
    )

    # Update receive_box_data to refresh file list
    def receive_box_data(attr, old, new):
        nonlocal df, csv_path
        if new.get("data") is None or len(new["data"]) == 0:
            return
        print(f"Received box coordinates")
        print(new["data"])
        # TODO: find a better way of passing data from js to python
        # source on_change event is only triggered when a non
        # empty list is passed. If a log file does not contain anomalies
        # passing empty list will not trigger the on_change event. In order
        # to bypass this edge case a dummy entry is always added to the end
        # of the data being passed.
        new["data"].pop()  # remove dummy entry
        save = new["data"].pop()  # second last entry indicates whether to save
        
        # Only process note and class if we're saving
        if save and len(new["data"]) >= 2:  # Check if we have enough data
            note = new["data"].pop()  # get the note
            selected_class = new["data"].pop()  # get the anomaly class
            
            # Get existing annotations for this file
            file_base = os.path.basename(csv_path)[:-4]
            current_annotations = mapping.get(file_base, {
                "annotations": []
            })
            
            # Add new annotation
            annotation = {
                "class": selected_class,
                "note": note or "",
                "timestamp": pd.Timestamp.now().isoformat(),
                "ranges": new["data"]  # Store the actual ranges for this annotation
            }
            current_annotations["annotations"].append(annotation)
            
            # Save annotations
            add_annotation(df, new["data"], selected_class)
            csv_loc = os.path.join(output_csv_dir, os.path.basename(csv_path))
            print(f"Saving annotated file to {csv_loc}")
            df.to_csv(csv_loc, index=False)
            
            # Update mapping
            mapping[file_base] = current_annotations
            
            # Save all mappings to file
            with open(mapping_file, "w") as f:
                json.dump(mapping, f, indent=2)

            print(f"Updated annotations for {file_base}")
            print(f"Current mapping contains {len(mapping)} files")

        # user didn't save annotated file, so add the file back to the list
        if not save:
            if csv_path not in csv_paths:  # Only add if not already in the list
                csv_paths.append(csv_path)

        # clear plot
        for model in models:
            model.renderers = []
            model.legend.items = []

        # Store current path before getting new one
        current_path = csv_path

        # load new data
        df, csv_path = rand_df_from_csv()
        if df is None:
            # If we skipped the last file, add it back to the list
            if not save and current_path not in csv_paths:
                csv_paths.append(current_path)
                # Try getting a new file again
                df, csv_path = rand_df_from_csv()

        if df is None:
            # hide everything except title and file list
            for model in models:
                model.visible = False
            bsave.visible = False
            bundo.visible = False
            note.visible = False
            class_select.visible = False
            loader.visible = False
            title.text = "All files have been annotated. Thank you for contributing"
            
            # Update file list one last time
            file_list.children = [file_list_title] + create_file_list()
            return

        # Update filename display
        filename_display.text = f"Current file: {os.path.basename(csv_path)}"
        
        plot_df(df, models)
        loader.visible = False

        # Update file list after processing
        file_list.children = [file_list_title] + create_file_list()

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
    bskip.js_on_click(
        CustomJS(
            args=dict(loader=loader, source=source),
            code="""
                loader.visible = true
                source.data = {
                    data: [0, false]  // Minimal data: [dummy_value, save_flag]
                }
                source.change.emit()
                if (window.boxes) {
                    window.boxes.forEach(({ fig, box }) => {
                        fig.remove_layout(box)
                        box.visible = false
                    })
                    window.boxes = []
                }
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

    def on_session_destroyed(session_context):
        csv_loc = os.path.join(output_csv_dir, os.path.basename(csv_path))
        if os.path.exists(csv_loc):
            return
        # user didn't save annotated file, so add the file back to the list
        csv_paths.append(csv_path)

    # Initialize filename display with first file
    if df is not None:
        filename_display.text = f"Current file: {os.path.basename(csv_path)}"

    # Create layout with main content and file list
    layout = row(
        main_content,
        file_list,
        sizing_mode="stretch_both"
    )

    # Initialize file list
    file_list.children = [file_list_title] + create_file_list()

    doc.add_root(layout)
    doc.on_session_destroyed(on_session_destroyed)


def annotated_files(doc: Document):
    annotated_files = [
        name[:-4] for name in os.listdir(output_csv_dir) if name.endswith(".csv")
    ]
    models = []
    stylesheet = InlineStyleSheet(
        css="""
        .title {
          font-size: 1.8rem;
          font-weight: bold;
          color: #3498db;
        }

        .bk-btn-group .bk-btn {
            font-size: 1rem;
            color: #222;
            display: list-item;
            padding: 0;
            border: 0;
            margin-left: 1.3rem;
            list-style-type: disc;
            outline: none;
            text-decoration: underline;

            &:hover {
                cursor: pointer;
                background: #fff;
            }
            &:active {
                cursor: pointer;
                background: #fff;
                box-shadow: none;
                outline: none;
            }
        }
    """
    )
    title = Div(
        text="Annotated files",
        css_classes=["title"],
    )
    msg = Paragraph(text="No annotated logs yet...", visible=False)
    for name in annotated_files:
        file_info = mapping.get(name, {"annotations": []})
        annotations = file_info.get("annotations", [])
        classes = ", ".join(set(ann["class"] for ann in annotations))
        label_text = f"{name} (Classes: {classes})"
        
        li = Button(
            label=label_text,
            button_type="light",
            stylesheets=[stylesheet],
        )
        li.js_on_click(
            CustomJS(
                args=dict(name=name),
                code="""
                    window.location="/plot?id=" + name
                """,
            )
        )
        models.append(li)

    if len(models) == 0:
        msg.visible = True
    doc.add_root(
        column(
            title,
            column(msg, *models),
            sizing_mode="scale_width",
            styles={"align-items": "center"},
            stylesheets=[stylesheet],
        )
    )


def show_plot(doc: Document):
    args = doc.session_context.request.arguments
    id = args.get("id", [b""])[0].decode()

    csv_path = os.path.join(output_csv_dir, id + ".csv")
    if not os.path.exists(csv_path):
        msg = Div(
            text="Not found",
            visible=True,
            styles={
                "font-size": "1.8rem",
                "font-weight": "bold",
                "color": "#3498db",
                "margin": "auto",
            },
        )
        doc.add_root(msg)
        return

    df = pd.read_csv(csv_path)
    models = plot_df(df, highlight=False)
    annotate_plot(df, models)

    doc.add_root(
        row(
            column(*models),
            sizing_mode="scale_width",
            styles={"justify-content": "center"},
        )
    )



server = Server(
    {"/": annotate, "/files": annotated_files, "/plot": show_plot},
    num_procs=1,
    extra_patterns=[("/cookie", IndexHandler)],
)
server.start()

if __name__ == "__main__":
    from bokeh.util.browser import view

    print(
        "Opening Tornado app with embedded Bokeh application on http://localhost:5006/"
    )

    server.io_loop.add_callback(view, "http://localhost:5006/")
    server.io_loop.start()
