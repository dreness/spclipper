#!python
# -*- coding: utf-8 -*-

import pysrt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Token, TokenText, AudioFile
from datetime import datetime, date
import sys
# import fileinput


# Configure SQLAlchemy
engine = create_engine('sqlite:///spclipper/tokens.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def srt_to_db(srt_file):
    path = srt_file

    # has the file been seen previously?
    file_seen = session.query(AudioFile).filter_by(file_path=path).first()

    # If file has been seen but metadata for the file is missing from the DB,
    # add it.
    if file_seen:
        print(f"File {path} has already been seen")
        # has the file been processed completely?
        if file_seen.finished_processing == 1:
            print(f"File {path} has already been processed")
            return
    # If the file has not been seen before, add it to the database
    else:
        print(f"Adding {path} to database")
        audio_file = AudioFile(
            file_path=path,
            finished_processing=False)
        session.add(audio_file)
        session.commit()

    af = session.query(AudioFile).filter_by(file_path=path).first()

    subs = pysrt.open(path)

    for sub in subs:
        # (datetime.combine(date.min, t.timestamp_from) - datetime.min).total_seconds()
        start = sub.start.to_time() # (datetime.combine(date.min, sub.start.to_time()) - datetime.min).total_seconds()
        end = sub.end.to_time()  # (datetime.combine(date.min, sub.end.to_time()) - datetime.min).total_seconds()
        text = sub.text.replace('\n', ' ')  # Replace newlines with spaces
        print(f"start: {start}, end: {end}, text: {text}")
        # Insert text into TokenText
        token_text = session.query(TokenText).filter_by(text=text).first()
        if not token_text:
            token_text = TokenText(text=text)
            session.add(token_text)
            session.commit()

        # # Assuming each subtitle is a separate phrase
        # transcribed_phrase = TranscribedPhrase(phrase=text)
        # session.add(transcribed_phrase)
        # session.commit()

        # Insert token data
        new_token = Token(
            token_text_id=token_text.id,
            timestamp_from=start,
            timestamp_to=end,
            audio_file=af,
        )
        session.add(new_token)

    af.finished_processing = True
    session.commit()


if __name__ == '__main__':
    for f in sys.argv[1:]:
        srt_to_db(f.strip())