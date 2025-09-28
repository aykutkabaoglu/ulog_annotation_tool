# Annotate ULOG Files / PX4 Logs

[![DOI](https://zenodo.org/badge/907262431.svg)](https://doi.org/10.5281/zenodo.17220628)


## Features
- Multiclass labeling
- Visualization of former annotated logs
- Navigation within files using either file list or navigation buttons
- Down or up sample data to match measurement frequencies
- Clear button to remove all annotations in the current file
- Highlighted annotated files in the file list
- Note taking for each annotation
- Keep folder hierarchy while creating csv files from the ulog files located under ulg_dir
- Use folder hierarchy while showing the file buttons on the file list panel

## Setup and Installation

### Create a virtual environment:

   ```bash
   python3 -m venv venv
   source ./venv/bin/activate
   ```

### Install dependencies:

   ```bash
   pip3 install -r requirements.txt
   ```

### Create database:

Put your ulg files under `./data/ulg_files`. Then, run ulog2csv script to convert ulg files to csv files under  `./data/csv_files`. 
You can download example dataset from [uav-flight-anomaly-dataset](https://huggingface.co/datasets/aykutkabaoglu/uav-flight-anomaly-dataset) with the annotations, put all the downloaded files under `./data` folder.

   ```bash
   python3 preprocessing/ulog2csv.py
   ```

You can either run the script with the default options or specify the `--skip-processed` flag to skip files that have already been processed. If you use get_all_topics() function, you can convert all the topics and fields to from ulog file to csv, or you can specify the topics and fields you want to convert by using get_custom_topics() function. The script uses synchronize_timeseries() function to subsample or upsample the ulg files to balance the number of rows of dataframes. You can disable it to store full-sized csv as same as ulg file.

### Run the server:

Now you are all set and you can run the server by issuing the following command,

   ```bash
   python3 server/app.py
   ```

All the annotated files will be stored in `mapping.json` file under `./data` folder. You can re-annotated the previos files and mapping.json file will be updated accordingly. It stores file names considering the folder hierarchy and timestamps of annotated windows. You can add multiple annotation into single file.

## License

This project is licensed under the AGPL3 License. For details, see the [LICENSE](LICENSE) file.
