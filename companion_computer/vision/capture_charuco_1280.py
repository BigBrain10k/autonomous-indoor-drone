import cv2
import os
from picamera2 import Picamera2

save_dir = "/home/henry/charuco_1280"
os.makedirs(save_dir, exist_ok=True)

picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"size": (1280, 720), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()

count = 0
print("Press SPACE to save image")
print("Press Q to quit")

while True:
    frame = picam2.capture_array()
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    display = frame_bgr.copy()
    cv2.putText(display, f"Saved: {count}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("ChArUco Capture 1280x720", display)
    key = cv2.waitKey(1) & 0xFF

    if key == ord(' '):
        filename = os.path.join(save_dir, f"img_{count:02d}.jpg")
        cv2.imwrite(filename, frame_bgr)
        print(f"Saved {filename}")
        count += 1

    elif key == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()
