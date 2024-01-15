#!python3

from flask import Flask, request, send_file, render_template, \
    make_response, url_for, send_from_directory, jsonify
from sqlalchemy import create_engine, select, join, and_, func
from sqlalchemy.orm import sessionmaker
from spclipper.database_setup import engine, Token, TokenText, AudioFile
import os
from collections import namedtuple
from datetime import datetime, date, time, timedelta
import soundfile as sf
import numpy as np
from glob import glob

# Database setup
DATABASE_URL = "sqlite:///spclipper/tokens.db"  # Replace with your database URL
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# We'll describe audio clips in the form of a namedtuple
AudioClip = namedtuple("AudioClip", ["file_path", "start_time", "end_time", "text"])

# Flask app setup
app = Flask(__name__)

def audio_url_for_file(file_path):
    """
    Get the URL for an audio file.
    :param file_path: Path to the audio file.
    :return: URL for the audio file.
    """
    print(f"audio_url_for_file: file_path: {file_path}")
    return url_for('static', filename=os.path.join('audio', os.path.basename(file_path)))


def timestamp_to_frame_index(timestamp, sample_rate):
    """
    Convert a timestamp to a frame index in an audio file.

    :param timestamp: Timestamp in seconds.
    :param sample_rate: Sample rate of the audio file in Hz.
    :return: Frame index corresponding to the timestamp.
    """
    return int(timestamp * sample_rate)


def get_audio_clips(stmt):
    """
    Get the audio clips for a given query.
    param stmt (sqlalchemy.orm.query.Query): Query.
    return: List of audio clips as tuples
    """
    session = Session()
    audio_clips = []
    print(f"get_audio_clips: stmt: {stmt}")
    query = session.execute(stmt)
    for t, af in query:
        if af.finished_processing:
            # look for an audio file with the same file base name as the SRT file
            fpath = os.path.splitext(af.file_path)[0]
            files = glob(f"{fpath}.*")
            # remove any element from files that ends with ".srt"
            files = [f for f in files if not f.endswith(".srt")]
            # just take the first one I guess
            fp = files[0]
            ts_from_seconds = (datetime.combine(date.min, t.timestamp_from) - datetime.min).total_seconds()
            ts_to_seconds = (datetime.combine(date.min, t.timestamp_to) - datetime.min).total_seconds()
            start_frames = timestamp_to_frame_index(ts_from_seconds, 48000)
            end_frames = timestamp_to_frame_index(ts_to_seconds, 48000)    
            #print(f"get_audio_clips: fp: {fp}, t: {start_frames}, t: {end_frames}")
            if isinstance(t, Token):
                #print(f"token: {t}")
                txt = t.token_text.text
            ac = AudioClip(fp, start_frames, end_frames, txt)
            #print(f"appending AudioClip: {ac}")
            audio_clips.append(ac)
    print(f"got {len(audio_clips)} audio clips")
    session.close()
    return audio_clips


def get_audio_files_for_tokens(query, max_results=None, audio_file=None):
    """
    Get the audio files for a given list of words.
    param words (list): List of words.
    return: List of audio files.
    """
    session = Session()
    audio_files = []
    print(f"get_audio_files_for_tokens: query: {query}, audio_file: {audio_file}")

    # Query for the audio file path
    if audio_file is not None and audio_file != '':
        stmt = (
            select(Token, AudioFile)
            .join_from(Token, TokenText)
            .join_from(Token, AudioFile)
            .where(
                # TokenText.text case insensitive equals word
                (TokenText.text.ilike(query)) &
                (AudioFile.id == audio_file)) 
            .limit(max_results)
        )
    else:
        stmt = (
            select(Token, AudioFile)
            .join_from(Token, TokenText)
            .join_from(Token, AudioFile)
            .where((TokenText.text).ilike(query))
            .limit(max_results)
        )
    audio_files.extend(get_audio_clips(stmt))
    session.close()
    return audio_files


def concatenate_audio_files(audio_files):
    print("concatenate_audio_files")
    concatenated_audio = []
    for file_path, start_time, end_time, phrase_text in audio_files:
        # Load audio file and extract relevant segment
        data, samplerate = sf.read(file_path, start=start_time-150, stop=end_time+150)
        concatenated_audio.append(data)
    # Concatenate audio segments and store in a temporary file under the static directory
    final_audio = np.concatenate(concatenated_audio, axis=0)
    # make a unique output path to make sure clients notice changes
    now = datetime.now()
    output_path = f"static/audio/temp_concatenated_audio_{now.strftime('%Y%m%d%H%M%S%f')}.wav"
    sf.write(output_path, final_audio, samplerate)
    return output_path


@app.route("/audio", methods=["POST"])
def create_audio():
    """
    Create an audio clip by concatenating audio files of phrases containing the given string
    """
    print("create_audio route")
    query = request.form.get("query")
    # mode = request.form.get("mode")
    # print(f"mode: {mode}")
    if not query:
        return "No query provided", 400
    
    max_results = request.form.get("max_results", type=int)
    selected_file = request.form.get("audio_file_path")

    audio_files = get_audio_files_for_tokens(query, max_results, audio_file=selected_file)
    # # elif mode == 'word':
    #     words_list = query.split(" ")
    #     audio_files = get_audio_files_for_tokens(words_list, max_results, audio_file=selected_file)
    # else:
    #     return "No mode provided", 400
    text = ''
    for file_path, start_time, end_time, phrase_text in audio_files:
        text += f"{phrase_text}<br/>"
    if len(audio_files) == 0:
        return "\nNo audio files found", 200
    concatenated_file_path = concatenate_audio_files(audio_files)

    # Assuming you have a way to access the concatenated file via a URL
    audio_url = audio_url_for_file(concatenated_file_path)
    print(f"audio_url: {audio_url}")

    # Creating a response with the audio URL followed by the text
    response_text = audio_url + '\n' + text
    response = make_response(response_text)
    response.headers["Content-Type"] = "text/plain"
    return response



# @app.route("/audio", methods=["POST"])
# def create_audio():
#     """
#     Create an audio clip by concatenating audio files for a given list of words (tokens)
#     """
#     print("audio route")
#     words = request.form.get("words")
#     if not words:
#         return "No words provided", 400
#     max_results = request.form.get("max_results", type=int)
#     words_list = words.split(" ")
#     selected_file = request.form.get("audio_file_path")
#     print(f"type of selected_file: {type(selected_file)}")
#     audio_files = get_audio_files_for_tokens(words_list, max_results, audio_file=selected_file)
#     text = ''
#     for file_path, start_time, end_time, phrase_text in audio_files:
#         text += f"{phrase_text}<br>"
#     if len(audio_files) == 0:
#         return "\nNo audio files found", 200
#     concatenated_file_path = concatenate_audio_files(audio_files)

#     # Assuming you have a way to access the concatenated file via a URL
#     audio_url = audio_url_for_file(concatenated_file_path)
#     print(f"audio_url: {audio_url}")

#     # Creating a response with the audio URL followed by the text
#     response_text = audio_url + '\n' + text
#     response = make_response(response_text)
#     response.headers["Content-Type"] = "text/plain"
#     return response


@app.route('/audio_files', methods=['GET'])
def get_audio_files():
    session = Session()
    stmt = select(AudioFile).order_by(AudioFile.file_path)
    audio_files = session.scalars(stmt).all()
    
    #print(f"type of audio_files: {type(audio_files)}")
    audio_files_list = []
    for af in audio_files:
        # print(type(af))
        #print(f"type of audio_file: {type(audio_file)}")
        #print(dir(audio_file))
        # for id, file_path in audio_file.tuple():
        #     print(f"type of id: {type(id)}")
        #     print(f"type of file_path: {type(file_path)}")
        # Convert to a list of dictionaries
        audio_files_list.append({
            'id': af.id,
            'file_path': af.file_path
        })

    # Return the list as JSON
    return jsonify(audio_files_list)



@app.route("/")
def index():
        return render_template("index.html")


# allow loading CSS from the templates directory
@app.route("/templates/<path:path>")
def send_js(path):
    return send_from_directory("templates", path)



if __name__ == "__main__":
    app.run()
