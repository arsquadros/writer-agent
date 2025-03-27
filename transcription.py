import whisperx

import sys
import uuid

filepath = sys.argv[1]

model = whisperx.load_model("large-v2", "cpu", compute_type="int8", language="pt")

audio = whisperx.load_audio(filepath)
result = model.transcribe(audio, batch_size=16, language="pt")

transcript = ""
for segment in result["segments"]:
    transcript += f"{segment['text'].strip()} "
transcript += "\n"

print("Resultado da transcrição sem diarização:", transcript)

with open(f"{uuid.uuid4()}.txt", "w") as f:
    f.write(transcript)
    