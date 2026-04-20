from __future__ import annotations

import argparse
import logging
from pathlib import Path

from speech_to_sign.config import PipelineConfig
from speech_to_sign.pipeline import SpeechToSignPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Real-time speech-to-sign conversion for VR avatars."
    )
    parser.add_argument(
        "--mapping-file",
        type=Path,
        default=Path("signs.json"),
        help="Path to the word-to-sign token mapping JSON file.",
    )
    parser.add_argument(
        "--language",
        default="en-US",
        help="Speech recognition language code (default: en-US).",
    )
    parser.add_argument(
        "--phrase-time-limit",
        type=int,
        default=5,
        help="Max duration to listen for each utterance.",
    )
    parser.add_argument(
        "--listen-timeout",
        type=int,
        default=1,
        help="Max wait time for speech before looping (seconds).",
    )
    parser.add_argument(
        "--stt-backend",
        choices=["google", "vosk"],
        default="google",
        help="Speech-to-text engine: online Google or offline Vosk.",
    )
    parser.add_argument(
        "--vosk-model-path",
        default=None,
        help="Path to local Vosk model directory (required if --stt-backend vosk).",
    )
    parser.add_argument(
        "--send-to-vr",
        action="store_true",
        help="Send generated sign sequence to a VR endpoint.",
    )
    parser.add_argument(
        "--vr-endpoint",
        default="http://127.0.0.1:5000/sign-sequence",
        help="HTTP endpoint for VR bridge.",
    )
    parser.add_argument(
        "--vr-socket-enabled",
        action="store_true",
        help="Use TCP sockets instead of HTTP when sending to VR.",
    )
    parser.add_argument("--vr-socket-host", default="127.0.0.1")
    parser.add_argument("--vr-socket-port", type=int, default=8765)
    parser.add_argument("--vr-retries", type=int, default=2)
    parser.add_argument("--vr-retry-backoff", type=float, default=0.4)
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    config = PipelineConfig(
        language=args.language,
        phrase_time_limit=args.phrase_time_limit,
        listen_timeout=args.listen_timeout,
        stt_backend=args.stt_backend,
        vosk_model_path=args.vosk_model_path,
        send_to_vr=args.send_to_vr,
        vr_endpoint=args.vr_endpoint,
        vr_socket_enabled=args.vr_socket_enabled,
        vr_socket_host=args.vr_socket_host,
        vr_socket_port=args.vr_socket_port,
        vr_retries=args.vr_retries,
        vr_retry_backoff_seconds=args.vr_retry_backoff,
    )

    pipeline = SpeechToSignPipeline(mapping_file=args.mapping_file, config=config)
    pipeline.run_forever()


if __name__ == "__main__":
    main()
