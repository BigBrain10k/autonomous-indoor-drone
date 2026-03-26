import cv2
import numpy as np
from picamera2 import Picamera2


# Load calibration
camera_matrix = np.load("camera_matrix_1280x720.npy")
dist_coeffs = np.load("dist_coeffs_1280x720.npy")


# printed marker
marker_length = 0.185  # meters
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
detector_params = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, detector_params)
#to start camera
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"size": (1280, 720), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()

print("Press q to quit.")

while True:
    frame = picam2.capture_array()
    display = frame.copy()

    corners, ids, _ = detector.detectMarkers(frame)

    if ids is not None and len(ids) > 0:
        cv2.aruco.drawDetectedMarkers(display, corners, ids)

        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
            corners,
            marker_length,
            camera_matrix,
            dist_coeffs
        )

        for i in range(len(ids)):
            rvec = rvecs[i][0]
            tvec = tvecs[i][0]

            x, y, z = tvec
            marker_id = int(ids[i][0])

            cv2.drawFrameAxes(display, camera_matrix, dist_coeffs, rvec, tvec, 0.08)

            text = f"ID {marker_id} X={x:.2f} Y={y:.2f} Z={z:.2f} m"
            c = corners[i][0]
            px = int(c[0][0])
            py = int(c[0][1]) - 10

            cv2.putText(
                display,
                text,
                (px, max(py, 30)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
                cv2.LINE_AA
            )

            print(f"ID {marker_id} | X={x:.3f} m  Y={y:.3f} m  Z={z:.3f} m")

    cv2.imshow("ArUco Pose Test", cv2.cvtColor(display, cv2.COLOR_RGB2BGR))

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

picam2.stop()
cv2.destroyAllWindows()
