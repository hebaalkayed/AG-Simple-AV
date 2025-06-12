class Controller:
    def __init__(self, vehicle):
        # Keep reference to the vehicle being controlled
        self.vehicle = vehicle
        # Minimum safe distance (in meters) to obstacle to trigger braking
        self.safe_distance = 10
    
    def control(self, perception_output, obstacle_distance):
        """
        Decide on steering and acceleration commands based on perception and obstacle distance.

        Parameters:
        perception_output : 0 (no obstacle) or 1 (obstacle detected)
        obstacle_distance : float, distance to obstacle in meters

        Returns:
        steering (float): steering angle in radians
        acceleration (float): acceleration in m/s^2
        """
        # If obstacle detected AND too close, apply emergency brake
        if perception_output == 1 and obstacle_distance < self.safe_distance:
            acceleration = -5.0  # strong deceleration (braking)
            steering = 0.0       # keep steering straight for simplicity
        else:
            acceleration = 1.0   # accelerate forward
            steering = 0.0       # keep steering straight
        
        return steering, acceleration
