import base64
import os
import uuid
from flask import Blueprint, request, jsonify
from flask_login import login_required

from arm.ui import app, db
from arm.models.job import Job, JobState
from arm.models import JobImage
from arm.models.ui_settings import UISettings

route_onboard = Blueprint('route_onboard', __name__, url_prefix='/api')


def _ensure_job_folder(job_id):
    try:
        from arm.config import config as cfg
        base = os.path.join(cfg.arm_config['RAW_PATH'], 'onboard', str(job_id))
        os.makedirs(base, exist_ok=True)
        return base
    except Exception:
        temp = os.path.join('/tmp', 'arm_onboard', str(job_id))
        os.makedirs(temp, exist_ok=True)
        return temp


def _save_dataurl_image(data_url, folder, side):
    if not data_url:
        return None
    header, b64data = data_url.split(',', 1) if ',' in data_url else (None, None)
    if not b64data:
        return None
    ext = 'jpg'
    if header and 'png' in header:
        ext = 'png'
    filename = f"{side}_{uuid.uuid4().hex}.{ext}"
    path = os.path.join(folder, filename)
    with open(path, 'wb') as f:
        f.write(base64.b64decode(b64data))
    return path


@route_onboard.route('/jobs/onboard-disk', methods=['POST'])
@login_required
def onboard_disk():
    body = request.get_json(silent=True) or {}
    has_jewel_case = bool(body.get('has_jewel_case'))
    front_image = body.get('front_image')
    back_image = body.get('back_image')
    disk_image = body.get('disk_image')
    notes = body.get('notes')
    voice_note = body.get('voice_note')

    # Create placeholder job
    job = Job(devpath='/dev/placeholder')
    job.status = JobState.VIDEO_INFO.value
    job.stage = 'detect'
    job.progress = 10
    db.session.add(job)
    db.session.commit()

    folder = _ensure_job_folder(job.job_id)
    saved = {}
    for side, data in [('front', front_image), ('back', back_image), ('disk', disk_image)]:
        path = _save_dataurl_image(data, folder, side)
        if path:
            db.session.add(JobImage(job_id=job.job_id, side=side, path=path))
            saved[side] = path
    db.session.commit()

    # Progress gating: images saved
    try:
        job.progress = 50 if saved else job.progress
        db.session.commit()
    except Exception:
        pass

    # Schedule background AI if enabled
    try:
        ui_cfg = UISettings.query.get(1)
        if ui_cfg and ui_cfg.enable_ai_identification and ui_cfg.openai_api_key:
            from arm.ui.onboard.worker import schedule_ai_identify
            schedule_ai_identify(job.job_id, notes, voice_note)
    except Exception as e:
        app.logger.info(f"AI identification not scheduled: {e}")

    return jsonify({
        'job_id': job.job_id,
        'status': job.status,
        'message': 'Job created; insert disk when ready. Images saved.'
    })


@route_onboard.route('/jobs/<int:job_id>/images/<side>', methods=['POST'])
@login_required
def upload_job_image(job_id, side):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'job not found'}), 404
    if side not in ('front', 'back', 'disk'):
        return jsonify({'error': 'invalid side'}), 400
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'file missing'}), 400
    folder = _ensure_job_folder(job_id)
    ext = os.path.splitext(file.filename)[1] or '.jpg'
    filename = f"{side}_{uuid.uuid4().hex}{ext}"
    path = os.path.join(folder, filename)
    file.save(path)
    db.session.add(JobImage(job_id=job_id, side=side, path=path))
    db.session.commit()
    try:
        from arm.ui.onboard.worker import schedule_ai_identify
        ui_cfg = UISettings.query.get(1)
        if ui_cfg and ui_cfg.enable_ai_identification and ui_cfg.openai_api_key:
            schedule_ai_identify(job_id, None, None)
    except Exception as e:
        app.logger.info(f"AI identification not scheduled: {e}")
    return jsonify({'success': True, 'path': path})


@route_onboard.route('/jobs/<int:job_id>/images_meta', methods=['GET'])
@login_required
def images_meta(job_id):
    images = JobImage.query.filter_by(job_id=job_id).all()
    return jsonify([
        {
            'side': img.side,
            'ocr_text': img.ocr_text,
            'ocr_lang': img.ocr_lang,
            'ocr_confidence': img.ocr_conf
        } for img in images
    ])


@route_onboard.route('/jobs/<int:job_id>/ai_identify', methods=['POST'])
@login_required
def ai_identify_now(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'job not found'}), 404
    try:
        from arm.ui.onboard.worker import schedule_ai_identify
        schedule_ai_identify(job_id, None, None)
        return jsonify({'scheduled': True})
    except Exception as e:
        return jsonify({'scheduled': False, 'error': str(e)}), 500


