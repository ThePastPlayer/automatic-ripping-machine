import json
import threading
from typing import Optional

from arm.ui import app, db
from arm.models import JobImage
from arm.models.job import Job
from arm.models.ui_settings import UISettings


def _run_identify(job_id: int, notes: Optional[str], voice_note: Optional[str]):
    job = Job.query.get(job_id)
    if not job:
        app.logger.error(f"AI identify: job {job_id} not found")
        return
    ui_cfg = UISettings.query.get(1)
    if not ui_cfg or not ui_cfg.openai_api_key or not ui_cfg.enable_ai_identification:
        app.logger.info(f"AI disabled or missing key for job {job_id}; skipping")
        return

    # Collect images
    images = JobImage.query.filter_by(job_id=job_id).all()
    image_urls = []
    for img in images:
        try:
            # For local files, we can pass as data URLs or file URLs; here keep path to be read by client wrapper
            image_urls.append(img.path)
        except Exception:
            continue

    # Build prompt
    user_text = "Extract canonical metadata from disc cover images. Return only JSON."
    if notes:
        user_text += f"\nUser notes: {notes}"
    if voice_note:
        user_text += f"\nVoice note: {voice_note}"

    # Call OpenAI via simple HTTP client (placeholder; integrate official SDK if available)
    try:
        from arm.ui.onboard.vision_client import identify_from_images
        result = identify_from_images(
            api_key=ui_cfg.openai_api_key,
            user_text=user_text,
            image_paths=image_urls,
        )
    except Exception as e:
        app.logger.error(f"OpenAI call failed: {e}")
        return

    # Parse and update job
    try:
        payload = json.loads(result) if isinstance(result, str) else result
    except Exception:
        app.logger.error("AI response not JSON; skipping update")
        return

    try:
        # Update job fields defensively
        media_type = payload.get('media_type')
        if media_type == 'music':
            job.video_type = 'unknown'
            job.title = payload.get('album_title') or job.title
            job.year = (payload.get('year') or job.year)
        elif media_type in ('movie', 'tv_show', 'unknown'):
            job.video_type = 'movie' if media_type == 'movie' else ('series' if media_type == 'tv_show' else 'unknown')
            job.title = payload.get('canonical_title') or job.title
            job.year = (payload.get('year') or job.year)
        # Progress gating
        confidence = payload.get('confidence') or 0
        job.progress = 75 if confidence and float(confidence) >= 0.7 else 65
        job.stage = 'identified'
        db.session.commit()
    except Exception as e:
        app.logger.error(f"Failed to update job with AI results: {e}")


def schedule_ai_identify(job_id: int, notes: Optional[str], voice_note: Optional[str]):
    thread = threading.Thread(target=_run_identify, args=(job_id, notes, voice_note), daemon=True)
    thread.start()
    return True


