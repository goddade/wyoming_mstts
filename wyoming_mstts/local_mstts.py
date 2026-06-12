"""Microsoft embedded TTS."""

import logging
from pathlib import Path
import ms_tts

_LOGGER = logging.getLogger(__name__)

def get_voices(data_dir):
    """Get available voices."""
    return ms_tts.get_voices(data_dir)

class LocalMSTTS:
    """Class to handle local Microsoft TTS."""
    sample_rate = 24000
    data_width = 2
    channels = 1

    def __init__(self, data_dir, speaker) -> None:
        """Initialize."""
        _LOGGER.debug("Initialize local MS TTS")

        self.speaker = speaker
        self.tts=ms_tts.MsTTS(data_dir, speaker)

    def __del__(self):
        pass

    def set_speaker(self, name):
        self.speaker=name
        self.tts.set_speaker(name)

    def synthesis(self, text):
        """Begin synthesize text to speech."""
        _LOGGER.debug(f"Requested TTS for [{text}]")
        return self.tts.synthesis(text)

