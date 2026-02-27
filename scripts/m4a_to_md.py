#!/usr/bin/env python3

"""
Converte arquivo de áudio M4A em texto (transcrição) e salva em arquivo .md local.
Offline e sem custo de API para transcrição (faster-whisper ou openai-whisper). PT-BR.
"""

import argparse
import os
import sys
import time
import warnings
from pathlib import Path
from typing import Optional

os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
warnings.filterwarnings("ignore")

PT_BR_PROMPT = "Transcrição em português do Brasil. Texto em português brasileiro."


def transcrever_audio(
    m4a_path: str,
    output_path: Optional[str] = None,
    model: str = "base",
    device: str = "auto",
) -> str:
    m4a = Path(m4a_path).resolve()
    if not m4a.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {m4a}")

    if output_path is None:
        output_path = m4a.with_suffix(".md")
    else:
        output_path = Path(output_path).resolve()
        if output_path.suffix.lower() != ".md":
            output_path = output_path.with_suffix(".md")

    print(f"Transcrevendo: {m4a.name}")
    print("Carregando modelo Whisper...")

    texto = ""
    duration = 0.0

    try:
        from faster_whisper import WhisperModel

        device_type = "cuda" if device == "cuda" else "cpu"
        compute_type = "float16" if device_type == "cuda" else "int8"
        audio_model = WhisperModel(model, device=device_type, compute_type=compute_type)
        print("Processando áudio...")
        segments, info = audio_model.transcribe(
            str(m4a),
            language="pt",
            initial_prompt=PT_BR_PROMPT,
            beam_size=5,
        )
        texto = " ".join(segment.text for segment in segments)
        duration = getattr(info, "duration", 0.0)

    except ImportError:
        print("faster-whisper não encontrado, tentando openai-whisper...")
        import whisper

        audio_model = whisper.load_model(model)
        resultado = audio_model.transcribe(
            str(m4a),
            language="pt",
            task="transcribe",
            initial_prompt=PT_BR_PROMPT,
        )
        texto = resultado.get("text", "")

    if not texto.strip():
        texto = "(Nenhum texto detectado no áudio.)"

    md_content = (
        f"# Transcrição: {m4a.stem}\n\n"
        f"*Transcrito em: {time.strftime('%d/%m/%Y %H:%M:%S')}*\n\n"
        f"**Modelo:** {model}\n"
        f"**Duração:** {duration:.2f}s\n\n"
        f"---\n\n"
        f"{texto}\n"
    )

    output_path.write_text(md_content, encoding="utf-8")
    print(f"Salvo em: {output_path}")
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(description="Transcreve áudio M4A para MD")
    parser.add_argument("arquivo", help="Arquivo M4A")
    parser.add_argument("-o", "--output", help="Arquivo MD de saída")
    parser.add_argument(
        "-m", "--model", default="base", choices=["tiny", "base", "small", "medium", "large"]
    )
    parser.add_argument(
        "-d", "--device", default="auto", choices=["auto", "cuda", "cpu"]
    )
    args = parser.parse_args()
    try:
        transcrever_audio(args.arquivo, args.output, args.model, args.device)
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
