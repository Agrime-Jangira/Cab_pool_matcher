class Cab:
    def __init__(self, driver, seats, destination, time_slot):
        if not isinstance(driver, str) or not driver.strip():
            raise ValueError("Driver name cannot be empty.")
        if type(seats) != int or not 1 <= seats <= 4:
            raise ValueError("Seats must be from 1 to 4.")
        if destination not in ("Delhi", "Jaipur"):
            raise ValueError("Invalid cab destination.")
        if time_slot not in ("Morning", "Afternoon", "Evening", "Night"):
            raise ValueError("Invalid cab time slot.")

        self.driver = driver
        self.seats = seats
        self.destination = destination
        self.time_slot = time_slot
        self.students = []
        self.left = False

    def to_dict(self):
        return {
            "driver": self.driver,
            "seats": self.seats,
            "destination": self.destination,
            "time_slot": self.time_slot,
            "students": [student.to_dict() for student in self.students],
            "left": self.left
        }
