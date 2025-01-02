# Annotate ULOG Files / PX4 Logs

## Features
- Multiclass labeling
- Visualization of former annotated logs
- Navigation within files using either file list or navigation buttons
- Down or up sample data to match measurement frequencies
- Clear button to remove all annotations in the current file
- Highlighted annotated files in the file list
- Note taking for each annotation

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

### Download log files:

Use the `./preprocessing/download_logs.py` script to download ulog files from PX4 flight review's
database. Download options are specified in the `./preprocessing/downloader_options.yaml` file.
Update the download parameters as desired and then run the following command:

   ```bash
   python3 preprocessing/download_logs.py
   ```

The above command will start downloading ulog files in the `./data/ulg_files` directory.

### Create database:

Once you have downloaded the ulog files, you need to convert them to csv files for the
application to serve the log files to users. Running the following command will convert
the ulog files into csv files and store them in the `./data/csv_files` directory.

   ```bash
   python3 preprocessing/ulog2csv.py
   ```

You can either run the script with the default options or specify the `--skip-processed` flag to skip files that have already been processed. If you use get_all_topics() function, you can convert all the topics and fields to from ulog file to csv, or you can specify the topics and fields you want to convert by using get_custom_topics() function.

### Run the server:

Now you are all set and you can run the server by issuing the following command,

   ```bash
   python3 server/app.py
   ```

All the annotated files will be stored in csv format in the `./data/annotated_csv_files`
directory.


## License

This project is licensed under the AGPL3 License. For details, see the [LICENSE](LICENSE) file.
