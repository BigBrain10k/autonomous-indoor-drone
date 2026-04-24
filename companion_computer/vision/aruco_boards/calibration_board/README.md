# ChArUco Calibration Board

This folder contains the ChArUco board PDF used for camera calibration.

## Purpose

The calibration board is used to calculate the camera intrinsic matrix and distortion coefficients.

## Output Files

Running camera calibration produces:

- camera_matrix_1280x720.npy
- dist_coeffs_1280x720.npy

## Notes

- Print the PDF without scaling.
- Use the same camera resolution for calibration and pose estimation.
- The current vision system uses 1280x720.
