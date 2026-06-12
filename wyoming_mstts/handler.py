"""Event handler for clients of the server."""
import argparse
import logging

from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import Event
from wyoming.info import Describe, Info
from wyoming.server import AsyncEventHandler
from wyoming.tts import Synthesize

from .local_mstts import LocalMSTTS

_LOGGER = logging.getLogger(__name__)

class LocalMSTTSEventHandler(AsyncEventHandler):
    """Event handler for clients of the server."""

    def __init__(
            self,
            wyoming_info: Info,
            cli_args: argparse.Namespace,
            *args,
            **kwargs,
    ) -> None:
        """Initialize."""
        super().__init__(*args, **kwargs)

        self.cli_args = cli_args
        self.wyoming_info_event = wyoming_info.event()
        self.tts = LocalMSTTS(cli_args.data_dir, cli_args.voice)
    
    async def handle_event(self, event: Event) -> bool:
        """Handle an event."""
        if Describe.is_type(event.type):
            await self.write_event(self.wyoming_info_event)
            _LOGGER.debug("Sent info")
            return True

        if not Synthesize.is_type(event.type):
            _LOGGER.warning("Unexpected event: %s", event)
            return True

        synthesize = Synthesize.from_event(event)
        _LOGGER.debug(synthesize)

        if synthesize.voice:
            if synthesize.voice.name!= self.tts.speaker:
                self.tts.set_speaker(synthesize.voice.name)
        await self.write_event(
            AudioStart(
                rate=self.tts.sample_rate,
                width=self.tts.data_width,
                channels=self.tts.channels,
            ).event(),
        )
        try:
            await self.write_event(
                AudioChunk(
                    audio=self.tts.synthesis(text=synthesize.text),
                    rate=self.tts.sample_rate,
                    width=self.tts.data_width,
                    channels=self.tts.channels,
                ).event(),
            )
        except Exception as e:
            _LOGGER.error(f"Error during TTS synthesis: {e}")
        await self.write_event(AudioStop().event())
        _LOGGER.debug("Completed request")

        return True
