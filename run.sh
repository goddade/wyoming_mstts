#!/bin/bash

source /PATH/TO/VENV/bin/activate

cd /PATH/TO/WYOMING_MSTTS

python3 -m wyoming_mstts \
    --voice "Microsoft Xiaoxiao (Natural) - Chinese (Simplified, China)" \
    --data-dir /PATH/TO/TTS_DATA \
    --uri "tcp://127.0.0.1:13775"
