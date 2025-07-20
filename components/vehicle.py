import math

class Vehicle:
    def __init__(self, lts_builder): 
        self.x = 0.0  # 2D - position
        self.y = 0.0  # 2D - position
        self.theta = 0.0  # heading angle
        self.actual_velocity = 6.0  # actual velocity
        self.L = 2.5  # vehicle wheelbase
        self.dt = 0.1  # simulation time step
        self.actual_acceleration = 0.0  # actual acceleration of the vehicle
        self.requested_acceleration = 0.0  # what the controller requested
        self.stopped = False
        self.lts_builder = lts_builder

    def get_state(self, quantize=2):
        """Return current state as rounded tuple."""
        return (
            round(self.x, quantize),
            round(self.y, quantize),
            round(self.theta, quantize),
            round(self.actual_velocity, quantize)
        )

    def step(self, delta, acceleration_from_controller, dt=None):
        """
        Update the vehicle's state using steering angle and acceleration.
        """
        # Get vehicle state before stepping
        current_state = self.get_state()
        # print("heba ", current_state)

        if self.stopped:
            self.actual_acceleration = 0.0
            return

        if dt is None:
            dt = self.dt

        self.requested_acceleration = acceleration_from_controller

        # Apply first-order lag model: actual_acceleration slowly tracks requested
        alpha = 0.5  # responsiveness factor (between 0 and 1)
        self.actual_acceleration += alpha * (self.requested_acceleration - self.actual_acceleration)

        # Update velocity with actual acceleration
        self.actual_velocity += self.actual_acceleration * dt

        # Prevent negative velocity (real vehicles can’t go backward in this model)
        if self.actual_velocity < 0.0:
            self.actual_velocity = 0.0

        # Mark vehicle as stopped if nearly stationary
        if self.actual_velocity <= 1e-5:
            self.actual_velocity = 0.0
            self.stopped = True
            self.actual_acceleration = 0.0
            return

        # Update position based on current heading and new velocity
        self.x += self.actual_velocity * math.cos(self.theta) * dt
        self.y += self.actual_velocity * math.sin(self.theta) * dt

        # Get vehicle state after stepping
        next_state = self.get_state()

        self.lts_builder.log_step(
            s1=current_state,
            delta=delta,
            acceleration=self.actual_acceleration,
            s2=next_state,
            act_vel=self.actual_velocity,
            req_acc=self.requested_acceleration
        )

