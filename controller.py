class Controller:
    def __init__(self, vehicle, lts_logger):
        self.vehicle = vehicle
        self.safe_distance = 10
        self.lts_logger = lts_logger

    def control(self, perception_output, obstacle_distance):
        if perception_output == 1 and obstacle_distance < self.safe_distance:
            next_state = 'brake'
            acceleration = -5.0
            steering = 0.0
        else:
            next_state = 'drive'
            acceleration = 1.0
            steering = 0.0

        self.lts_logger.log(perception_output, obstacle_distance, next_state)
        return steering, acceleration
