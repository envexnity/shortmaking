"""
studio_frame_server.py — Local HTTP receiver on 127.0.0.1:8765 that accepts raw RGBA buffers
captured inside Roblox Studio via CaptureService + AssetService:CreateEditableImageAsync + ReadPixelsBuffer
and writes them directly to studio_frames/f_####.png.
"""
import os
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import numpy as np
import cv2

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, "studio_frames")
os.makedirs(OUT_DIR, exist_ok=True)


class FrameHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        f_idx = int(qs.get("f", ["1"])[0])
        w = int(qs.get("w", ["405"])[0])
        h = int(qs.get("h", ["720"])[0])
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)

        expected = w * h * 4
        if len(raw) == expected:
            arr = np.frombuffer(raw, dtype=np.uint8).reshape((h, w, 4))
            bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
            out_p = os.path.join(OUT_DIR, f"f_{f_idx:04d}.png")
            cv2.imwrite(out_p, bgr)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"Bad length {len(raw)} != {expected}".encode("utf-8"))

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8765), FrameHandler)
    print(f"[OK] Studio Frame Server listening on http://127.0.0.1:8765 -> {OUT_DIR}", flush=True)
    server.serve_forever()
