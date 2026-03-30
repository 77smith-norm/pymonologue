"""
speech_recognizer.py — SFSpeechRecognizer wrapper for Pythonista.

Phase 1: File-based recording.
Records audio via sound.Recorder → saves to .m4a → transcribes via SFSpeechRecognizer.

Validated on device (iPhone 11 Pro Max):
- sound.Recorder works in keyboard context (use tempfile.gettempdir(), NOT /tmp)
- SFSpeechRecognizer accessible via objc_util
- NSLocale requires: NSLocale.alloc().initWithLocaleIdentifier_('en-US')
  (objc_util.ns('en-US') returns NSTaggedPointerString — wrong type)
"""

import objc_util
import sound
import os
import tempfile


def _create_recognizer(locale: str = 'en-US'):
    """
    Create and return an SFSpeechRecognizer instance.

    Args:
        locale: BCP-47 locale string (e.g. 'en-US')

    Returns:
        SFSpeechRecognizer ObjC instance
    """
    SFSpeechRecognizer = objc_util.ObjCClass('SFSpeechRecognizer')
    NSLocale = objc_util.ObjCClass('NSLocale')

    locale_obj = NSLocale.alloc().initWithLocaleIdentifier_(locale)
    recognizer = SFSpeechRecognizer.alloc().initWithLocale_(locale_obj)
    return recognizer


def transcribe(audio_path: str, locale: str = 'en-US') -> str:
    """
    Transcribe an audio file using on-device SFSpeechRecognizer.

    Args:
        audio_path: Path to .m4a or .wav audio file
        locale: BCP-47 locale string

    Returns:
        Transcribed text string, or empty string if transcription fails
    """
    if not os.path.exists(audio_path):
        return ''

    recognizer = _create_recognizer(locale)
    if not recognizer.isAvailable():
        return ''

    NSURL = objc_util.ObjCClass('NSURL')
    SFSpeechURLRecognitionRequest = objc_util.ObjCClass('SFSpeechURLRecognitionRequest')

    url = NSURL.fileURLWithPath_(audio_path)
    request = SFSpeechURLRecognitionRequest.alloc().init()
    request.setURL_(url)
    request.setRequestsOnDeviceRecognition_(True)

    # recognitionTaskWithRequest_ is async delegate-based.
    # For Phase 1 we use SFSpeechURLRecognitionRequest which can give
    # a synchronous result for short files.
    result = recognizer.recognitionTaskWithRequest_(request)

    if result:
        best = result.bestTranscription()
        if best:
            return str(best.formattedString())

    return ''


def record_audio(duration: float = 3.0, suffix: str = '.m4a') -> str:
    """
    Record audio to a temp file using sound.Recorder.

    IMPORTANT: Use tempfile.gettempdir() for the path — /tmp is NOT writable
    in the Pythonista keyboard extension sandbox.

    Args:
        duration: Recording duration in seconds
        suffix: File suffix (.m4a or .wav)

    Returns:
        Path to the recorded audio file
    """
    path = tempfile.gettempdir() + '/pymonologue_rec' + suffix
    recorder = sound.Recorder(path)
    recorder.record()
    import time
    time.sleep(duration)
    recorder.stop()
    return path


# --- Convenience API (main entry point for keyboard) ---


class SpeechRecognizer:
    """
    Wrapper around SFSpeechRecognizer for file-based transcription.

    Usage:
        recognizer = SpeechRecognizer()
        path = record_audio(duration=3.0)
        transcript = recognizer.transcribe(path)
    """

    def __init__(self, locale: str = 'en-US'):
        self.locale = locale
        self._recognizer = None

    def transcribe(self, audio_path: str) -> str:
        """Transcribe an audio file."""
        return transcribe(audio_path, self.locale)


if __name__ == '__main__':
    # Quick smoke test
    print('Recording 3s...')
    path = record_audio(3.0)
    print(f'Recorded: {path}, exists: {os.path.exists(path)}')

    print('Transcribing...')
    text = transcribe(path)
    print(f'Transcript: {text}')
