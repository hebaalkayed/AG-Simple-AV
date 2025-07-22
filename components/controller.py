import random

class Controller:
    def __init__(self, vehicle, lts_builder, velocity_noise=0.2, acceleration_noise=0.5):
        self.vehicle = vehicle
        self.lts_builder = lts_builder
        self.state = 'drive'  # Initial control state
        self.estimated_velocity = 6.0  # Controller's estimate of velocity at starting time is the same as the actual velocity
        self.estimated_acceleration = 0.0  # Controller's estimate of acceleration
        self.velocity_noise = velocity_noise
        self.acceleration_noise = acceleration_noise

    def control(self, perception_output, noisy_obstacle_distance):
    
        if self.vehicle.stopped:
            next_state = 'stopped'
            requested_acceleration = 0.0
        else:
            if perception_output == 1:
                if noisy_obstacle_distance < 3:
                    next_state = 'emergency_brake'
                    requested_acceleration = -8.0 
                elif noisy_obstacle_distance < 6:
                    next_state = 'brake'
                    requested_acceleration = -4.0
                elif noisy_obstacle_distance < 12:
                    next_state = 'coast'
                    requested_acceleration = 0.0
                else:
                    next_state = 'drive'
                    requested_acceleration = 1.0
            else:
                next_state = 'drive'
                requested_acceleration = 1.0

        # Force stop override at the very end, regardless of above logic
        if self.estimated_velocity <= 1e-5:
            requested_acceleration = 0.0
            next_state = 'stopped'
            self.vehicle.stopped = True

        # print(f"[DEBUG] After update: next_state={next_state}")

        steering = 0.0
        # self.lts_builder.log(perception_output, obstacle_distance, next_state)
        # print(f"[DEBUG] Velocity: {self.vehicle.v:.5f}, State: {next_state}, Acceleration: {acceleration}")
        self.state = next_state
        # self.vehicle.requested_acceleration = requested_acceleration

        # Controller's noisy estimate update (could be based on model/prediction)
        self.estimated_acceleration = requested_acceleration + random.uniform(-self.acceleration_noise, self.acceleration_noise)
        self.estimated_velocity += self.estimated_acceleration * self.vehicle.dt
        self.estimated_velocity += random.uniform(-self.velocity_noise, self.velocity_noise)


        self.lts_builder.log_step(
            obs=perception_output,
            dist=noisy_obstacle_distance,
            next_state=self.state,
            est_vel=self.estimated_velocity,
            est_acc=self.estimated_acceleration,
            req_acc=requested_acceleration
        )

        return steering, requested_acceleration