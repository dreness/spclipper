# South Park Clipper

South Park Clipper is a small Python / Flask application with the following features:

* Import transcripts from SRT files using the `spclipper/load_srt.py` script. The data is stored in the local sqlite3 `spclipper/tokens.db`.
* Search for a word in the transcripts and get an audio file containing the found words.

## Pre-requisites

* Tested with Python 3.11

## Installation

1. `cd` into the project directory.
1. Make a virtual environment:

    ```bash
    python3.11 -m venv --prompt spclipper venv
    ```

1. Activate the virtual environment:

    ```bash
    source venv/bin/activate
    ```

1. Install the requirements:

    ```bash
    pip install --ignore-installed -r requirements.txt
    ```

1. Create database

    ```bash
    python spclipper/database_setup.py.py
    ```

## Use

### Import transcripts

1. `cd` into the project directory.
1. Activate the virtual environment:

    ```bash
    source venv/bin/activate
    ```

1. Run the import script. You can pass more than one SRT file.

    ```bash
    python spclipper/load_srt.py /path/to/a/file.srt
    ```

### Start Web Server

1. `cd` into the project directory.
1. Activate the virtual environment:

    ```bash
    source venv/bin/activate
    ```

1. Start the web server. Omit `--port` or `--debug` if you want.

    ```bash
    flask run --host 0.0.0.0 --port 8766 --debug
    ```
