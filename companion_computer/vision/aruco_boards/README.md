# ArUco Boards

This folder contains the printable boards and markers used by the vision system.

## calibration_board

Contains the ChArUco board used for camera calibration.

This board is used to generate:

- camera_matrix_1280x720.npy
- dist_coeffs_1280x720.npy

## navigation_marker

Contains the ArUco marker used for real-time position and yaw estimation.

The marker is used to estimate:

- X position
- Y position
- Z height
- yaw angle

## Important Notes

The printed board or marker size must match the values used in the vision code.

Incorrect print scaling will cause inaccurate position and height estimates.
