import cv2
import cv2.aruco as aruco
import numpy as np
import glob
import os

image_dir = "/home/henry/charuco_1280"
image_paths = sorted(glob.glob(os.path.join(image_dir, "*.jpg")))

# BOARD SETTINGS 
squaresX = 10
squaresY = 7

squareLength = 0.024
markerLength = 0.018

dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
board = aruco.CharucoBoard((squaresX, squaresY), squareLength, markerLength, dictionary)

all_charuco_corners = []
all_charuco_ids = []
image_size = None

detector_params = aruco.DetectorParameters()

accepted = 0

for path in image_paths:
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if image_size is None:
        image_size = gray.shape[::-1]

    corners, ids, _ = aruco.detectMarkers(gray, dictionary, parameters=detector_params)

    if ids is not None and len(ids) > 0:
        retval, charuco_corners, charuco_ids = aruco.interpolateCornersCharuco(
            markerCorners=corners,
            markerIds=ids,
            image=gray,
            board=board
        )

        if retval is not None and retval >= 6:
            all_charuco_corners.append(charuco_corners)
            all_charuco_ids.append(charuco_ids)
            accepted += 1
            print(f"Accepted: {path}")
        else:
            print(f"Rejected: {path}")
    else:
        print(f"Rejected: {path}")

print(f"\nTotal accepted images: {accepted}")

ret, camera_matrix, dist_coeffs, _, _ = aruco.calibrateCameraCharuco(
    charucoCorners=all_charuco_corners,
    charucoIds=all_charuco_ids,
    board=board,
    imageSize=image_size,
    cameraMatrix=None,
    distCoeffs=None
)

print("\nRMS error:", ret)
print("\nCamera matrix:\n", camera_matrix)
print("\nDistortion coeffs:\n", dist_coeffs)

np.save("camera_matrix_1280x720.npy", camera_matrix)
np.save("dist_coeffs_1280x720.npy", dist_coeffs)
