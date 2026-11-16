# Cab Pool Matcher - SUTT Backend Task 1

A basic Python terminal app to collect student cab requests and match them with cabs. No extra packages needed.

## Run

Open a terminal in this folder and run (the app also works when launched from another working directory):

```bash
python main.py
```

Menu: **1** Add request, **2** Show waiting students and all cabs, **3** Find matches (preview), **4** Dispatch cab, **5** Quit.

Run the included tests:

```bash
python -m unittest discover -s tests -v
```

## Cab file

`data/cabs.json` has the starting cabs. A cab has a driver, 1-4 seats, a destination (Delhi or Jaipur) and a time slot (Morning, Afternoon, Evening or Night).

Example item:

```json
{"driver": "Ravi", "seats": 4, "destination": "Delhi", "time_slot": "Morning"}
```

Cabs are checked in the order they are written in this file. You can change the sample cab list before starting a new game.

## How it works

- Each destination and time slot has its own waiting priority queue made using Python's `heapq`.
- A queue entry is `(-year, order, student)`. Fifth years have highest priority. For the same year, the smaller request number (earlier submission) wins. Request numbers don't repeat.
- **Find matches** makes copies of the queues and checks open cabs in file order. It doesn't remove anybody or book a seat. A student won't be previewed twice.
- **Dispatch cab** chooses the first open cab for the selected destination and time, fills up to its seat limit, removes those students from the waiting queue, and marks it left. A cab that left cannot take more students.

## Saving between runs (brownie points)

The program stores waiting requests, passengers, cab status, request times, and the next request number in `data/state.json`. It saves **after every added request, every dispatch, and on exit (including Ctrl+C)**. It writes a temporary JSON file and renames it, so an interruption is less likely to damage the previous save.

JSON is easy to read and works with Python's built-in library. If the save is missing or broken, the program prints a message and starts again from `data/cabs.json` instead of crashing. To reset manually, delete `data/state.json`. The save is ignored by Git.

## Tricky situations

1. **Half-empty cab:** It can leave even with just one student. After that, it is permanently marked `Left`.
2. **No cabs left:** New students are still added to their trip's waiting list. The app tells the user no cab is open, and students remain saved.
3. **Same year:** Each request receives an increasing `order` number, which also gets saved. Earlier request wins even after restart.
4. **Nobody waiting:** Dispatch prints a message and does not send the cab.
5. **Bad input:** The app checks student name, city, time slot, year, and seats rather than crashing.

## Big-O complexity

Let **n** = number of waiting requests and **c** = number of cabs.

| Action | Queue / matching work | Including automatic JSON saving |
| --- | --- | --- |
| Add one request | `O(log n)` for heap push | `O(n + c)` to save all data |
| Add 1,000 requests | `O(n log n)` total heap pushes | `O(n² + nc)` total (save after every request) |
| Dispatch one cab (up to 4 students) | `O(c + 4 log n)` = `O(c + log n)` | `O(n + c)` for save too |
| Find first open cab for a trip | `O(c)` scan through cabs | No save |

Match preview copies the waiting queues in `O(n)` and removes up to four preview students per open cab, `O(n + c log n)`. Since there are only eight trip combinations and each cab has at most four seats, these are small operations for this task.

## Files

```text
cab_pool_matcher_basic/
    main.py
    app/
        ride_request.py
        cab.py
    data/
        cabs.json
        state.json  (created automatically)
    tests/
        test_app.py
    .gitignore
    README.md
```

## GitHub

Put this code in a public GitHub repo, make meaningful commits as you develop and test it, and submit your repo link in the form listed in the assignment.
