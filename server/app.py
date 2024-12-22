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
          margin-left: 30px;
          color: #3498db;
          flex-grow: 1;
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

        .nav {
            align-items: center;
            justify-content: right;
            position: sticky;
            top: 0;
            z-index: 1000;
            background: #fff;
        }

        @keyframes spin {
          0% {
            transform: rotate(0deg);
          }

          100% {
            transform: rotate(360deg);
          }
        }
    """
    )
    title = Div(
        text="Annotate anomalies in log file",
        visible=True,
        css_classes=["title"],
    )
    tutorial = Button(
        label="How to annotate?", button_type="light", stylesheets=[stylesheet]
    )
    loader = Div(text="", width=20, height=20, visible=False, css_classes=["loader"])
    bskip = Button(label="Skip", button_type="primary")
    bsave = Button(label="Save", button_type="primary")
    bundo = Button(label="Undo", button_type="primary")
    name = TextInput(placeholder="Contributor name")

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

        if save:
            add_annotation(df, new["data"])
            csv_loc = os.path.join(output_csv_dir, os.path.basename(csv_path))
            print(f"Saving annotated file to {csv_loc}")
            df.to_csv(csv_loc, index=False)

            # TODO: move to a better way of storing contributor map
            mapping[os.path.basename(csv_path)[:-4]] = name.value or "Anonymous"
            with open(mapping_file, "w") as f:
                json.dump(mapping, f)
        else:
            # user didn't save annotated file, so add the file back to the list
            csv_paths.append(csv_path)

        # clear plot
        for model in models:
            model.renderers = []
            model.legend.items = []
        # load new data
        df, csv_path = rand_df_from_csv()
        if df is None:
            # hide everything except title
            for model in models:
                model.visible = False
            bsave.visible = False
            bundo.visible = False
            name.visible = False
            tutorial.visible = False
            loader.visible = False
            title.text = "All files have been annotated. Thank you for contributing"
            return

        plot_df(df, models)
        loader.visible = False

    # add listeners
    source.on_change("data", receive_box_data)
    bsave.js_on_click(
        CustomJS(
            args=dict(loader=loader, source=source),
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
                if (!window.boxes) {
                    window.boxes = []
                }
                loader.visible = true
                source.data = {
                    data: [false, Math.random()]
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
    tutorial.js_on_click(
        CustomJS(
            args=dict(),
            code="""
                window.open("https://youtu.be/N7PXKv16L4A", '_blank')
            """,
        )
    )

    def on_session_destroyed(session_context):
        csv_loc = os.path.join(output_csv_dir, os.path.basename(csv_path))
        if os.path.exists(csv_loc):
            return
        # user didn't save annotated file, so add the file back to the list
        csv_paths.append(csv_path)

    doc.add_root(
        column(
            column(
                row(
                    title,
                    loader,
                    name,
                    bundo,
                    bskip,
                    bsave,
                    sizing_mode="scale_width",
                    css_classes=["nav"],
                    stylesheets=[stylesheet],
                ),
                tutorial,
                *models,
                stylesheets=[stylesheet],
            ),
            sizing_mode="scale_width",
            styles={"align-items": "center"},
        )
    )
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
        li = Button(
            label=f"{name} (by {mapping.get(name, 'Anonymous')})",
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
