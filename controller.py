class Controller:
    def __init__(self, vehicle, lts_logger):
        self.vehicle = vehicle
        self.lts_logger = lts_logger
        self.state = 'drive'  # Initial control state

    def control(self, perception_output, obstacle_distance):
        # Basic state transition logic based on perception and distance
        if perception_output == 1 and obstacle_distance < 5:
            next_state = 'emergency brake'
            acceleration = -3.0  # Strong deceleration
        elif perception_output == 1 and obstacle_distance < 10:
            next_state = 'brake'
            acceleration = -1.0  # deceleration
        else:
            next_state = 'drive'
            acceleration = 1.0   # Mild acceleration

        # Steering remains neutral in this simple example
        steering = 0.0

        # Log the transition
        self.lts_logger.log(perception_output, obstacle_distance, next_state)

        # Update controller state
        self.state = next_state

        return steering, acceleration
