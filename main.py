import heapq
import json
import os

from app.cab import Cab
from app.ride_request import RideRequest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CABS_FILE = os.path.join(BASE_DIR, "data", "cabs.json")
SAVE_FILE = os.path.join(BASE_DIR, "data", "state.json")
CITIES = ("Delhi", "Jaipur")
TIMES = ("Morning", "Afternoon", "Evening", "Night")
 

def make_queues():
    queues = {}
    for city in CITIES:
        for time in TIMES:
            queues[(city, time)] = []
    return queues


def add_to_queue(queues, student):
    trip = (student.destination, student.time_slot)
    heapq.heappush(queues[trip], (-student.year, student.order, student))


def load_data():
    with open(CABS_FILE, "r") as file:
        cab_info = json.load(file)
    cabs = [Cab(**item) for item in cab_info]
    queues = make_queues()

    if not os.path.exists(SAVE_FILE):
        print("No save found. Starting fresh.")
        return cabs, queues, 1

    try:
        with open(SAVE_FILE, "r") as file:
            data = json.load(file)

        saved_cabs = []
        used_orders = set()
        for item in data["cabs"]:
            cab = Cab(item["driver"], item["seats"], item["destination"], item["time_slot"])
            if type(item["left"]) != bool:
                raise ValueError("Bad cab status")
            cab.left = item["left"]
            for student_data in item["students"]:
                student = RideRequest(**student_data)
                if student.order in used_orders or (student.destination, student.time_slot) != (cab.destination, cab.time_slot):
                    raise ValueError("Bad saved passenger")
                used_orders.add(student.order)
                cab.students.append(student)
            if len(cab.students) > cab.seats or (cab.students and not cab.left):
                raise ValueError("Bad saved cab")
            saved_cabs.append(cab)

        for item in data["waiting"]:
            student = RideRequest(**item)
            if student.order in used_orders:
                raise ValueError("Repeated request number")
            used_orders.add(student.order)
            add_to_queue(queues, student)

        next_order = max(used_orders, default=0) + 1
        if type(data["next_order"]) != int or data["next_order"] < 1:
            raise ValueError("Bad counter")
        next_order = max(next_order, data["next_order"])
        print("Previous data loaded.")
        return saved_cabs, queues, next_order
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        print("Save file is broken. Starting fresh.")
        return cabs, make_queues(), 1


def save_data(cabs, queues, next_order):
    waiting = []
    for queue in queues.values():
        for item in queue:
            waiting.append(item[2].to_dict())

    data = {
        "cabs": [cab.to_dict() for cab in cabs],
        "waiting": waiting,
        "next_order": next_order
    }
    try:
        with open(SAVE_FILE + ".tmp", "w") as file:
            json.dump(data, file, indent=2)
        os.replace(SAVE_FILE + ".tmp", SAVE_FILE)
    except OSError as error:
        print("Could not save data:", error)


def find_cab(cabs, trip):
    for cab in cabs:
        if not cab.left and (cab.destination, cab.time_slot) == trip:
            return cab
    return None


def show_all(cabs, queues):
    print("\nWAITING STUDENTS")
    if not any(queues.values()):
        print("Nobody is waiting.")
    for trip, queue in queues.items():
        for _, _, student in sorted(queue):
            print(f"{student.name} | Year {student.year} | {trip[0]} | {trip[1]} | {student.submitted_at}")

    print("\nCABS")
    for cab in cabs:
        status = "Left" if cab.left else "Open"
        names = ", ".join(student.name for student in cab.students) or "None"
        print(f"{cab.driver} | {cab.destination} | {cab.time_slot} | "
              f"{len(cab.students)}/{cab.seats} seats | {status} | {names}")


def find_matches(cabs, queues):
    copy_queues = {}
    for trip in queues:
        copy_queues[trip] = queues[trip].copy()

    print("\nMATCH PREVIEW")
    for cab in cabs:
        if cab.left:
            continue
        trip = (cab.destination, cab.time_slot)
        names = []
        for _ in range(cab.seats - len(cab.students)):
            if not copy_queues[trip]:
                break
            names.append(heapq.heappop(copy_queues[trip])[2].name)
        print(f"{cab.driver} ({trip[0]}, {trip[1]}): {', '.join(names) or 'No matches'}")

    for trip in queues:
        if queues[trip] and find_cab(cabs, trip) is None:
            print(f"No cab for {trip[0]}, {trip[1]}. Those students stay waiting.")


def dispatch(cabs, queues, trip):
    cab = find_cab(cabs, trip)
    if cab is None:
        print("No open cab for this trip. Students stay waiting.")
        return False
    if not queues[trip]:
        print("Nobody is waiting for this trip.")
        return False

    while queues[trip] and len(cab.students) < cab.seats:
        student = heapq.heappop(queues[trip])[2]
        cab.students.append(student)
    cab.left = True
    print(f"{cab.driver}'s cab has left with {len(cab.students)} student(s).")
    return True


def ask_trip():
    city = input("Destination (Delhi/Jaipur): ").strip().title()
    time = input("Time (Morning/Afternoon/Evening/Night): ").strip().title()
    if city not in CITIES or time not in TIMES:
        print("Invalid destination or time slot.")
        return None
    return (city, time)


def main():
    try:
        cabs, queues, next_order = load_data()
    except (OSError, ValueError, TypeError, KeyError):
        print("Problem with data/cabs.json. Please check the cab file.")
        return

    try:
        while True:
            print("\n1. Add request\n2. Show students and cabs\n3. Find matches")
            print("4. Dispatch cab\n5. Quit")
            choice = input("Enter choice: ").strip()

            if choice == "1":
                name = input("Student name: ")
                trip = ask_trip()
                if trip is None:
                    continue
                try:
                    year = int(input("Year (1-5): "))
                    student = RideRequest(name, trip[0], trip[1], year, next_order)
                except ValueError as error:
                    print("Invalid request:", error)
                    continue
                add_to_queue(queues, student)
                next_order += 1
                save_data(cabs, queues, next_order)
                print("Request added to the waiting list.")
                if find_cab(cabs, trip) is None:
                    print("No open cab for this trip. Your request is still saved.")

            elif choice == "2":
                show_all(cabs, queues)
            elif choice == "3":
                find_matches(cabs, queues)
            elif choice == "4":
                trip = ask_trip()
                if trip and dispatch(cabs, queues, trip):
                    save_data(cabs, queues, next_order)
            elif choice == "5":
                print("Goodbye!")
                break
            else:
                print("Please choose 1 to 5.")
    except (KeyboardInterrupt, EOFError):
        print("\nApp closed.")
    finally:
        save_data(cabs, queues, next_order)


if __name__ == "__main__":
    main()
