import os
import re
import unicodedata

from arm.ui import db
from arm.models import JobImage
from arm.models.job import Job
from arm.models.ui_settings import UISettings


LINE_PER_TRACK_REGEX = re.compile(r"^(\d{1,2})[)\.\-\s]+(.+)$")


def _sanitize_filename(name: str) -> str:
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    name = re.sub(r'[\\/:*?"<>|]', '', name)
    name = name.strip()
    return name


def _parse_tracklist(text: str) -> list[str]:
    tracks = []
    for raw in text.splitlines():
        raw = raw.strip()
        m = LINE_PER_TRACK_REGEX.match(raw)
        if m:
            title = re.sub(r"\b\d{1,2}:\d{2}\b$", "", m.group(2)).strip()
            tracks.append(title)
    if not tracks:
        # Fallback blob: "01 Title 02 Title ..."
        parts = re.split(r"\b(\d{2})\s+", text)
        buf = []
        current = None
        for part in parts:
            if re.fullmatch(r"\d{2}", part):
                if current:
                    buf.append(current.strip())
                current = ""
            else:
                if current is not None:
                    current += part
        if current:
            buf.append(current.strip())
        tracks = [re.sub(r"\b\d{1,2}:\d{2}\b$", "", t).strip() for t in buf if t.strip()]
    return tracks


def rename_tracks_from_back_cover(job: Job):
    ui_cfg = UISettings.query.get(1)
    if not ui_cfg or not ui_cfg.enable_cd_track_renaming:
        return
    images = JobImage.query.filter_by(job_id=job.job_id, side='back').all()
    if not images:
        return
    # Use stored OCR text if available; else skip (OCR via AI handled in worker)
    back = next((i for i in images if i.ocr_text), None)
    if not back or not back.ocr_text:
        return
    tracks = _parse_tracklist(back.ocr_text)
    if not tracks:
        return
    # Rename files in job.path
    out_dir = job.path or ''
    if not out_dir or not os.path.isdir(out_dir):
        return
    files = sorted([f for f in os.listdir(out_dir) if os.path.isfile(os.path.join(out_dir, f))])
    audio_exts = {'.flac', '.mp3', '.m4a', '.wav', '.aiff', '.ogg'}
    audio_files = [f for f in files if os.path.splitext(f)[1].lower() in audio_exts]
    audio_files.sort()
    for idx, src in enumerate(audio_files[:len(tracks)], start=1):
        title = _sanitize_filename(tracks[idx - 1]) or f"Track {idx:02d}"
        album_prefix = ''
        if job.title and job.video_type == 'unknown':
            album_prefix = f"{_sanitize_filename(job.title)} - "
        dst = f"{album_prefix}{idx:02d} - {title}{os.path.splitext(src)[1]}"
        src_path = os.path.join(out_dir, src)
        dst_path = os.path.join(out_dir, dst)
        if os.path.abspath(src_path) == os.path.abspath(dst_path):
            continue
        if os.path.exists(dst_path):
            continue
        try:
            os.rename(src_path, dst_path)
        except Exception:
            continue


