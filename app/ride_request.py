from datetime import datetime


class RideRequest:
    def __init__(self, name, destination, time_slot, year, order, submitted_at=None):
        destination = destination.strip().title()
        time_slot = time_slot.strip().title()

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Please enter a student name.")
        if destination not in ("Delhi", "Jaipur"):
            raise ValueError("Destination must be Delhi or Jaipur.")
        if time_slot not in ("Morning", "Afternoon", "Evening", "Night"):
            raise ValueError("Choose Morning, Afternoon, Evening or Night.")
        if type(year) != int or year < 1 or year > 5:
            raise ValueError("Year must be between 1 and 5.")
        if type(order) != int or order < 1:
            raise ValueError("Invalid request number.")

        self.name = name.strip()
        self.destination = destination
        self.time_slot = time_slot
        self.year = year
        self.order = order
        self.submitted_at = submitted_at or datetime.now().isoformat(timespec="seconds")

    def to_dict(self):
        return {
            "name": self.name,
            "destination": self.destination,
            "time_slot": self.time_slot,
            "year": self.year,
            "order": self.order,
            "submitted_at": self.submitted_at
        }
