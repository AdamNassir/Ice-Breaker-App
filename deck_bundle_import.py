"""Validated, revision-safe ZIP imports for the publicly accessible IceBreaker deck.

A bundle contains manifest.json + questions.json and optionally assets/ binaries.
Curated bundles may instead reference pinned publisher image IDs. Such sources
are downloaded server-side during import; no arbitrary client URL is fetched.
Never commit the saved deck unless *all* referenced media has been obtained,
validated, uploaded and the revision is still current.
"""
from __future__ import annotations

import hashlib
import io
import ipaddress
import json
import re
import socket
import urllib.error
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import PurePosixPath
from urllib.parse import urlsplit

from fastapi import HTTPException
from question_content import DeckError, MEDIA_FOLDERS, validate_rounds, is_public_icebreaker_blob

MAX_ZIP = 4 * 1024 * 1024
MAX_ASSETS = 20
MAX_IMAGE_BYTES = 9 * 1024 * 1024
MAX_TOTAL_BYTES = 35 * 1024 * 1024
MAX_QUESTION_BYTES = 2 * 1024 * 1024

# Curated, attributed source originals. Only these IDs can be downloaded; ZIP
# authors cannot submit arbitrary URLs to the Vercel server (SSRF protection).
# A publisher can change/remove a file at any time; imports fail atomically
# instead of silently substituting a lookalike image.
CURATED_SOURCES = {
    'squirrel_nikon_2024': 'https://c02.purpledshub.com/uploads/sites/62/2024/12/Nikon-Comedy-Wildlife-Awards-stuck-squirrel.jpg',
    'jira_cloud_excentia_2026': 'https://www.excentia.es/img/atlassian-products/nueva-vista-work-item-jira-cloud.png',
    'excel_arena_microsoft_2025': 'https://techcommunity.microsoft.com/t5/s/gxcuf89792/images/bS00NDc1MjI4LTN1UzNhRA?revision=2',
    'pope_leo_nikes_2026': 'https://i.pdimage.com/static/content/26-05/08/vatikanin-papa-14-leo-icin-hazirladigi-belgeselde-papanin-ayaginda-nike-ayakkabili-fotograflari-seytan-prada-giyer-papa-nike-esprilerine-neden-oldu.jpg',
    'flamingone_original_miles_astray': 'https://static.wixstatic.com/media/c396be_17aa907139bc454887e9ec2b59da986d~mv2.jpg',
}


def _public_https(url):
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError('Image must use a public HTTPS address.')
    addresses = socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(addr[4][0]).is_global for addr in addresses):
        raise ValueError('Image destination is not a public address.')


class SafePublicRedirect(urllib.request.HTTPRedirectHandler):
    """Publisher CDNs may redirect; never follow redirects to local/private hosts."""
    max_redirections = 2
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _public_https(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _read_json_file(zf, name, limit):
    try:
        info = zf.getinfo(name)
    except KeyError as error:
        raise HTTPException(422, f'ZIP missing {name}.') from error
    if info.file_size > limit:
        raise HTTPException(413, f'{name} exceeds the permitted size.')
    try:
        return json.loads(zf.read(name).decode('utf-8'))
    except (UnicodeError, ValueError) as error:
        raise HTTPException(422, f'{name} is not valid UTF-8 JSON.') from error


def _safe_path(value):
    return (isinstance(value, str) and bool(re.fullmatch(r'assets/[a-zA-Z0-9_-]+\.(jpg|jpeg|png|webp)', value))
            and '..' not in PurePosixPath(value).parts)


def read_bundle(data: bytes):
    """Return (questions, manifest-media, embedded-bytes). No side effects."""
    if not data or len(data) > MAX_ZIP:
        raise HTTPException(413, 'ZIP is empty or exceeds the 4 MB Vercel upload limit.')
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
    except (ValueError, zipfile.BadZipFile) as error:
        raise HTTPException(422, 'Not a valid ZIP file.') from error
    with zf:
        entries = zf.infolist()
        if len(entries) > MAX_ASSETS + 2:
            raise HTTPException(422, 'The ZIP has too many files.')
        names = [f.filename for f in entries]
        if len(set(names)) != len(names):
            raise HTTPException(422, 'Duplicate ZIP paths are not permitted.')
        total = 0
        for info in entries:
            if info.is_dir() or (info.external_attr >> 16) & 0o170000 == 0o120000:
                raise HTTPException(422, 'ZIP directories and links are not permitted.')
            if not (info.filename in ('manifest.json', 'questions.json') or _safe_path(info.filename)):
                raise HTTPException(422, f'Unexpected ZIP file: {info.filename[:100]}')
            total += info.file_size
            if total > MAX_TOTAL_BYTES or info.file_size > MAX_IMAGE_BYTES:
                # Manifest/question limit has separate checks below.
                if info.filename not in ('manifest.json', 'questions.json'):
                    raise HTTPException(413, 'ZIP contains oversized media or excessive uncompressed data.')
            if info.compress_size and info.file_size / info.compress_size > 350:
                raise HTTPException(422, 'Suspicious ZIP compression ratio.')
        if total > MAX_TOTAL_BYTES:
            raise HTTPException(413, 'The ZIP unpacks to too much data.')
        manifest = _read_json_file(zf, 'manifest.json', 64 * 1024)
        raw = _read_json_file(zf, 'questions.json', MAX_QUESTION_BYTES)
        if not isinstance(manifest, dict) or manifest.get('format') != 'icebreaker-deck-bundle' or manifest.get('version') != 1:
            raise HTTPException(422, 'Unknown manifest format/version (expected icebreaker-deck-bundle v1).')
        media = manifest.get('media')
        rounds = raw.get('rounds') if isinstance(raw, dict) else None
        if not isinstance(media, dict) or not isinstance(rounds, list) or not 1 <= len(rounds) <= 200:
            raise HTTPException(422, 'The ZIP must contain a manifest.media map and 1–200 questions.')
        if len(media) > MAX_ASSETS or any(not _safe_path(path) for path in media):
            raise HTTPException(422, 'Invalid media paths in manifest.')
        embedded = {}
        for path, description in media.items():
            if not isinstance(description, dict) or set(description) - {'source_id', 'transform', 'credit', 'source_url'}:
                raise HTTPException(422, f'Invalid manifest media metadata: {path}')
            if path in names:
                embedded[path] = zf.read(path)
            elif description.get('source_id') not in CURATED_SOURCES:
                raise HTTPException(422, f'{path} missing. Include the image or provide a supported curated source_id.')
            if description.get('transform') not in (None, 'jira-story-overlay'):
                raise HTTPException(422, f'Unknown image transformation: {path}')
            if description.get('transform') == 'jira-story-overlay' and description.get('source_id') != 'jira_cloud_excentia_2026':
                raise HTTPException(422, 'The Jira overlay requires the verified 2026 Jira screenshot source.')
        for filename in names:
            if filename.startswith('assets/') and filename not in media:
                raise HTTPException(422, f'Undeclared ZIP media: {filename}')
        # Identify every media reference and reject any missing manifest entry
        # before a single Blob upload is attempted.
        referenced = set()
        for index, row in enumerate(rounds, 1):
            if not isinstance(row, dict):
                raise HTTPException(422, f'Question {index} is not an object.')
            for target, key in _media_locations(row):
                val = target.get(key, '')
                if isinstance(val, str) and val.startswith('assets/'):
                    if val not in media:
                        raise HTTPException(422, f'Question {index}: missing media declaration: {val}')
                    referenced.add(val)
        if set(media) != referenced:
            raise HTTPException(422, 'Every declared image must be referenced by a question.')
        # Substitute known-good Blob placeholders to validate all the ordinary
        # question fields *before* performing network I/O and writing to Blob.
        probe = json.loads(json.dumps(rounds))
        for row in probe:
            for target, key in _media_locations(row):
                if target.get(key) in media:
                    target[key] = 'https://sample.public.blob.vercel-storage.com/icebreaker/images/safe.jpg'
        try:
            validate_rounds(probe, require_media=True)
        except DeckError as error:
            raise HTTPException(422, str(error)) from error
        return rounds, media, embedded


def _media_locations(row):
    yield row, 'media'
    yield row, 'reveal_media'
    news = row.get('news')
    if isinstance(news, dict):
        yield news, 'logo_url'
        yield news, 'hero_image'
        for item in news.get('related') or []:
            if isinstance(item, dict):
                yield item, 'image'


def fetch_curated(source_id):
    """Fetch only a fixed trusted publisher URL, without redirects or private IPs."""
    url = CURATED_SOURCES[source_id]
    hostname = urlsplit(url).hostname
    if not hostname or not url.startswith('https://'):
        raise HTTPException(502, 'Invalid curated media host.')
    try:
        _public_https(url)
        req = urllib.request.Request(url, headers={'User-Agent': 'IceBreaker-DeckImporter/1.0 (seminar presentation)', 'Accept': 'image/*'})
        with urllib.request.build_opener(SafePublicRedirect()).open(req, timeout=12) as response:
            if not response.headers.get('content-type', '').lower().startswith('image/'):
                raise ValueError('Publisher did not serve an image')
            data = response.read(MAX_IMAGE_BYTES + 1)
            if not data or len(data) > MAX_IMAGE_BYTES:
                raise ValueError('Publisher image is empty or too large')
            return data
    except (OSError, urllib.error.URLError, ValueError) as error:
        raise HTTPException(502, 'Unable to obtain original image from its credited publisher (' + source_id + '). '
                             'Download the source image yourself and add it under assets/ in the ZIP.') from error


def _font(size, bold=False):
    from PIL import ImageFont
    for font in ('DejaVuSans-Bold.ttf', 'DejaVuSans.ttf') if bold else ('DejaVuSans.ttf',):
        try:
            return ImageFont.truetype(font, size)
        except OSError:
            pass
    return ImageFont.load_default()


def _wrap_text(draw, text, font, width):
    lines = []
    for paragraph in text.split('\n'):
        current = ''
        for word in paragraph.split():
            attempt = (current + ' ' + word).strip()
            if draw.textbbox((0, 0), attempt, font=font)[2] > width and current:
                lines.append(current)
                current = word
            else:
                current = attempt
        lines.append(current)
    return lines


def _jira_overlay(img):
    """Modify the real Jira issue screenshot, retaining its actual right panel."""
    from PIL import Image, ImageDraw
    # The verified screenshot is 1000x617 with a 640px left pane. The
    # replacement is restricted to that pane. Refuse a changed source layout.
    if not 1.48 < (img.width / img.height) < 1.75:
        raise HTTPException(422, 'The Jira screenshot layout changed; cannot safely overlay this ticket.')
    frame = img.convert('RGB')
    w, h = frame.size
    sx = w / 1000
    sy = h / 617
    d = ImageDraw.Draw(frame)
    def xy(x, y): return round(x * sx), round(y * sy)
    d.rectangle((xy(0, 0), xy(628, 617)), fill='#ffffff')
    d.line((xy(629, 0), xy(629, 617)), fill='#dfe1e6', width=max(1, int(2 * sx)))
    ink = '#172b4d'; muted = '#44546f'
    d.text(xy(17, 8), 'LogicLever  /  MERCATO  /  LL-482  ·  Story', font=_font(int(11*sx)), fill=muted)
    d.text(xy(17, 42), 'Fluidifier la collaboration entre COP et EPIC', font=_font(int(19*sx), True), fill=ink)
    d.line((xy(17, 78), xy(601, 78)), fill='#dde3eb', width=max(1, int(sx)))
    d.text(xy(17, 95), 'Description', font=_font(int(15*sx), True), fill=ink)
    story = ('En tant que participant au Mercato, je souhaite bénéficier d’une expérience intuitive, '
             'intelligente et personnalisée afin de maximiser les synergies inter-équipes et l’engagement collectif.')
    f = _font(int(13*sx)); y = 127
    for line in _wrap_text(d, story, f, int(570*sx)):
        d.text(xy(17, y), line, font=f, fill=ink); y += 24
    y += 16
    d.text(xy(17, y), 'Critères d’acceptation', font=_font(int(15*sx), True), fill=ink); y += 37
    for item in ('Navigation parfaitement fluide pour tous les profils.',
                 'Recommandations pertinentes et innovantes.',
                 'Chaque interaction maximise la valeur créée.',
                 'Satisfaction globale optimale.'):
        for first, line in enumerate(_wrap_text(d, item, f, int(535*sx))):
            d.text(xy(21 if first else 31, y), line if first else '• ' + line, font=f, fill=ink); y += 22
        y += 10
    return frame


def normalize_image(data, transform=None):
    from PIL import Image, ImageOps, UnidentifiedImageError
    try:
        Image.MAX_IMAGE_PIXELS = 25_000_000
        image = ImageOps.exif_transpose(Image.open(io.BytesIO(data)))
        image.load()
        if image.width * image.height > 25_000_000:
            raise ValueError('image too many pixels')
        if transform == 'jira-story-overlay':
            image = _jira_overlay(image)
        image.thumbnail((1900, 1400), Image.Resampling.LANCZOS)
        output = io.BytesIO()
        image.convert('RGB').save(output, format='JPEG', quality=83, optimize=True)
        blob = output.getvalue()
        if len(blob) > 4 * 1024 * 1024:
            raise ValueError('compressed image still larger than 4 MB')
        return blob
    except HTTPException:
        raise
    except (OSError, ValueError, UnidentifiedImageError, Image.DecompressionBombError) as error:
        raise HTTPException(422, 'Invalid or oversized image in the ZIP/import source.') from error


def collect_assets(media, embedded):
    def get_one(item):
        path, meta = item
        raw = embedded.get(path) or fetch_curated(meta['source_id'])
        normalized = normalize_image(raw, meta.get('transform'))
        if path.startswith('assets/') and path != 'assets/03_jira_user_story.png':
            # Reject accidental low-resolution thumbnails (a previous import
            # accepted a blurred squirrel thumbnail). Keep the deck untouched.
            from PIL import Image
            with Image.open(io.BytesIO(normalized)) as img:
                min_width, min_height = (900, 600) if path.endswith('02_stuck_squirrel.jpg') else (700, 450)
                if img.width < min_width or img.height < min_height:
                    raise HTTPException(422, 'Media resolution too low for projection: ' + path)
        return path, normalized
    # Resolve/transform all media before uploading any object or changing deck.
    with ThreadPoolExecutor(max_workers=5) as pool:
        return dict(pool.map(get_one, media.items()))


def upload_assets(blobs, token):
    if blobs and not token:
        raise HTTPException(503, 'BLOB_READ_WRITE_TOKEN is missing from IceBreaker Vercel environment variables.')
    urls = {}
    try:
        from vercel.blob import BlobClient
        with BlobClient(token=token) as client:
            for path, binary in blobs.items():
                stem = hashlib.sha256(binary).hexdigest()[:24]
                item = client.put('icebreaker/images/' + stem + '.jpg', binary, access='public',
                                  content_type='image/jpeg', add_random_suffix=True)
                url = item.get('url', '') if isinstance(item, dict) else getattr(item, 'url', '')
                if not is_public_icebreaker_blob(url, 'images'):
                    raise ValueError('Vercel Blob returned an invalid public URL')
                urls[path] = url
    except Exception as error:
        # No deck state is written on failure. Successfully uploaded objects
        # may be left orphaned; reimport does not publish a partial deck.
        raise HTTPException(502, 'Unable to upload all ZIP images to Vercel Blob. The deck was not changed.') from error
    return urls


def substitute_assets(rounds, urls):
    result = json.loads(json.dumps(rounds))
    for row in result:
        for target, key in _media_locations(row):
            if target.get(key) in urls:
                target[key] = urls[target[key]]
    return result
