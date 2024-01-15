# South Park Clipper

South Park Clipper is a small Python / Flask application with the following features:

* Import transcripts from SRT files using the `spclipper/load_srt.py` script. The data is stored in the local sqlite3 `spclipper/tokens.db`.
* Search for a word in the transcripts and get an audio file containing the found words.

## Pre-requisites

* Tested with Python 3.11
* You have some audio files in one of the [formats supported by libsndfile](http://www.mega-nerd.com/libsndfile/#Features).
* You have some SRT files containing transcripts of those audio files.
* The audio files and the SRT files are in the same directory.
* Each pair of files (audio and SRT) have the same file name, except for the extension. For example:

    ```plain
    South.Park.S01E01.srt
    South.Park.S01E01.mp3
    South.Park.S01E02.srt
    South.Park.S01E02.mp3
    ```

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
    python spclipper/database_setup.py
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

1. Start the web server. Omit `--port` if you want.

    ```bash
    flask run --host 0.0.0.0 --port 8766
    ```

### Demo

https://github.com/dreness/spclipper/assets/5242016/25be8f04-2ed6-42f5-8e46-a4930fac0455

