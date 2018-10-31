import os
import sys
import pandas
import speech_recognition as sr
from pathlib import Path # Requires Python 3

# from google.cloud import speech
# from google.cloud.speech import enums
# from google.cloud.speech import types

def setAccountInfo(account_info = 'koranda.json',
				   verbose = True):
	"""
	Sets up account info to use Google Speech Recognition API
	+ account_info: Path to the .json file containing account information
	"""
	if verbose:
		print('Setting account information to {}'.format(account_info))
	if account_info != None:
		try:
			assert os.path.isfile(account_info)
			os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = account_info
		except:
			print('\tAccount information not found. Aborting program.')
			sys.exit()
	else:
		if verbose:
			print('\tNo account information provided. Defaulting to demo.')

def getFiles(directory,
			 extension = '.wav',
			 ignore_key = 'Practice',
			 need_key = None,
			 verbose = False):
	"""
	Takes a directory of folder containing files and returns a list of the files that meet specific requirement
	+ directory: Folder containing the files
	+ extension: File extension for the audio files
	+ ignore_key: Which files to ignore (i.e. how to identify practice audio files)
	+ need_key: Files must contain this string (i.e. how to identify file of presented words)
	"""
	if verbose:
		print('\tGetting files from {}'.format(directory))
	folder = Path(directory)
	files = directory.glob('*' + extension)
	if ignore_key != None:
		files = [file for file in files if ignore_key not in file.stem]
	if need_key != None:
		files = [file for file in files if need_key in file.stem]
	return files


									
def getParticipants(participant_directory,
					target_file_extension = '.wav',
					data_key = None,
					data_extension = '.txt',
					verbose = False):
	"""
	Takes a directory of participants and returns the target files for each participant in a dictionary
	+ participant_directory: Folder containing child folders for each participant
	+ target_file_extension: The main file type being extracted (i.e. .wav files)
	+ data_key: The string used to identify the data file for the participant if it has already been created
	+ data_extension: The file type of the data file being extracted (i.e. .csv)
	"""
	if verbose:
		print('Getting participants and their audio files')
	participant_files = {}
	data_files = {}
	# participants = [participant for participant in participant_directory.glob('*') if participant.is_dir()]
	participants = [participant for participant in os.listdir(participant_directory)]
	for participant in participants:
		participant_files[participant] = getFiles(directory = Path(participant_directory)+participant,
													   extension = target_file_extension,
													   verbose = verbose)
		if data_key != None:
			assert data_extension
			data_files[participant] = getFiles(directory = Path(participant),
											   extension = data_extension,
											   ignore_key = None,
											   need_key = data_key)
			data_files[participant] = data_files[participant]
		else:
			data_files[participant] = None
	print(participant_files)

	return participant_files, data_files


# main horse
def wav_lumps(list_of_wavs):
	"""
	intended use: combine audio files from given participant, 
	keep track of original audio boundaries in combined file.
	
	input: list of wav files
	output: 
	- combined wav file, 
	- list of (start_time,end_time) for the wavs in the combined file.
	"""

	cat_duration  = 0
	clip_start = 0
	clip_end = 0
	cat_wav_arrays = []
	cat_wav_time_boundaries = []	
	cat_wav_list = []
	
	for cur_wav in participant_audio_files:
			
		cur_wav_path = participant_directory + participant + cur_wav
		
		samplerate, wav_array = wavfile.read(cur_wav_path) 
		cat_wav_arrays.append(wav_array) # 
		
		# timing updates
		clip_start = cat_duration
		clip_duration = len(wav_array)/samplerate
		# print(clip_duration)
		cat_duration += clip_duration
		clip_end = cat_duration
		# print((clip_start,clip_end))
		cat_wav_time_boundaries.append((clip_start,clip_end))
		# print(cat_wav_time_boundaries)

	# combine all audio files.
	stacked_wav = np.hstack(cat_wav_arrays)
	compiled_wav = wavfile.write('last{}.wav'.format(cur_wav),samplerate,stacked_wav)

	return(compiled_wav,cat_wav_time_boundaries)

				
def getTranscription(audio_file,
					 recognizer,
					 account_info = None):
	# modify this to return timestamps.
	
	"""
	Takes an audio file and a 'recognizer' object and returns the transcription
	+ audio_file: path to the audio file
	+ recognizer: recognizer object through the sppech_recognition API
	+ accountInfo: Its existence indicate whether or not to use demo credentials
	"""
	with sr.AudioFile(audio_file) as source:
		audio = recognizer.record(source)
	# Querying free uses
	if account_info == None:
		output = recognizer.recognize_google(audio)
	# Querying through account -- payment required
	else:
		output = recognizer.recognize_google_cloud(audio)
	return output

def transcribe(participant_files,
			   account_info,
			   verbose = True):
	"""
	Input: list of audio files
	Returns transcriptions from audio files. 
	+ participant_files: Input dictionary
	+ account_info: Information about the account. None if using demo
	"""
	if verbose:
		print('Getting transcriptions')
	recognizer = sr.Recognizer()

	for file in participant_files:
			transcriptions	= getTranscription(audio_file = file,
												recognizer = recognizer,
												account_info = account_info,
												# add_new_parameters (see end of script)
												)
																				
	return transcriptions

def saveTranscriptions(transcriptions, data_files,
					   new_file_name = 'Transcription',
					   extension = '.csv',
					   verbose = True):
	"""
	Save transcriptions to either existing files or new files
	+ transcriptions: Dictionary of participants containing dictionary of transcription file keys and transcription values
	+ data_files: Which files to save to. Files of None default to a new 'Transcription' file in participant's folder
	+ extension: Extension of file type (i.e. .csv)
	"""
	if verbose:
		print('Saving transcriptions')
	for participant in transcriptions:
		if data_files[participant] == None:
			transcribeNewFile(participant = Path(participant),
							  transcriptions_participant = transcriptions[participant],
							  verbose = verbose)
		else:
			transcribeToFile_SRSyn(participant = Path(participant),
								   transcriptions_participant = transcriptions[participant],
								   file_out = data_files[participant],
								   verbose = verbose)

def transcribeNewFile(participant, transcriptions_participant, 
					  new_file_name = 'Transcription', 
					  extension = '.csv',
					  header = ['participant', 'file', 'transcription'],
					  verbose = False):
	"""
	Creates new file for transcriptions
	+ participant: Identifies participant
	+ transcriptions_participant: Dictionary of transcriptions for each participant
	+ new_file_name: Name of new file for the participant containing the transcriptions
	+ extension: filetype of output
	"""
	file_out = participant / ('Transcription' + extension)
	if verbose:
		print('\tTranscribing {} in new file {}'.format(participant.stem, file_out.stem))
	with file_out.open('w') as f:
		f.write(','.join(header))
		f.write('\n')
		for file in transcriptions_participant:
			f.write('{},{},{}\n'.format(participant.stem, file, transcriptions_participant[file]))

def transcribeToFile_SRSyn(participant, transcriptions_participant, file_out,
						   newDir = 'Data/Transcribed',
						   trial_column = 'trialNum',
						   transcription_column = 'recall',
					  	   verbose = False):
	"""
	Outputs to an existing data file, appending to a new column
	+ participant: Identifies participant
	+ transcription_participant: Dictionary of transcriptions for each participant
	+ file_out: The file to which the transcription will be appended
	+ trial_column: Name of the column containing trial number information
	+ transcription_column: Name of the new column to which the transcription will be appended
	"""
	if verbose:
		print('\tTranscribing {} in old file {}'.format(participant.stem, file_out.stem))
	df = pandas.read_csv(str(file_out))
	data = {trial_column:[],
			transcription_column:[]}
	for file in transcriptions_participant:
		data[trial_column].append(file.stem.split('_')[-1][1:]) # Trial number pulled from name of audio file
		data[transcription_column].append(transcriptions_participant[file])
	new_df = pandas.DataFrame(data)
	output = pandas.merge(df, new_df, on = trial_column, how = 'outer')
	if newDir == None:
		output.to_csv(str(file_out), index_label = False, index = False)
	else:
		output.to_csv(str(Path.cwd() / newDir / file_out.name), index_label = False, index = False)

if __name__ == '__main__':
	# Setting up
	verbose = True
	participant_directory = 'participants/'
	participant_directory = Path(Path.cwd() / participant_directory)
	#account_info = '/Users/StevenSchwering/GoogleSpeech_Credentials.json'
	account_info = None
	data_key = 'PresentedTrials'
	# Starting
	setAccountInfo(account_info = account_info,
				   verbose = verbose)
	participant_files, data_files = getParticipants(participant_directory = participant_directory,
													target_file_extension = '.wav',
													data_key = data_key,
													data_extension = '.csv',
													verbose = verbose)
	compiled_wav,cat_wav_time_boundaries = wav_lumps(participant_files)
	transcriptions = transcribe(participant_files = [compiled_wav],
								account_info = account_info,
								verbose = verbose)
	saveTranscriptions(transcriptions = transcriptions,
					   data_files = data_files) # add cat_wav_time_boundaries here

# def transcribe_gcs_with_word_time_offsets(gcs_uri):
    # """Transcribe the given audio file asynchronously and output the word time
    # offsets."""
    # from google.cloud import speech
    # from google.cloud.speech import enums
    # from google.cloud.speech import types
    # client = speech.SpeechClient()

    # audio = types.RecognitionAudio(uri=gcs_uri)
    # config = types.RecognitionConfig(
        # encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
        # sample_rate_hertz=16000,
        # language_code='en-US',
        # enable_word_time_offsets=True)

    # operation = client.long_running_recognize(config, audio)

    # print('Waiting for operation to complete...')
    # result = operation.result(timeout=90)

    # for result in result.results:
        # alternative = result.alternatives[0]
        # print(u'Transcript: {}'.format(alternative.transcript))
        # print('Confidence: {}'.format(alternative.confidence))

        # for word_info in alternative.words:
            # word = word_info.word
            # start_time = word_info.start_time
            # end_time = word_info.end_time
            # print('Word: {}, start_time: {}, end_time: {}'.format(
                # word,
                # start_time.seconds + start_time.nanos * 1e-9,
                # end_time.seconds + end_time.nanos * 1e-9))