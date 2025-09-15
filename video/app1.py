import argparse
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
import yt_dlp
import whisper


def parse_video_id(url_or_id: str) -> str:
    # Mendukung input berupa URL atau langsung video ID
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",  # full URL
        r"^([0-9A-Za-z_-]{11})$"           # direct ID
    ]
    for p in patterns:
        m = re.match(p, url_or_id)
        if m:
            return m.group(1)
    # fallback: coba potong setelah v=
    if "v=" in url_or_id:
        return url_or_id.split("v=")[-1][:11]
    raise ValueError("Tidak bisa mengenali YouTube video ID dari input.")


def pick_best_transcript(video_id: str, lang_prefs: List[str]) -> Optional[Tuple[List[dict], str]]:
    """
    Mengembalikan (transcript_entries, language_code) bila tersedia.
    Prioritas:
      1) Non-auto captions sesuai lang_prefs
      2) Auto captions sesuai lang_prefs
      3) Translatable captions ke lang_prefs
    """
    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
    except (NoTranscriptFound, TranscriptsDisabled):
        return None

    # Helper: cari transcript tertentu sesuai preferensi
    def find_exact(is_generated: Optional[bool]):
        for pref in lang_prefs:
            for t in transcripts:
                if t.language_code.startswith(pref) and (is_generated is None or t.is_generated == is_generated):
                    try:
                        return t.fetch(), t.language_code
                    except Exception:
                        continue
        return None

    # 1) Non-auto
    res = find_exact(is_generated=False)
    if res:
        return res

    # 2) Auto
    res = find_exact(is_generated=True)
    if res:
        return res

    # 3) Translatable ke preferensi
    for t in transcripts:
        for pref in lang_prefs:
            if t.is_translatable and t.language_code != pref:
                try:
                    tr = t.translate(pref).fetch()
                    return tr, pref
                except Exception:
                    continue

    return None


def transcript_to_srt(entries: List[dict]) -> str:
    def fmt_time(sec: float) -> str:
        ms = int((sec - int(sec)) * 1000)
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = int(sec % 60)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

    srt_lines = []
    for i, e in enumerate(entries, 1):
        start = e.get("start", 0.0)
        dur = e.get("duration", 0.0)
        end = start + dur
        text = (e.get("text") or "").replace("\n", " ").strip()
        srt_lines.append(str(i))
        srt_lines.append(f"{fmt_time(start)} --> {fmt_time(end)}")
        srt_lines.append(text if text else "[...]")
        srt_lines.append("")  # blank line
    return "\n".join(srt_lines)


def download_audio_with_ytdlp(url: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    outtmpl = str(out_dir / "%(id)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "noprogress": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # Setelah postprocess, file berekstensi .mp3
        audio_path = out_dir / f"{info['id']}.mp3"
        if not audio_path.exists():
            # fallback: cari file yang ada
            for f in out_dir.glob(f"{info['id']}.*"):
                return f
        return audio_path


def whisper_transcribe(audio_path: Path, model_size: str = "base", language_hint: Optional[str] = None) -> dict:
    model = whisper.load_model(model_size)
    # task 'transcribe' = tetap bahasa asli; 'translate' = terjemahkan ke Inggris
    return model.transcribe(str(audio_path), language=language_hint, task="transcribe", verbose=False)


def whisper_segments_to_srt(result: dict) -> str:
    def fmt_time(sec: float) -> str:
        ms = int((sec - int(sec)) * 1000)
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = int(sec % 60)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

    srt_lines = []
    for i, seg in enumerate(result.get("segments", []), 1):
        start = seg.get("start", 0.0)
        end = seg.get("end", start)
        text = (seg.get("text") or "").strip()
        srt_lines.append(str(i))
        srt_lines.append(f"{fmt_time(start)} --> {fmt_time(end)}")
        srt_lines.append(text if text else "[...]")
        srt_lines.append("")
    return "\n".join(srt_lines)


def save_outputs(base_path: Path, txt: str, srt: str):
    base_path.parent.mkdir(parents=True, exist_ok=True)
    (base_path.with_suffix(".txt")).write_text(txt, encoding="utf-8")
    (base_path.with_suffix(".srt")).write_text(srt, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Transkrip YouTube (with/without subtitles) -> .txt & .srt")
    parser.add_argument("--url", required=True, help="YouTube URL atau video ID")
    parser.add_argument("--langs", default="id,en", help="Preferensi bahasa subtitle, urut prioritas. Contoh: id,en")
    parser.add_argument("--outdir", default="outputs", help="Folder output")
    parser.add_argument("--prefer-captions", action="store_true", help="Fokus pakai caption jika ada (default sudah otomatis).")
    parser.add_argument("--force-stt", action="store_true", help="Paksa STT (abaikan subtitle).")
    parser.add_argument("--model", default="base", help="Whisper model size (tiny, base, small, medium, large).")
    parser.add_argument("--lang-hint", default=None, help="Hint bahasa untuk Whisper (mis. id).")
    args = parser.parse_args()

    url = args.url
    out_dir = Path(args.outdir)
    lang_prefs = [l.strip() for l in args.langs.split(",") if l.strip()]
    video_id = parse_video_id(url)

    base_out = out_dir / video_id

    # 1) Coba ambil caption jika tidak dipaksa STT
    if not args.force_stt:
        picked = pick_best_transcript(video_id, lang_prefs)
        if picked:
            entries, lang = picked
            txt = "\n".join((e.get("text") or "").strip() for e in entries if e.get("text"))
            srt = transcript_to_srt(entries)
            save_outputs(base_out, txt, srt)
            print(f"[OK] Subtitle ditemukan ({lang}). Disimpan ke:\n- {base_out.with_suffix('.txt')}\n- {base_out.with_suffix('.srt')}")
            sys.exit(0)
        else:
            print("[INFO] Subtitle tidak tersedia. Beralih ke STT (Whisper).")

    # 2) Fallback: STT dengan Whisper
    with tempfile.TemporaryDirectory() as tmpd:
        tmp_dir = Path(tmpd)
        audio_path = download_audio_with_ytdlp(url, tmp_dir)
        result = whisper_transcribe(audio_path, model_size=args.model, language_hint=args.lang_hint)
        # Simpan hasil
        txt = (result.get("text") or "").strip()
        srt = whisper_segments_to_srt(result)
        save_outputs(base_out, txt, srt)
        print(f"[OK] Hasil STT disimpan ke:\n- {base_out.with_suffix('.txt')}\n- {base_out.with_suffix('.srt')}")


if __name__ == "__main__":
    main()
