import serial
import time
from datetime import datetime, timezone


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
    """
    HDT = Heading, True
    Example:
    $GPHDT,90.00,T*XX
    """
    heading_deg = heading_deg % 360.0
    body = f"GPHDT,{heading_deg:.2f},T"
    return build_nmea(body)


def main():
    port = "/dev/ttyUSB0"
    baud = 9600

    # Fixed test position
    lat = 44.2312
    lon = -76.4860
    altitude_m = 100.0

    # Fixed heading for yaw test
    heading_deg = 90.0

    ser = serial.Serial(port, baudrate=baud, timeout=1)

    print(f"Sending NMEA to {port} at {baud} baud...")
    print("Now sending GGA + RMC + HDT")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            gga = build_gga(lat, lon, altitude_m, satellites=10, hdop=0.9)
            rmc = build_rmc(lat, lon, speed_mps=0.0, course_deg=0.0)
            hdt = build_hdt(heading_deg)

            ser.write(gga.encode("ascii"))
            ser.write(rmc.encode("ascii"))
            ser.write(hdt.encode("ascii"))

            print(gga.strip())
            print(rmc.strip())
            print(hdt.strip())
            print("-" * 50)

            time.sleep(0.2)   # 5 Hz
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        ser.close()


if __name__ == "__main__":
    main()


