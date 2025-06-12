import math

class Vehicle:
    def __init__(self):
        # Initialize position (x, y) in meters
        self.x = 0
        self.y = 0
        # Heading angle in radians (0 means facing east)
        self.theta = 0
        # Velocity in meters per second
        self.v = 0
        # Wheelbase length in meters (distance between front and rear axles)
        self.L = 2.5
    
    def step(self, delta, a, dt=0.1):
        """
        Update the vehicle's state given steering angle and acceleration.

        Parameters:
        delta : steering angle in radians
        a : acceleration in m/s^2
        dt : time step in seconds
        """
        # Update x position: move forward along current heading
        self.x += self.v * math.cos(self.theta) * dt
        # Update y position similarly
        self.y += self.v * math.sin(self.theta) * dt
        # Update heading angle based on steering and velocity
        self.theta += self.v / self.L * math.tan(delta) * dt
        # Update velocity based on acceleration
        self.v += a * dt
