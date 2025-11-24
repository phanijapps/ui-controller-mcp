from __future__ import annotations

import os
from typing import Optional

from pyngrok import ngrok


class NgrokManager:
    def __init__(self, port: int) -> None:
        self.port = port
        self.tunnel: Optional[ngrok.NgrokTunnel] = None

    def start(self) -> Optional[str]:
        token = os.getenv("NGROK_AUTH_TOKEN")
        if not token:
            return None

        ngrok.set_auth_token(token)
        
        # Build connection options
        options = {"bind_tls": True}
        
        # Add domain if specified
        domain = os.getenv("NGROK_DOMAIN")
        if domain:
            options["hostname"] = domain
        
        if self.tunnel is None:
            self.tunnel = ngrok.connect(self.port, **options)
        
        return self.tunnel.public_url

    def stop(self) -> None:
        if self.tunnel:
            ngrok.disconnect(self.tunnel.public_url)
            self.tunnel = None
            ngrok.kill()
