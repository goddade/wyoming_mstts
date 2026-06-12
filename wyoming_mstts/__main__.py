#!/usr/bin/env python3
import argparse
import asyncio
import logging
from functools import partial
from pathlib import Path
from typing import Any, Dict, Set

from wyoming.info import Attribution, Info, TtsProgram, TtsVoice, TtsVoiceSpeaker
from wyoming.server import AsyncServer

from . import __version__
from .handler import LocalMSTTSEventHandler
from .local_mstts import get_voices

_LOGGER = logging.getLogger(__name__)

async def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--voice",
        default="Microsoft Xiaoxiao (Natural) - Chinese (Simplified, China)",
        help="Default voice to use (e.g., 'Microsoft Xiaoxiao (Natural) - Chinese (Simplified, China)')",
    )
    parser.add_argument(
        "--uri",
        default="tcp://127.0.0.1:13775",
        help="unix:// or tcp://"
    )
    parser.add_argument(
        "--data-dir",
        required=True,
        help="Data directory to check for downloaded models",
    )
    parser.add_argument("--debug", action="store_true", help="Log DEBUG messages")
    parser.add_argument(
        "--log-format", default=logging.BASIC_FORMAT, help="Format for log messages"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=__version__,
        help="Print version and exit",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO, format=args.log_format
    )
    _LOGGER.debug(args)

    # Load voice info
    voices_info = get_voices(args.data_dir)

    voices = [
        TtsVoice(
            name=voice.name,
            description=get_description(voice),
            attribution=None,
            installed=True,
            version=None,
            languages=[
                voice.language
            ],
            speakers=None
        )
        for voice in voices_info
    ]
    
    wyoming_info = Info(
        tts=[
            TtsProgram(
                name="Local MS TTS",
                description="Local MS TTS",
                attribution=Attribution(
                    name="MS", url=""
                ),
                installed=True,
                voices=sorted(voices, key=lambda v: v.name),
                version=__version__,
            )
        ],
    )

    # Start server
    server = AsyncServer.from_uri(args.uri)

    _LOGGER.info("Ready")

    await server.run(
        partial(
            LocalMSTTSEventHandler,
            wyoming_info,
            args,
        )
    )


# -----------------------------------------------------------------------------


def get_description(voice_info):
    """Get a human readable description for a voice."""
    info = voice_info.name.split(" - ")[0].replace("Microsoft ", "").split("(")
    name= info[0].strip()
    quality = info[1].replace(")", "").strip()
    return f"{name} ({quality} {voice_info.gender})"


# -----------------------------------------------------------------------------


def run():
    asyncio.run(main())


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass
