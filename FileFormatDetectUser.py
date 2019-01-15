#!/usr/local/opt/python/libexec/bin/python
import audiotools
import eyed3
from zipfile import ZipFile
import shutil
import sys
import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

eyed3.log.setLevel("ERROR")

userFolder = input("Drag your AJ downloads folder here and press enter...")
tempVar = userFolder.replace("\\", "")
tempVar2 = tempVar.rstrip()
AJDownloadsFolder = os.path.abspath(tempVar2)
os.chdir(AJDownloadsFolder)
print("Downloads folder = " + AJDownloadsFolder)
print("")
print("Monitoring " + AJDownloadsFolder + "...")


def detect():

    print("")
    print("")

    os.chdir(AJDownloadsFolder)
    cwd = os.getcwd()

    for directory, subdirectories, files in os.walk(cwd):
        for file in files:
            # print(file) Debugging output
            if file.endswith((".zip", ".ZIP")):

                currentZipFile = os.path.join(directory, file)
                zipFolderName = os.path.splitext(currentZipFile)[0]

                print(file)

                with ZipFile(currentZipFile, 'r') as zipArchive:

                    # printing all the contents of the zip file
                    # zipArchive.printdir()
                    # extracting all the files
                    try:
                        zipArchive.extractall(zipFolderName)
                        print('Extracting...')
                        # print('Done!')
                        print("")
                        os.remove(currentZipFile)
                    except:
                        # print("zip file corrupt")
                        print("Zip already extracted")

                    hiddenFolder = (os.path.join(zipFolderName, "__MACOSX"))
                    if os.path.isdir(hiddenFolder):
                        try:
                            shutil.rmtree(hiddenFolder)
                            print("Found and removed __MACOSX hidden folder...")
                            # print("")
                        except:
                            print("unable to remove __MACOSX hidden folder...")

    for directory, subdirectories, files in os.walk(cwd):
        for file in files:
            if file.endswith((".mp3", ".MP3", "Mp3")):
                currentFile = os.path.join(directory, file)
                try:
                    sampleRate = (audiotools.open(currentFile).sample_rate())
                    bits = (audiotools.open(currentFile).bits_per_sample())
                    channels = int(audiotools.open(currentFile).channels())

                    mp3File = eyed3.load(currentFile)
                    bitRate = mp3File.info.bit_rate

                    if bitRate[0] is True:
                        vbrTrueFalse = "vbr"
                    else:
                        vbrTrueFalse = "cbr"

                    errorMp3 = " [ok]  "
                    if sampleRate != 44100 or bits != 16 or channels != 2 or vbrTrueFalse != "cbr" or bitRate[1] != 320:
                        errorMp3 = "[ERROR]"
                    print(errorMp3, sampleRate, bits, channels, "ch", vbrTrueFalse, bitRate[1], file)
                except:

                    print("                              " + file + " >>switching to eyeD3")

                    mp3File = eyed3.load(currentFile)
                    try:
                        bitRate = mp3File.info.bit_rate
                    except:
                        bitRate = ""
                    try:
                        sampleRate = mp3File.info.sample_freq
                    except:
                        sampleRate = "samplerate unsupported "
                    try:
                        channels = mp3File.info.mode
                    except:
                        channels = ""

                    bits = "  "
                    vbrTrueFalse = ''

                    if bitRate[0] is True:
                        vbrTrueFalse = "vbr"
                    else:
                        vbrTrueFalse = "cbr"
                    if channels == "Joint stereo":
                        channels = 2

                    if sampleRate == 44100 and channels == 2 and vbrTrueFalse == "cbr" and bitRate[1] == 320:
                        errorMp3 = " [ok]  "
                    else:
                        errorMp3 = "[ERROR]"

                    print(errorMp3, sampleRate, bits, channels, "ch", vbrTrueFalse, bitRate[1], file)

            if file.endswith((".wav", ".WAV", "WaV", "wAV", "WAv", "Wav")):

                currentFile = os.path.join(directory, file)
                try:
                    sampleRate = (audiotools.open(currentFile).sample_rate())
                    ch = "ch"
                    gap = "       "
                except:
                    sampleRate = "samplerate unsupported"
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

                if sampleRate == 44100 and bits == 16 and channels == 2:
                    errorWav = " [ok]  "


                else:
                    errorWav = "[ERROR]"


                print(errorWav, sampleRate, bits, channels, ch, gap, file)

            if file.endswith((".aac", ".aiff", "aif", "flac", "m4a", "m4p")):

                currentFile = os.path.join(directory, file)
                try:
                    sampleRate = (audiotools.open(currentFile).sample_rate())
                except:
                    sampleRate = "samplerate unsupported "
                try:
                    bits = (audiotools.open(currentFile).bits_per_sample())
                except:
                    bits = " "
                try:
                    channels = int(audiotools.open(currentFile).channels())
                except:
                    channels = " "

                # if sampleRate == 44100 and bits == 16 and channels == 2:
                #     errorWav = " [ok]  "
                #     ch = "ch"
                # else:
                errorWav = "[ERROR]"
                ch = ""

                print(errorWav, sampleRate, bits, channels, ch, "         ", file)
    # return

#detect()


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
            # print("process running")
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































