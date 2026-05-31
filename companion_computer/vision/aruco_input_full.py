import cv2
import numpy as np
import serial
import time
from datetime import datetime, timezone
from picamera2 import Picamera2


def nmea_checksum(sentence_body: str) -> str:
    checksum = 0
    for char in sentence_body:
        checksum ^= ord(char)
    return f"{checksum:02X}"


def build_nmea(sentence_body: str) -> str:
    return f"${sentence_body}*{nmea_checksum(sentence_body)}\r\n"


def format_lat(lat_deg: float):
    hemisphere = 'N' if lat_deg >= 0 else 'S'
    lat_abs = abs(lat_deg)
    degrees = int(lat_abs)
    minutes = (lat_abs - degrees) * 60
    return f"{degrees:02d}{minutes:07.4f}", hemisphere


def format_lon(lon_deg: float):
    hemisphere = 'E' if lon_deg >= 0 else 'W'
    lon_abs = abs(lon_deg)
    degrees = int(lon_abs)
    minutes = (lon_abs - degrees) * 60
    return f"{degrees:03d}{minutes:07.4f}", hemisphere


def build_gga(lat: float, lon: float, altitude_m: float, satellites: int = 10, hdop: float = 1.0):
    now = datetime.now(timezone.utc)
    utc_str = now.strftime("%H%M%S") + f".{int(now.microsecond / 10000):02d}"

    lat_nmea, lat_hemi = format_lat(lat)
    lon_nmea, lon_hemi = format_lon(lon)

    body = (
        f"GPGGA,{utc_str},{lat_nmea},{lat_hemi},{lon_nmea},{lon_hemi},"
        f"1,{satellites:02d},{hdop:.1f},{altitude_m:.1f},M,0.0,M,,"
    )
    return build_nmea(body)


def knots_from_mps(speed_mps: float) -> float:
    return speed_mps * 1.94384


def build_rmc(lat: float, lon: float, speed_mps: float = 0.0, course_deg: float = 0.0):
    now = datetime.now(timezone.utc)
    utc_str = now.strftime("%H%M%S") + f".{int(now.microsecond / 10000):02d}"
    date_str = now.strftime("%d%m%y")

    lat_nmea, lat_hemi = format_lat(lat)
    lon_nmea, lon_hemi = format_lon(lon)

    speed_knots = knots_from_mps(speed_mps)

    body = (
        f"GPRMC,{utc_str},A,{lat_nmea},{lat_hemi},{lon_nmea},{lon_hemi},"
        f"{speed_knots:.2f},{course_deg:.2f},{date_str},,"
    )
    return build_nmea(body)


def build_hdt(heading_deg: float):
    heading_deg = heading_deg % 360.0
    body = f"GPHDT,{heading_deg:.2f},T"
    return build_nmea(body)


def meters_to_latlon(east_m: float, north_m: float, lat0_deg: float, lon0_deg: float):
    dlat = north_m / 111320.0
    dlon = east_m / (111320.0 * np.cos(np.radians(lat0_deg)))
    lat = lat0_deg + dlat
    lon = lon0_deg + dlon
    return lat, lon


# Load calibration
camera_matrix = np.load("camera_matrix_1280x720.npy")
dist_coeffs = np.load("dist_coeffs_1280x720.npy")

# Printed marker
marker_length = 0.185  # meters
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
detector_params = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, detector_params)

# Serial output to FC
ser = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=1)

# Fixed indoor origin (same known-good origin as before)
lat0 = 44.2312
lon0 = -76.4860
altitude_m = 100.0

# Optional simple smoothing for x/y
alpha = 0.2
filtered_x = None
filtered_y = None

# Start camera
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"size": (1280, 720), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()

print("Press q to quit.")

last_send_time = 0.0
send_period = 0.2  # 5 Hz

try:
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

            # Use only the first detected marker
            rvec = rvecs[0][0]
            tvec = tvecs[0][0]
            marker_id = int(ids[0][0])

            x, y, z = tvec

            # Smooth x and y a bit
            if filtered_x is None:
                filtered_x = float(x)
                filtered_y = float(y)
            else:
                filtered_x = (1 - alpha) * filtered_x + alpha * float(x)
                filtered_y = (1 - alpha) * filtered_y + alpha * float(y)

            # First-pass local mapping
            east_m = filtered_x
            north_m = -filtered_y

            # Convert local offsets to fake GPS
            lat, lon = meters_to_latlon(east_m, north_m, lat0, lon0)

            # Convert rotation vector to rotation matrix
            R_marker_to_cam, _ = cv2.Rodrigues(rvec)

            # Extract yaw
            yaw_rad = np.arctan2(R_marker_to_cam[1, 0], R_marker_to_cam[0, 0])
            yaw_deg = np.degrees(yaw_rad) % 360.0

            # Draw axes
            cv2.drawFrameAxes(display, camera_matrix, dist_coeffs, rvec, tvec, 0.08)

            text1 = f"ID {marker_id} X={x:.2f} Y={y:.2f} Z={z:.2f}"
            text2 = f"Yaw={yaw_deg:.1f} East={east_m:.2f} North={north_m:.2f}"

            c = corners[0][0]
            px = int(c[0][0])
            py = int(c[0][1]) - 10

            cv2.putText(
                display,
                text1,
                (px, max(py, 30)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
                cv2.LINE_AA
            )

            cv2.putText(
                display,
                text2,
                (px, max(py + 25, 55)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2,
                cv2.LINE_AA
            )

            now = time.time()
            if now - last_send_time >= send_period:
                gga = build_gga(lat, lon, altitude_m, satellites=10, hdop=0.9)
                rmc = build_rmc(lat, lon, speed_mps=0.0, course_deg=0.0)
                hdt = build_hdt(yaw_deg)

                ser.write(gga.encode("ascii"))
                ser.write(rmc.encode("ascii"))
                ser.write(hdt.encode("ascii"))

                print(
                    f"ID {marker_id} | "
                    f"X={x:.3f} m Y={y:.3f} m Z={z:.3f} m | "
                    f"East={east_m:.3f} m North={north_m:.3f} m | "
                    f"Lat={lat:.7f} Lon={lon:.7f} | "
                    f"Yaw={yaw_deg:.2f} deg"
                )
                print(gga.strip())
                print(rmc.strip())
                print(hdt.strip())
                print("-" * 60)

                last_send_time = now

        cv2.imshow("ArUco Pose Yaw + Position Test", cv2.cvtColor(display, cv2.COLOR_RGB2BGR))

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    picam2.stop()
    cv2.destroyAllWindows()
    ser.close()
