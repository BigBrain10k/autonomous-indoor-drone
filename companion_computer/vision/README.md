# Vision System

This folder contains all software related to camera-based localization for indoor drone flight.

The system uses a downward-facing Raspberry Pi Camera Module 2 to detect ArUco markers and estimate the drone’s position relative to the environment.

All computations are performed on the companion computer (Raspberry Pi).

---

## Overview

The vision pipeline consists of two main stages:

1. Camera Calibration  
2. Pose Estimation  

Camera calibration is required to obtain accurate real-world measurements from the camera.  
Pose estimation then uses these calibration parameters to compute position (X, Y, Z) and orientation (yaw) from detected markers.

---

## Files

### charuco_calibrate_1280.py
Performs camera calibration using a ChArUco board.

- Detects ArUco markers and interpolates ChArUco corners  
- Computes camera intrinsic parameters  
- Outputs:
  - camera_matrix_1280x720.npy  
  - dist_coeffs_1280x720.npy  

This script must be run before pose estimation.

---

### capture_charuco_1280.py
Captures calibration images using the Raspberry Pi camera.

- Resolution: 1280x720  
- Used to generate the dataset for calibration  
- Images should include multiple angles, distances, and positions  

---

### aruco_pose_test.py
Performs real-time ArUco marker detection and pose estimation.

- Detects markers in camera frames  
- Computes:
  - X (left/right position)  
  - Y (forward/backward position)  
  - Z (height)  
  - Yaw (rotation about vertical axis)  

Uses:
- camera_matrix_1280x720.npy  
- dist_coeffs_1280x720.npy  

---

### camera_matrix_1280x720.npy
Camera intrinsic matrix obtained from calibration.

Used to convert image coordinates into real-world measurements.

---

### dist_coeffs_1280x720.npy
Distortion coefficients from calibration.

Used to correct lens distortion for accurate pose estimation.

---

## Important Notes

- Calibration and pose estimation must use the SAME resolution (1280x720)  
- Incorrect resolution will result in inaccurate distance (Z) measurements  
- The correct ArUco dictionary must match the printed markers  

---

## Workflow

1. Capture calibration images  
   → capture_charuco_1280.py  

2. Run calibration  
   → charuco_calibrate_1280.py  

3. Run pose estimation  
   → aruco_pose_test.py  

---

## Future Work

- Send pose data (X, Y, Z, yaw) to the flight controller via MAVLink  
- Improve filtering and stability of pose estimates  
- Integrate vision-based navigation into autonomous flight  

---
