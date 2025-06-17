class Controller:
    def __init__(self, vehicle, lts_logger):
        self.vehicle = vehicle
        self.lts_logger = lts_logger
        self.state = 'drive'  # Initial control state

    def control(self, perception_output, obstacle_distance):
        # Multi-level control logic based on obstacle proximity
        if perception_output == 1:
            if obstacle_distance < 3:
                next_state = 'emergency_brake'
                acceleration = -2.0  # Strong deceleration
            elif obstacle_distance < 6:
                next_state = 'brake'
                acceleration = -1.5  # Normal brake
            elif obstacle_distance < 9:
                next_state = 'slow'
                acceleration = -0.5  # Mild deceleration
            elif obstacle_distance < 12:
                next_state = 'coast'
                acceleration = 0.0  # No throttle, no brake
            else:
                next_state = 'drive'
                acceleration = 1.0  # Mild acceleration
        else:
            next_state = 'drive'
            acceleration = 1.0

        # Clamp acceleration to zero if vehicle velocity is zero and acceleration would be negative (braking)
        if self.vehicle.v <= 1e-5 and acceleration < 0:
            acceleration = 0.0

        # Neutral steering
        steering = 0.0

        # Log the transition
        self.lts_logger.log(perception_output, obstacle_distance, next_state)

        # Update controller state
        self.state = next_state

        return steering, acceleration
