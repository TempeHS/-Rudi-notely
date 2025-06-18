import math

# Input: all angles in degrees, distances in same units
theta_BA = float(input("enter player 1 angle: "))
c = float(input("enter player 1 distance: "))
theta_CA = float(input("enter player 2 angle: "))
b = float(input("enter player 2 distance: "))

# Convert to radians
theta_BA_rad = math.radians(theta_BA)
theta_CA_rad = math.radians(theta_CA)

# Coordinates
Bx = -c * math.sin(theta_BA_rad)
By = -c * math.cos(theta_BA_rad)
Cx = -b * math.sin(theta_CA_rad)
Cy = -b * math.cos(theta_CA_rad)

# Vector from B to C
dx = Cx - Bx
dy = Cy - By

# Bearing from B to C (in degrees, compass bearing)
bearing_BC = (math.degrees(math.atan2(dx, dy)) + 360) % 360

print("Bearing from player 1 to player 2:", bearing_BC)

print("Bearing from player 2 to player 1:", (bearing_BC + 180) % 360)