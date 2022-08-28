#!/usr/bin/env python3
from threading import TIMEOUT_MAX
import rospy
from sound_recognition.msg import SpeechData
from std_msgs.msg import Int16MultiArray, String
from optparse import OptionParser

from ros_vad import SpeechRecognitionVAD
from speech_recognition import Microphone
from voice_activity_detection import ROSMicrophoneSource

import numpy as np
from time import sleep
import soundfile as sf
from queue import Queue




class AudioDetectionNode:

    def __init__(self, test_value=False):
        self.test = test_value
        self.pub = None

    def start(self):
        # Node and publisher initialization
        self.pub = rospy.Publisher('audio_detection', SpeechData, queue_size=1)
        rospy.init_node('audio_detection_node')
        rospy.Subscriber('listen_start', String, self.listen)
        if self.test:
            source = Microphone(None, 16000, 2720)
        else:
            source = ROSMicrophoneSource(None, 16000, 2720)
        # VAD initialization        
        self.speechRecognition = SpeechRecognitionVAD(
            device_index=None,
            sample_rate=16000,
            chunk_size=2720,
            timeout=0,
            phrase_time_limit=5,  # if put to None, the sounds heard can be of infinite lenght
            calibration_duration=1,
            # the method works by using an energy threshold, so to calibrate the threshould the noise energy in
            # the environment has to be known, the calibration factor che used
            format='int16',
            source=source
        )  

    def listen(self, data):
        rospy.loginfo("Listening...")

        # Get speech data
        # rospy.loginfo("Calibrating...")
        self.speechRecognition.calibrate()  # dynamic calibration manages variations in the sound
        # rospy.loginfo("Recording...")
        speech, timestamps = self.speechRecognition.get_speech_frame(timeout = 5)#TODO use a variable

        msg = SpeechData()
        # publish nothing
        if speech is None:
            msg.data = [0, 0]
            msg.start_time = rospy.get_time()
            msg.end_time = msg.start_time
        # Message preparing if speech is not none
        else:
            msg.data = speech
            msg.start_time = timestamps[0]
            msg.end_time = timestamps[1]

        # Message publishing
        rospy.loginfo("I'm publishing a record of "+ str(msg.end_time - msg.start_time)) # TODO remove
        self.pub.publish(msg)

        rospy.logdebug('Audio published with timestamps')

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--test", dest="test", default='0')
    (options, args) = parser.parse_args()
    test = True if options.test == '1' else False
    speech_detection = AudioDetectionNode(test)
    speech_detection.start()
    rospy.spin()
