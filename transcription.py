import whisperx
import pydantic

from dotenv import load_dotenv
import uuid

import sys
import os

load_dotenv()

filepath = sys.argv[1]

WHISPERX_MODEL = "large-v2"
DEVICE = "cpu"
COMPUTE_TYPE = "int8"
BATCH_SIZE = 16
LANGUAGE = "pt"

class TranscriptionIntermediateRequest(pydantic.BaseModel):
    """
    A class to represent an intermediate transcription request. Includes diarization and speaker identification assigning ID's.
    hf_key is the Hugging Face API key to be used for transcription.

    Attributes:
        filepath (str): The path to the audio file to be transcribed.
        hf_key (str): The Hugging Face API key to be used for transcription.
    """
    
    filepath: pydantic.FilePath
    hf_key: pydantic.SecretStr

    @staticmethod
    def __transcript_by_segments(segments) -> str:
        """
        Generates a transcript from a list of dialogue segments.
        This function takes a list of dialogue segments and formats them into a transcript, preserving speaker turns and segment breaks.

        Args:
            segments (list): A list of dictionaries representing dialogue segments. 
                            Each dictionary should have the following keys:
                            - 'speaker' (str): The name of the speaker for the segment.
                            - 'text' (str): The text spoken in the segment.

        Returns:
            str: The formatted transcript text.
        """
        transcript = ""
        last_speaker = None
        
        for segment in segments:
            if last_speaker is None:
                transcript += f"*{segment['speaker']}:* \"{segment['text'].strip()}"
            elif last_speaker != segment['speaker']:
                transcript += f"\"\n*{segment['speaker']}:* \"{segment['text'].strip()}"
            else:
                transcript += f" {segment['text'].strip()}"
            last_speaker = segment['speaker']
        
        transcript += "\"\n"

        return transcript

    
    @staticmethod
    def __speaker_segments(segments, verbose: bool = False) -> dict:
        """
        This function takes a list of dialogue segments and identifies the speaker segments based on the speaker turns.

        Args:
            segments (list): A list of dictionaries representing dialogue segments. 
                            Each dictionary should have the following keys:
                            - 'speaker' (str): The name of the speaker for the segment.
                            - 'text' (str): The text spoken in the segment.
                            - 'start' (float): The start time of the segment in seconds.
                            - 'end' (float): The end time of the segment in seconds.
        
        Returns:
            dict: A dictionary mapping speaker names to segment intervals. The segment intervals can be either
            a single tuple (start, end) or a list of tuples [(start1, end1), (start2, end2), ...], 
            or None, if not identified enough audio samples for at least 5 seconds of audio.
            The time intervals are in seconds.
        """
        _MIN_DURATION = 5
        _IDEAL_DURATION = 10
        _MAX_DURATION = 15

        unique_speakers = set([segment['speaker'] for segment in segments])

        pairs = {}
        for segment in segments:
            start = segment['start']
            end = segment['end']

            if segment['speaker'] not in pairs:
                if end - start < _MIN_DURATION:
                    if verbose:
                        print(f"Segment too short: {segment['text']}")  # print the segment text if it's too short
                    continue
                elif end - start < _IDEAL_DURATION:
                    interval = (start, end)
                elif end - start > _MAX_DURATION:
                    interval = (start, start + _MAX_DURATION)
                else:
                    interval = (start, start + _IDEAL_DURATION)
                pairs[segment['speaker']] = interval

        if len(pairs) != len(unique_speakers):
            if verbose:
                print("Warning: Some speakers were not identified. Combining segments...")
            combined_segments = {}
            for segment in segments:
                if segment['speaker'] not in combined_segments:
                    combined_segments[segment['speaker']] = []
                combined_segments[segment['speaker']].append((segment['start'], segment['end']))

            for speaker in combined_segments:
                if speaker not in pairs:
                    # sum the total duration of all segments for the speaker
                    total_duration = sum([end - start for start, end in combined_segments[speaker]])
                    if total_duration < _MIN_DURATION:
                        if verbose:
                            print(f"Total duration too short for speaker {speaker}. Defining as None and skipping.")
                        pairs[speaker] = None
                    else:
                        # get all necessary segments for a total duration of at most 5 seconds
                        intervals = []
                        for start, end in combined_segments[speaker]:
                            if sum([e - s for s, e in intervals]) >= _IDEAL_DURATION:
                                break
                            else:
                                intervals.append((start, end))
                        pairs[speaker] = intervals
            
            # check if there are still speakers that were not identified and are None
            for speaker in pairs:
                if pairs[speaker] is None:
                    if verbose:
                        print(f"Speaker {speaker} was not identified.")
                elif type(pairs[speaker]) == list:
                    if verbose:
                        print(f"Speaker {speaker} was identified with multiple segments.")
                elif verbose:
                    print(f"Speaker {speaker} was identified with a single segment.")
        
        if verbose:
            for speaker in pairs:
                print(f"Speaker '{speaker}' was identified with {int(len(pairs[speaker]) / 2)} segment(s).")
        return pairs

    @staticmethod
    def __map_segments(pairs: dict) -> dict:
        """
        Maps speaker segments transforming the time intervals from seconds to miliseconds.

        Args:
            pairs (dict): A dictionary mapping speaker names to segment intervals. The segment intervals can be either
            a single tuple (start, end) or a list of tuples [(start1, end1), (start2, end2), ...], 
            or None, if not identified enough audio samples for at least 5 seconds of audio.
            The time intervals are in seconds.

        Returns:
            dict: A dictionary mapping speaker names to segment intervals. The segment intervals are in miliseconds.
        """
        mapped_segments = {}
        for pair in pairs:
            if pair not in mapped_segments:
                mapped_intervals = None
                if pairs[pair] is not None and type(pairs[pair]) == list:
                    mapped_intervals = [(start * 1000, end * 1000) for start, end in pairs[pair]]
                elif pairs[pair] is not None:
                    mapped_intervals = [(pairs[pair][0] * 1000, pairs[pair][1] * 1000)]
                mapped_segments[pair] = mapped_intervals
        return mapped_segments

    def get_intermediate_transcription(self) -> str:
        """
        Transcribes and diarizes an audio file, returning dialogue segments and speaker turns for the user to identify.
        Passing the speaker turns to the user is a way to help the user identify the speakers in the audio file.
        After the user identifies the speakers, their names can be set in the speaker segments.

        Returns:
            tuple: A tuple containing the transcript (str) and the speaker segments (dict[id, segments]).
        
        Raises:
            FileNotFoundError: If the audio file is not found.
            ValueError: If the model is invalid or the API key is missing.
            Exception: If an error occurs during transcription or diarization.
        """

        model = whisperx.load_model(WHISPERX_MODEL, DEVICE, compute_type=COMPUTE_TYPE, language=LANGUAGE)

        audio = whisperx.load_audio(self.filepath)
        result = model.transcribe(audio, batch_size=BATCH_SIZE, language=LANGUAGE)
        
        model_a, metadata = whisperx.load_align_model(language_code=LANGUAGE, device=DEVICE)
        result = whisperx.align(result["segments"], model_a, metadata, audio, DEVICE, return_char_alignments=False)
        
        diarize_model = whisperx.DiarizationPipeline(use_auth_token=self.hf_key.get_secret_value(), device=DEVICE)
        diarize_segments = diarize_model(audio)

        result = whisperx.assign_word_speakers(diarize_segments, result)
    
        pairs = TranscriptionIntermediateRequest.__map_segments(
                    TranscriptionIntermediateRequest.__speaker_segments(
                        result["segments"]))
    
        transcript = TranscriptionIntermediateRequest.__transcript_by_segments(result["segments"])
    
        word_level_diarization = result

        return transcript, pairs, word_level_diarization

hf_key = os.getenv("HF_KEY")

print("get_intermediate_transcription:")

transcript, _, _ = TranscriptionIntermediateRequest(filepath=filepath, hf_key=hf_key).get_intermediate_transcription()

print(transcript)

with open(f"transcription_results/{uuid.uuid4()}.txt", "w") as f:
    f.write(transcript)