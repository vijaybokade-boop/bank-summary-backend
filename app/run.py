import uvicorn 
import ssl 
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CERTS_DIR = BASE_DIR / "certs"

import sys
sys.path.append(str(BASE_DIR))

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host = "0.0.0.0",
        port = 5001,
        ssl_certfile=str(CERTS_DIR / "server" / "server.crt"),
        ssl_keyfile=str(CERTS_DIR / "server" / "server.key"),
        ssl_ca_certs=str(CERTS_DIR / "ca" / "ca.crt"),
        ssl_cert_reqs=ssl.CERT_REQUIRED,
        reload=True

    )
