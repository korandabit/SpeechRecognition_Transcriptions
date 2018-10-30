import speech_recognition as sr
import os
import time


"""

Introduction:
This is a basic script that will read audio files in a directory,
record them to memory, transcribe them using Google Cloud Speech,
and record them to an output file.

This script uses a package called SpeechRecognition to access Google Cloud Speech's
API.


The below instructions below in this file should be sufficient for installation,
but here are some references:

Basic Walkthrough: https://realpython.com/python-speech-recognition/
Tools for SpeechRecognition package: https://github.com/Uberi/speech_recognition/blob/master/reference/library-reference.rst
Reference: https://pypi.org/project/SpeechRecognition/


INSTALLATIONS:
	pip install SpeechRecognition
	pip install --upgrade google-cloud-speech
	pip install --upgrade gcloud
	pip install --upgrade google-api-python-client
	pip install google-cloud-storage

GOOGLE CLOUD:
	-Create Google Cloud Account
	-Enable Google speech API in your Google Cloud Acct
	-Create service account key in (this will permit you to save 
		your credentials as a .json file - you need this file)
	-Note the directory and filename of the credentials file
	
PROVIDE CREDENTIALS:
	-Get the path and filename of your credentials from the prior step.
	-Enter that as one string in the first line of this script to provide your credentials:

	CREDENTIALS_PATH="ENTER CREDENTIALS PATH HERE.json"


Using the script:
	-Place audio files for transcription in the same directory as this script(main folder)
	-Run this script
	-Transcriptions will be placed in the Transcriptions folder

"""

#Set environment variable to tell google where to find your credentials:
CREDENTIALS_PATH="~/GoogleSpeech_Credentials.json"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=CREDENTIALS_PATH

#Set MODE to "regular" to use your own credentials
# or to "demo" to test the installation (50 queries/day) with "demo"
MODE="demo" 
if MODE=="demo":
	print "Using Demo Mode. To run transcriptions on your account, provide Google Cloud credentials and change MODE to 'regular'"

cwd=os.getcwd()

INPUT_FOLDER=cwd #folder for audio input
OUTPUT_FOLDER=cwd+'/Transcriptions'
filetime=time.strftime("%m.%d.%Y-%H.%M.%S")
OUTPUT_FILE_NAME="Filename_"+filetime

r=sr.Recognizer()

#Creates a list of audio files for transcription
dirList=os.listdir(INPUT_FOLDER) #look for filetype
audioFileList=[]
for item in dirList:
	if item.endswith('.wav'):
		audioFileList.append(item)

#This loop cycles through each .wav filename in the current directory
#records the audio file to memory, sends that audio for transcription
#and then writes it to a .csv with each transcription on a new line, 
#formatted: audio-filename, transcription
#			audio-filename, transcription
for item in audioFileList:
	
	outputFile=open(OUTPUT_FOLDER+"/"+OUTPUT_FILE_NAME+"_output.csv", "a") #open output file

	currFile=sr.AudioFile(item)

	with currFile as source:
		audio = r.record(source) #record current file to memory
	if MODE=="demo":
		output=r.recognize_google(audio) #send to Google for transcription
		outputToFile=item+', '+output+'\n' 
		print outputToFile
	
	else:
		output=r.recognize_google_cloud(audio) #send to Google for transcription
		outputToFile=item+', '+output+'\n' 
		print outputToFile
	
	outputFile.write(outputToFile)

print "done"