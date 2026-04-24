# snapshot.py — run this separately to debug colour detection
# Press SPACE to save a snapshot with detection overlay, Q to quit
# Pull the saved image with: scp fri@<pi-ip>:~/Group3_ReactionWheel_Sp26/snapshot.jpg .

import cv2
import numpy as np
from picamera2 import Picamera2
import time
import sys
import tty
import termios
import threading

FRAME_WIDTH  = 640
FRAME_HEIGHT = 480
SAVE_PATH    = "/home/fri/Group3_ReactionWheel_Sp26/snapshot.jpg"

# ── Copy your HSV values from the main script ─────────────────────────────────
HSV_LOWER = np.array([ 40, 120, 120], dtype=np.uint8)
HSV_UPPER = np.array([ 75, 255, 255], dtype=np.uint8)
DETECT_RED   = False
HSV_LOWER_R1 = np.array([  0,  80,  80], dtype=np.uint8)
HSV_UPPER_R1 = np.array([ 10, 255, 255], dtype=np.uint8)
HSV_LOWER_R2 = np.array([160,  80,  80], dtype=np.uint8)
HSV_UPPER_R2 = np.array([179, 255, 255], dtype=np.uint8)
MIN_RECT_AREA = 2000
CENTRE_TOL_X  = 0.30
CENTRE_TOL_Y  = 0.30

_frame_cx = FRAME_WIDTH  // 2
_frame_cy = FRAME_HEIGHT // 2
_cx_tol   = int(FRAME_WIDTH  * CENTRE_TOL_X)
_cy_tol   = int(FRAME_HEIGHT * CENTRE_TOL_Y)

# ── Camera init ───────────────────────────────────────────────────────────────
picam = Picamera2()
picam.configure(picam.create_preview_configuration(
    main={"format": "BGR888", "size": (FRAME_WIDTH, FRAME_HEIGHT)}
))
picam.start()
time.sleep(1)

# ── Keypress detection (non-blocking, works over SSH) ─────────────────────────
_key_pressed = None

def _read_keys():
    global _key_pressed
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while True:
            ch = sys.stdin.read(1)
            _key_pressed = ch
            if ch == 'q':
                break
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

key_thread = threading.Thread(target=_read_keys, daemon=True)
key_thread.start()

# ── Detection overlay ─────────────────────────────────────────────────────────
def annotate(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    if DETECT_RED:
        m1   = cv2.inRange(hsv, HSV_LOWER_R1, HSV_UPPER_R1)
        m2   = cv2.inRange(hsv, HSV_LOWER_R2, HSV_UPPER_R2)
        mask = cv2.bitwise_or(m1, m2)
    else:
        mask = cv2.inRange(hsv, HSV_LOWER, HSV_UPPER)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask   = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel)
    mask   = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

    # Draw centre tolerance box
    cv2.rectangle(frame,
                  (_frame_cx - _cx_tol, _frame_cy - _cy_tol),
                  (_frame_cx + _cx_tol, _frame_cy + _cy_tol),
                  (180, 180, 180), 1)
    cv2.drawMarker(frame, (_frame_cx, _frame_cy),
                   (255, 255, 255), cv2.MARKER_CROSS, 20, 1)

    best_rect = None
    best_area = 0
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        if area < MIN_RECT_AREA:
            continue
        # Draw all candidates in yellow
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 200, 255), 1)
        if area > best_area:
            best_area = area
            best_rect = (x, y, w, h)

    status = "NO DETECTION"
    colour = (0, 0, 255)

    if best_rect is not None:
        x, y, w, h = best_rect
        rect_cx = x + w // 2
        rect_cy = y + h // 2
        in_centre = (abs(rect_cx - _frame_cx) <= _cx_tol and
                     abs(rect_cy - _frame_cy) <= _cy_tol)

        if in_centre:
            colour = (0, 255, 0)
            status = f"LOCKED  {w}x{h}px  area={best_area}px²"
        else:
            colour = (0, 165, 255)
            status = f"FOUND NOT CENTRED  {w}x{h}px  area={best_area}px²"

        cv2.rectangle(frame, (x, y), (x+w, y+h), colour, 2)
        cv2.putText(frame, status, (x, max(y-8, 12)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, colour, 2)

        # Print centre HSV of the detected rectangle for tuning
        roi_hsv = hsv[y:y+h, x:x+w]
        avg_h = int(np.mean(roi_hsv[:,:,0]))
        avg_s = int(np.mean(roi_hsv[:,:,1]))
        avg_v = int(np.mean(roi_hsv[:,:,2]))
        print(f"  Detected rect HSV avg: H={avg_h}  S={avg_s}  V={avg_v}")

    # Print centre-pixel HSV regardless
    cx_hsv = hsv[_frame_cy-5:_frame_cy+5, _frame_cx-5:_frame_cx+5]
    ch = int(np.mean(cx_hsv[:,:,0]))
    cs = int(np.mean(cx_hsv[:,:,1]))
    cv2.putText(frame, status if best_rect is None else "",
                (10, FRAME_HEIGHT - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, colour, 1)
    cv2.putText(frame, f"Centre HSV: H={ch} S={cs}",
                (10, FRAME_HEIGHT - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

    return frame

# ── Main loop ─────────────────────────────────────────────────────────────────
print("Running. Press SPACE to save snapshot, Q to quit.")
print(f"Snapshots saved to: {SAVE_PATH}")
print(f"Pull with: scp fri@<pi-ip>:{SAVE_PATH} .\n")

snap_count = 0
try:
    while True:
        frame = picam.capture_array()
        annotated = annotate(frame.copy())

        key = _key_pressed
        _key_pressed = None

        if key == ' ':
            cv2.imwrite(SAVE_PATH, annotated)
            snap_count += 1
            print(f"  Snapshot {snap_count} saved → {SAVE_PATH}")
        elif key == 'q':
            print("Quitting.")
            break

        time.sleep(0.05)   # ~20 fps capture rate

finally:
    picam.stop()
    print("Done.")