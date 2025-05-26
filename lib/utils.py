# lib/utils.py
from urllib.parse import urlencode
from flask import current_app

def frontend_url_for(route_key, **params):
    """Generate full frontend URLs safely"""
    base = current_app.config['FRONTEND_BASE_URL'].rstrip('/')
    path = current_app.config['FRONTEND_ROUTES'].get(route_key, '/').lstrip('/')
    
    url = f"{base}/{path}"
    
    if params:
        return f"{url}?{urlencode(params)}"
    return url