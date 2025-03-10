

import sys
print(sys.executable)
import os
import tempfile
from pydub import AudioSegment
import speech_recognition as sr
import time
import moviepy as mp

class UniversalTranscriber:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
    def convert_to_wav(self, input_file_path):
        """
        Convert any audio/video file format to WAV format for speech recognition
        """
        print(f"Converting file to WAV format: {input_file_path}")
        filename, extension = os.path.splitext(input_file_path)
        extension = extension.lower()
        
        # Create a temp directory for intermediate files
        temp_dir = tempfile.mkdtemp()
        temp_wav_path = os.path.join(temp_dir, f"temp_audio_{int(time.time())}.wav")
        
        try:
            # For video files (mp4, avi, mov, etc.)
            if extension in ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']:
                print(f"Detected video file with extension {extension}")
                video = mp.VideoFileClip(input_file_path)
                audio = video.audio
                audio.write_audiofile(temp_wav_path, codec='pcm_s16le', verbose=False, logger=None)
                video.close()
            # For audio files (mp3, ogg, m4a, etc.)
            else:
                print(f"Detected audio file with extension {extension}")
                audio = AudioSegment.from_file(input_file_path)
                audio.export(temp_wav_path, format="wav")
                
            return temp_wav_path, temp_dir
            
        except Exception as e:
            print(f"Error converting file: {str(e)}")
            raise
    
    def segment_audio(self, wav_file_path, segment_length_ms=30000):
        """
        Split audio into manageable segments for better speech recognition
        """
        print(f"Segmenting audio file: {wav_file_path}")
        audio = AudioSegment.from_wav(wav_file_path)
        segments = []
        
        for i in range(0, len(audio), segment_length_ms):
            segment = audio[i:i + segment_length_ms]
            segments.append(segment)
            
        print(f"Audio split into {len(segments)} segments")
        return segments
    
    def transcribe_audio(self, audio_segments):
        """
        Perform speech-to-text on audio segments
        """
        print("Transcribing audio...")
        full_transcript = ""
        
        for i, segment in enumerate(audio_segments):
            print(f"Processing segment {i+1}/{len(audio_segments)}")
            # Create a unique temp filename
            temp_filename = f"temp_segment_{i}_{int(time.time())}.wav"
            temp_filepath = os.path.join(tempfile.gettempdir(), temp_filename)
            
            try:
                # Export segment to temp file
                segment.export(temp_filepath, format="wav")
                
                # Perform speech recognition
                with sr.AudioFile(temp_filepath) as source:
                    audio_data = self.recognizer.record(source)
                    try:
                        text = self.recognizer.recognize_google(audio_data)
                        full_transcript += text + " "
                    except sr.UnknownValueError:
                        print(f"Speech Recognition could not understand audio in segment {i+1}")
                    except sr.RequestError as e:
                        print(f"Could not request results for segment {i+1}; {e}")
            
            finally:
                # Clean up the temp file
                if os.path.exists(temp_filepath):
                    try:
                        os.remove(temp_filepath)
                    except:
                        pass
        
        print("Transcription complete")
        if not full_transcript.strip():
            print("Warning: No text was transcribed from the audio.")
            full_transcript = "No speech could be recognized in the provided audio/video file."
        
        return full_transcript
    
    def process_media_file(self, input_file_path):
        """
        Process any audio/video file and transcribe its content
        """
        print(f"Processing media file: {input_file_path}")
        
        try:
            # Step 1: Convert to WAV format (if needed)
            temp_wav_path, temp_dir = self.convert_to_wav(input_file_path)
            
            # Step 2: Segment audio
            audio_segments = self.segment_audio(temp_wav_path)
            
            # Step 3: Transcribe audio
            transcript = self.transcribe_audio(audio_segments)
            
            # Clean up the temporary directory
            try:
                if os.path.exists(temp_wav_path):
                    os.remove(temp_wav_path)
                os.rmdir(temp_dir)
            except:
                print("Warning: Could not remove some temporary files")
            
            return transcript
            
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            raise

# Example usage
if __name__ == "__main__":
    try:
        transcriber = UniversalTranscriber()
        
        # Input file path - can be any audio/video format
        input_file_path = "./data/ES2002a.Mix-Headset.wav"  # Replace with your file
        
        # Check if file exists
        if not os.path.exists(input_file_path):
            print(f"Error: The file {input_file_path} does not exist.")
            exit(1)
        else:
            print(f"Found media file: {input_file_path}")
            
            # Create output directory
            output_dir = "./output"
            os.makedirs(output_dir, exist_ok=True)
            
            # Process the file and get transcript
            transcript = transcriber.process_media_file(input_file_path)
            
            # Save the transcript to a file
            output_filename = os.path.splitext(os.path.basename(input_file_path))[0]
            with open(f"{output_dir}/{output_filename}_transcript.txt", "w", encoding="utf-8") as f:
                f.write(transcript)
            
            print(f"\nTranscript saved to {output_dir}/{output_filename}_transcript.txt")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # Create error log
        with open("error_log.txt", "w", encoding="utf-8") as f:
            f.write(f"Error: {str(e)}")
        print("Error details have been saved to error_log.txt")