import openai
from music21 import converter, stream, instrument, midi
import mido
openai.api_key = "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"

from flask import Flask, request, render_template
import re

app = Flask(__name__)
app.secret_key = "dev"


#straight to index.html
@app.route('/')
def index():

    return render_template('index.html')
    

@app.route('/music',methods=['GET', 'POST'])
def generate_abc():
    
    x=request.form.get("musicInput")
    style1, attitude, scene2, theme2 = x.split(",")
    instrument_names = ['Bass', "Violin", "Trumpet", "Piano", "Guitar"]
    messages = []
    system_message = "You are a %s musician, good at composing  %s music and writing lyrics.\
    When outputting, you only need to output the result without any polite language" % (style1,theme2)
    messages.append({"role": "system", "content": system_message})
    message = "Please help me generate a %s pure music for a %s scene \
                Note that the sheet music must be in ABC form.\
                Please do not output anything else, only ABC sheet music" % (attitude, scene2)
    messages.append({"role": "user", "content": message})

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, n=1, max_tokens=2048,)
    reply = response["choices"][0]["message"]["content"]

    start1 ='X:1'
    end1 = '```'

    try:
        score = reply.split(start1)[1].split(end1)[0]
        score = start1+score
        with open("static\Score\score.abc", "w") as f:
          f.write(score)
        abc_score = converter.parse(score)
        mf = midi.translate.music21ObjectToMidiFile(abc_score)
        s = midi.translate.midiFileToStream(mf)
        note = []
        for note_or_chord in s.flat.notesAndRests:
            note.append(note_or_chord)
        track_flag = 0
        for instrument_name in instrument_names:
            s = stream.Stream()
            instrument_class = getattr(instrument, instrument_name)
            my_instrument = instrument_class()
            s.append(my_instrument)
            for n in note:
                n.duration.quarterLength = 1.0
                s.append(n)
            s.write('midi', 'static\Mid\%s.mid' % instrument_name)
            s.write('mxl', 'static\Mxl\%s.mxl' % instrument_name)
            mid = mido.MidiFile('static\Mid\%s.mid' % instrument_name)
            if track_flag == 0:
                new_mid = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)
            for track in mid.tracks:
                new_mid.tracks.append(track)
            track_flag += 1
        new_mid.save('static\Merged.mid')
        return render_template('music.html',score=score,instrument_names=instrument_names)
    except:
        return render_template('error.html')







if __name__ == "__main__":
 
    app.run(host="0.0.0.0",debug=True)