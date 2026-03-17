This module provides simulated GPS position data to the flight controller.

The emulator runs on the Raspberry Pi companion computer and sends GPS data using the NMEA protocol over a UART serial connection.

This code inputs pre-determined cordinates, to test if the drone can get a position lock

Position lock should update on Mission Planner map, with all EKF flags on


Protocol: NMEA  
Interface: UART
