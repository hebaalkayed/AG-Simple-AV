class Controller:
    def __init__(self, vehicle, lts_logger):
        self.vehicle = vehicle
        self.lts_logger = lts_logger
        self.state = 'drive'  # Initial control state
        
    def control(self, perception_output, obstacle_distance):
        # print(f"[DEBUG] Before update: current_state={self.state}")
        if self.vehicle.stopped:
            next_state = 'stopped'
            acceleration = 0.0
        else:
            if perception_output == 1:
                if obstacle_distance < 3:
                    next_state = 'emergency_brake'
                    acceleration = -2.0
                elif obstacle_distance < 6:
                    next_state = 'brake'
                    acceleration = -0.5
                elif obstacle_distance < 12:
                    next_state = 'coast'
                    acceleration = 0.0
                else:
                    next_state = 'drive'
                    acceleration = 1.0
            else:
                next_state = 'drive'
                acceleration = 1.0

        # Force stop override at the very end, regardless of above logic
        if self.vehicle.v <= 1e-5:
            acceleration = 0.0
            next_state = 'stopped'
            self.vehicle.stopped = True

        # print(f"[DEBUG] After update: next_state={next_state}")

        steering = 0.0
        # self.lts_logger.log(perception_output, obstacle_distance, next_state)
        # print(f"[DEBUG] Velocity: {self.vehicle.v:.5f}, State: {next_state}, Acceleration: {acceleration}")
        self.state = next_state
        
        self.lts_logger.log_step(perception_output, obstacle_distance, self.state)
        return steering, acceleration

