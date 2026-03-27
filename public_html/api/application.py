import datetime
import os
import tempfile
import hashlib
import json
import shutil

BASE_DIR = '/home/ivysfyoq/public_html/api'
VIEW_COUNT_FILE = os.path.join(BASE_DIR, 'v.txt')
VIEW_BACKUP_FILE = os.path.join(BASE_DIR, 'v.txt.bak')
RATE_LIMIT_FILE = os.path.join(BASE_DIR, 'rate_limits.json')

MAX_VIEWS_PER_IP_PER_DAY = 30

def today():
    return datetime.date.today().isoformat()

def get_client_ip(environ):
    forwarded = environ.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return environ.get('REMOTE_ADDR', 'unknown')

def hash_ip(ip):
    return hashlib.sha256(ip.encode()).hexdigest()[:16]

def atomic_write(filepath, content):
    """Write content to file atomically via temp file + rename."""
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(filepath))
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        os.replace(tmp, filepath)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise

def read_view_data():
    """Read view counts, falling back to backup if primary is corrupt."""
    for path in (VIEW_COUNT_FILE, VIEW_BACKUP_FILE):
        try:
            with open(path, 'r') as f:
                lines = f.readlines()
            data = {}
            for line in lines:
                parts = line.strip().split(',')
                if len(parts) != 2:
                    continue
                date_str, count_str = parts
                try:
                    data[date_str] = int(count_str)
                except ValueError:
                    continue
            if data:
                return data
        except (FileNotFoundError, IOError):
            continue
    return {}

def write_view_data(data):
    """Write view data atomically and maintain a backup."""
    content = ''.join(f"{d},{c}\n" for d, c in sorted(data.items()))
    # Backup current file before overwriting
    if os.path.exists(VIEW_COUNT_FILE):
        try:
            shutil.copy2(VIEW_COUNT_FILE, VIEW_BACKUP_FILE)
        except IOError:
            pass
    atomic_write(VIEW_COUNT_FILE, content)

def check_rate_limit(ip_hash):
    t = today()
    try:
        with open(RATE_LIMIT_FILE, 'r') as f:
            limits = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, IOError):
        limits = {}

    limits = {k: v for k, v in limits.items() if v.get('date') == t}

    entry = limits.get(ip_hash, {'date': t, 'count': 0})
    if entry.get('date') != t:
        entry = {'date': t, 'count': 0}

    if entry['count'] >= MAX_VIEWS_PER_IP_PER_DAY:
        return False

    entry['count'] += 1
    limits[ip_hash] = entry

    try:
        atomic_write(RATE_LIMIT_FILE, json.dumps(limits))
    except (IOError, OSError):
        pass  # Non-critical: rate limit file write failure

    return True

def application(environ, start_response):
    headers = [
        ('Content-Type', 'text/plain'),
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', 'GET, OPTIONS'),
        ('Cache-Control', 'no-cache'),
    ]

    if environ.get('REQUEST_METHOD') == 'OPTIONS':
        start_response('200 OK', headers)
        return [b'']

    try:
        path = environ.get('PATH_INFO', '/')

        # Serve raw v.txt for historical chart data
        if path == '/v.txt':
            try:
                with open(VIEW_COUNT_FILE, 'r') as f:
                    content = f.read()
                start_response('200 OK', headers)
                return [content.encode('utf-8')]
            except (FileNotFoundError, IOError):
                start_response('404 Not Found', headers)
                return [b'']

        client_ip = get_client_ip(environ)
        ip_hash = hash_ip(client_ip)
        allowed = check_rate_limit(ip_hash)

        data = read_view_data()

        if allowed:
            t = today()
            data[t] = data.get(t, 0) + 1
            write_view_data(data)

        total = sum(data.values())
        start_response('200 OK', headers)
        return [str(total).encode('utf-8')]

    except Exception as e:
        start_response('500 Internal Server Error', headers)
        return [b'Error']