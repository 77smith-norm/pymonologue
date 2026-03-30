"""
speech_recognizer.py — SFSpeechRecognizer wrapper for Pythonista.

Phase 1: File-based recording.
Records audio via sound.Recorder → saves to .m4a → transcribes via SFSpeechRecognizer.

This is the Phase 1 approach (Approach A).
Approach B (streaming via AVAudioEngine) is in streaming_recognizer.py (Phase 4).
"""

import tempfile
from pathlib import Path

# Will be populated with objc_util calls after device smoke test
# The actual implementation depends on whether SFSpeechRecognizer
# works via objc_util in the keyboard context.

# PLACEHOLDER — implementation after smoke test confirms it works
#
# Expected API:
#
# from speech_recognizer import SpeechRecognizer
#
# recognizer = SpeechRecognizer()
# transcript = recognizer.transcribe('/path/to/audio.m4a')
# print(transcript)


class SpeechRecognizer:
    """
    Wrapper around SFSpeechRecognizer for file-based transcription.

    Usage:
        recognizer = SpeechRecognizer()
        transcript = recognizer.transcribe('/path/to/audio.m4a')
    """

    def __init__(self, locale: str = 'en-US'):
        self.locale = locale
        self._recognizer = None  # Lazily initialized

    def _ensure_recognizer(self):
        """Initialize SFSpeechRecognizer via objc_util."""
        # This is where objc_util calls will go:
        #
        # from objc_util import ObjCClass, ObjCInstance
        #
        # NSLocale = ObjCClass('NSLocale')
        # SFSpeechRecognizer = ObjCClass('SFSpeechRecognizer')
        #
        # locale_obj = NSLocale.localeWithLocaleIdentifier_(self.locale)
        # self._recognizer = SFSpeechRecognizer.alloc().initWithLocale_(locale_obj)
        pass

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe an audio file using on-device SFSpeechRecognizer.

        Args:
            audio_path: Path to .m4a or .wav audio file

        Returns:
            Transcribed text string
        """
        self._ensure_recognizer()

        # This is where the actual transcription call goes:
        #
        # NSURL = ObjCClass('NSURL')
        # SFSpeechRecognitionRequest = ObjCClass('SFSpeechRecognitionRequest')
        # AVAudioSession = ObjCClass('AVAudioSession')
        #
        # # Set audio session
        # session = AVAudioSession.sharedInstance()
        # session.setCategory_error_('playAndRecord', None)
        # session.setActive_error_(True, None)
        #
        # # Create request
        # url = NSURL.fileURLWithPath_(audio_path)
        # request = SFSpeechRecognitionRequest.alloc().init()
        # request.setURl(url)
        # request.setRequestsOnDeviceRecognition_(True)
        #
        # # Recognize
        # result = self._recognizer.recognitionTaskWithRequest_(request)
        # return result.bestTranscription().formattedString()

        raise NotImplementedError(
            "SFSpeechRecognizer implementation pending device smoke test. "
            "Run the smoke test first to confirm objc_util calls work in keyboard context."
        )


# --- Voice recording helpers ---


def get_temp_audio_path(suffix: str = '.m4a') -> str:
    """Get a temp file path for audio recording."""
    fd, path = tempfile.mkstemp(suffix=suffix)
    import os
    os.close(fd)
    return path


if __name__ == '__main__':
    print("speech_recognizer.py — Phase 1 placeholder")
    print()
    print("This module requires device smoke test before implementation.")
    print("Key question: does SFSpeechRecognizer work via objc_util in a Pythonista keyboard?")
    print()
    print("Expected workflow:")
    print("1. Run device smoke test (docs/TESTING.md)")
    print("2. If smoke test passes, implement the _ensure_recognizer() and transcribe() methods")
    print("3. Phase 1 core loop is then: sound.Recorder → transcribe() → insert_text()")
