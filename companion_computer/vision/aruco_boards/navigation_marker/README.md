# ArUco Navigation Marker

This folder contains the ArUco marker PDF used for real-time pose estimation.

## Marker Details

- Dictionary: DICT_6X6_50
- Marker ID: 0
- Marker size: 0.185 m / 18.5 cm

## Purpose

This marker is detected by the downward-facing Raspberry Pi camera to estimate the drone's position relative to the marker.

The pose estimation script uses this marker to estimate:

- X position
- Y position
- Z height
- yaw angle

## Important

The printed marker size must match the value in the code:

```python
marker_length = 0.185
