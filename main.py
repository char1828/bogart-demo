import os
import functions_framework
from werkzeug.wrappers import Response, Request
from a2wsgi import ASGIMiddleware
from app.main import app

# Wrap FastAPI ASGI app to WSGI for Cloud Functions compatibility
wsgi_app = ASGIMiddleware(app)

@functions_framework.http
def bogart_demo(request: Request):
    """
    Google Cloud Function HTTP Entry Point for BOGART DEMO.
    Routes all web UI, static asset, and benchmark API traffic to FastAPI.
    """
    environ = dict(request.environ)
    path_info = environ.get("PATH_INFO", "")
    
    # Strip function name prefix if routed via Cloud Functions URL path
    for prefix in ("/bogart-demo", "/bogart_demo"):
        if path_info.startswith(prefix):
            path_info = path_info[len(prefix):]
            if not path_info or not path_info.startswith("/"):
                path_info = "/" + path_info.lstrip("/")
            environ["PATH_INFO"] = path_info
            break
            
    return Response.from_app(wsgi_app, environ)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
