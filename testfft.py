#!/usr/local/opt/python/libexec/bin/python
import audiotools
import eyed3
from zipfile import ZipFile
import shutil
import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import datetime
from colors import *
import sys
import subprocess
from pathlib import Path
import speech_recognition as sr
from os import path
from pydub import AudioSegment
import ffmpeg
from scipy.io.wavfile import read
from scipy.fftpack import fft, fftfreq, fftshift
from scipy.signal import get_window
from math import ceil
from pylab import figure, imshow, clf, gray, xlabel, ylabel


# Let's define some colours
black = lambda text: '\033[0;30m' + text + '\033[0m'
red = lambda text: '\033[0;31m' + text + '\033[0m'
green = lambda text: '\033[0;32m' + text + '\033[0m'
yellow = lambda text: '\033[0;33m' + text + '\033[0m'
blue = lambda text: '\033[0;36m' + text + '\033[0m'
magenta = lambda text: '\033[0;35m' + text + '\033[0m'
cyan = lambda text: '\033[0;36m' + text + '\033[0m'
white = lambda text: '\033[0;37m' + text + '\033[0m'
# Suppress warnings from eyeD3
eyed3.log.setLevel("ERROR")
# Get AJ Downloads folder from user input
userFolder = input("Drag your AJ downloads folder here and press enter...")
# create instance of speech_recognition
r = sr.Recognizer()

# Format the user input
tempVar = userFolder.replace("\\", "")
tempVar2 = tempVar.rstrip()
AJDownloadsFolder = os.path.abspath(tempVar2)
os.chdir(AJDownloadsFolder)
print("Downloads folder = " + AJDownloadsFolder)
print("")
print("Monitoring " + AJDownloadsFolder + "...")


# Set up a "clear" with cross platform compatibility with Windoze
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


# This is the function which does the evaluation
def detect():
    clear()
    print("")
    print("")

    os.chdir(AJDownloadsFolder)
    cwd = os.getcwd()

# Look for zip files and unzip then remove
    for directory, subdirectories, files in os.walk(cwd):
        for file in files:
            # print(file) Debugging output
            if file.endswith((".zip", ".ZIP")):

                currentZipFile = os.path.join(directory, file)
                zipFolderName = os.path.splitext(currentZipFile)[0]
                print(file)

                with ZipFile(currentZipFile, 'r') as zipArchive:
                    try:
                        zipArchive.extractall(zipFolderName)
                        print('Extracting...')
                        print('Done!')
                        print("")
                        os.remove(currentZipFile)
                    except Exception as e:
                        # print("zip file corrupt")
                        print("Zip already extracted?")
                        print(e)

                    hiddenFolder = (os.path.join(zipFolderName, "__MACOSX"))
                    if os.path.isdir(hiddenFolder):
                        try:
                            shutil.rmtree(hiddenFolder)
                            print("Found and removed __MACOSX hidden folder...")
                            # print("")
                        except:
                            print("unable to remove __MACOSX hidden folder...")

# Look for mp3 files and evaluate
    for directory, subdirectories, files in os.walk(cwd):
        for file in files:
            if file.endswith((".mp3", ".MP3", ".Mp3")) and not file.startswith("."):
                currentFile = os.path.join(directory, file)

                try:
                    mp3File = eyed3.load(currentFile)
                except:
                    mp3File = "Could not load MP3"
                try:
                    bitRate = mp3File.info.bit_rate
                except:
                    bitRate = ""
                try:
                    sampleRate = mp3File.info.sample_freq
                except:
                    sampleRate = "Samplerate Unsupported"
                try:
                    channels = str(mp3File.info.mode)
                    # print(channels)
                except:
                    channels = ""
                try:
                    durationSecs = mp3File.info.time_secs
                    duration = str(datetime.timedelta(seconds=durationSecs))

                except:
                    duration = "***"
                try:
                    bits = (audiotools.open(currentFile).bits_per_sample())
                except:

                    bits = "  "
                try:
                    if bitRate[0] is True:
                        vbrTrueFalse = "vbr"
                    else:
                        vbrTrueFalse = "cbr"
                except:
                    vbrTrueFalse = "***"

                ch = "   "

                # convert mp3 to wav for voice recognition
                # files
                src = currentFile
                dst = os.path.join(directory, "tempWav.wav")

                # convert wav to mp3
                sound = AudioSegment.from_mp3(src)# [10000:]
                sound.export(dst, format="wav")

                # Do watermark detection with voice recognition only on testWav.wav
                srVoiceTestWav = sr.AudioFile(dst)

                try:
                    with srVoiceTestWav as source:
                        audio = r.record(source, duration=12)
                        # print("Found the following speech in audio file...")
                        # print(r.recognize_google(audio))
                        recognisedSpeech = str((r.recognize_google(audio)))
                        if "audio" in recognisedSpeech:
                            ch = red("WM")
                            wm = "wmd"
                        else:
                            ch = "  "

                        if "jungle" in recognisedSpeech:
                            ch = red("WM")
                            wm = "wmd"
                        else:
                            ch = "  "


                except Exception as e:
                    # print(e)
                    # print("No watermark detected in " + file)
                    ch = "  "
                    wm = "nowm"

                if os.path.exists(dst):
                    # clean up temp file
                    os.remove(dst)


                if channels == "Joint stereo" or "Stereo" or "stereo" or "Joint Stereo":
                    channels = 2
                try:
                    rate = int(bitRate[1])
                except:
                    rate = "err"

                vbrTrueFalse = "  "



                if sampleRate == 44100 and channels == 2 and rate < 325 and rate > 315: #  and wm != "wmd":
                    errorMp3 = green(" [ok]")
                else:
                    errorMp3 = red("[ERR]")



                print(errorMp3, sampleRate, bits, channels, ch, vbrTrueFalse, rate, duration[3:], file)

# Look for wav files and evaluate
            if file.endswith((".wav", ".WAV", ".WaV", ".wAV", ".WAv", ".Wav")) and not file.startswith("."):

                currentFile = os.path.join(directory, file)
                try:
                    sampleRate = (audiotools.open(currentFile).sample_rate())
                    ch = "ch"
                    gap = "       "
                except:
                    sampleRate = "BitDepth Unsupported"
                    gap = ""
                    ch = ""
                try:
                    bits = (audiotools.open(currentFile).bits_per_sample())
                except:
                    bits = ""
                try:
                    channels = int(audiotools.open(currentFile).channels())
                except:
                    channels = ""

                try:
                    home = str(Path.home())
                    LACpath = os.path.join(home, "LAC")
                    a = [LACpath, currentFile]

                    p = subprocess.Popen(a, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
                    p2 = subprocess.Popen(['grep', 'Result'], stdin=p.stdout,
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    sys.stdout.flush()
                    for line in iter(p2.stdout.readline, b''):
                        LACout = str(line)

                except Exception as ex:
                    print("crap!")
                    print(ex)
                    LACout = ''
                try:
                    durationSecsWav = int(audiotools.open(currentFile).seconds_length())
                    duration = str(datetime.timedelta(seconds=durationSecsWav))
                except:
                    duration = "****"

                ch = "   "

                srVoiceTestWav = sr.AudioFile(currentFile)
                try:
                    with srVoiceTestWav as source:
                        audio = r.record(source, duration=12)
                        # print(r.recognize_google(audio))
                        recognisedSpeech = str((r.recognize_google(audio)))

                        # if "audio" or "jungle" or "audiojungle" in recognisedSpeech:

                        if "audio" in recognisedSpeech:

                            ch = red("WM")
                            wm = "wmd"
                        else:
                            ch = "  "

                        if "jungle" in recognisedSpeech:

                            ch = red("WM")
                            wm = "wmd"
                        else:
                            ch = "  "
                except Exception as e:
                    # print(e)
                    # print("No watermark detected in " + file)
                    ch = "  "
                    wm = "nowm"

                # Read in a wav file
                #   returns sample rate (samples / sec) and data
                rate, data = read(currentFile)

                # Define the sample spacing and window size.
                dT = 1.0 / rate
                T_window = 50e-3
                N_window = int(T_window * rate)
                N_data = len(data)

                # 1. Get the window profile
                window = get_window('hamming', N_window)

                # 2. Set up the FFT
                result = []
                start = 0
                while (start < N_data - N_window):
                    end = start + N_window
                    result.append(fftshift(fft(window * data[start:end])))
                    start = end

                result.append(fftshift(fft(window * data[-N_window:])))
                result = array(result, result[0].dtype)

                # Display results
                freqscale = fftshift(fftfreq(N_window, dT))[150:-150] / 1e3
                figure(1)
                clf()
                imshow(abs(result[:, 150:-150]),
                       extent=(freqscale[-1], freqscale[0], (N_data * dT - T_window / 2.0), T_window / 2.0))
                xlabel('Frequency (kHz)')
                ylabel('Time (sec.)')
                gray()

                if sampleRate == 44100 and bits == 16 and channels == 2: # and wm !="wmd":
                    errorWav = green(" [ok]")

                else:
                    errorWav = red("[ERR]")

                if "Result: Upsampled" in LACout:
                    gap = yellow("Upsamp")
                if "Result: Upscaled" in LACout:
                    gap = yellow("Upscal")
                if "Result: Transcoded" in LACout:
                    gap = yellow("Transc")
                if "Result: Clean" in LACout:
                    gap = blue(" Clean")
                # gap = LACout



                print(errorWav, sampleRate, bits, channels, ch, gap, duration[3:], file)
# If any other audio file types are present mark as [ERR]
            if file.endswith((".aac", ".aiff", ".aif", ".flac", ".m4a", ".m4p")):

                currentFile = os.path.join(directory, file)
                try:
                    sampleRate = (audiotools.open(currentFile).sample_rate())
                except:
                    sampleRate = "Bitdepth Unsupported"
                try:
                    bits = (audiotools.open(currentFile).bits_per_sample())
                except:
                    bits = " "
                try:
                    channels = int(audiotools.open(currentFile).channels())
                except:
                    channels = " "

                errorWav = red("[ERR]")
                ch = ""

                print(errorWav, sampleRate, bits, channels, ch, "         ", file)

# Watch folder and run main function when a file is downloaded into folder
class Event(LoggingEventHandler):
    def on_moved(self, event):
        print('\n' * 50)
        detect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = Event()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

