"""Schedule meeting rooms and equipment while recording booking conflicts."""

import json
from collections import Counter
from datetime import datetime
from pathlib import Path


DEFAULT_EQUIPMENT = {"projector": 2, "microphone": 4, "webcam": 1}


def slot_hours(time_slot: str) -> int:
    """Return the duration of a slot such as ``09-11`` in hours."""
    parts = time_slot.split("-")
    if len(parts) != 2:
        raise ValueError("A time slot must use the HH-HH format.")

    try:
        start, end = (int(part) for part in parts)
    except ValueError as error:
        raise ValueError("Time slot hours must be whole numbers.") from error

    if not 0 <= start < 24 or not 0 < end <= 24 or end <= start:
        raise ValueError("A time slot must end after it starts in one day.")
    return end - start


class Scheduler:
    """Manage room reservations, equipment stock, and conflict logs."""

    def __init__(self) -> None:
        self.reservations: dict[int, dict[str, object]] = {}
        self.equipment_pool = DEFAULT_EQUIPMENT.copy()
        self.conflicts: list[str] = []
        self.next_reservation_id = 1

    def schedule_room(
        self,
        room_id: str,
        time_slot: str,
        equipment_list: list[str] | None = None,
    ) -> int:
        """Book a room with equipment and return its reservation ID."""
        slot_hours(time_slot)
        requested_equipment = list(equipment_list or [])
        requested_counts = Counter(requested_equipment)

        for equipment, quantity in requested_counts.items():
            available = self.equipment_pool.get(equipment)
            if available is None or quantity > available:
                message = f"Not enough {equipment} equipment is available."
                raise ValueError(message)

        for reservation in self.reservations.values():
            if (
                reservation["room"] == room_id
                and reservation["slot"] == time_slot
            ):
                message = f"{room_id} double-booked at {time_slot}"
                self.conflicts.append(message)

        for equipment, quantity in requested_counts.items():
            self.equipment_pool[equipment] -= quantity

        reservation_id = self.next_reservation_id
        self.reservations[reservation_id] = {
            "room": room_id,
            "slot": time_slot,
            "equipment": requested_equipment,
        }
        self.next_reservation_id += 1
        return reservation_id

    def cancel_reservation(self, reservation_id: int) -> bool:
        """Cancel a reservation and restore its equipment, if it exists."""
        reservation = self.reservations.pop(reservation_id, None)
        if reservation is None:
            return False

        for equipment in reservation["equipment"]:
            self.equipment_pool[equipment] += 1
        return True

    def export_schedule(self, file: str = "schedule.json") -> None:
        """Write current reservations to a UTF-8 JSON file."""
        with Path(file).open("w", encoding="utf-8") as schedule_file:
            json.dump(self.reservations, schedule_file, indent=2)

    def log_conflicts(self, file: str = "conflicts.log") -> None:
        """Append conflicts to a log and print its contents without a shell."""
        with Path(file).open("a", encoding="utf-8") as conflict_file:
            for conflict in self.conflicts:
                conflict_file.write(f"{datetime.now()} {conflict}\n")
        print(Path(file).read_text(encoding="utf-8"), end="")


def main() -> None:
    """Run a short demonstration of room and equipment scheduling."""
    scheduler = Scheduler()
    scheduler.schedule_room("Board-1", "09-11")
    scheduler.schedule_room("Board-1", "09-11")

    try:
        scheduler.schedule_room("Huddle-3", "14-12")
    except ValueError as error:
        print(f"Invalid booking rejected: {error}")

    slot = input("Slot for Board-2, like 10-12 (Enter for 10-12): ").strip()
    slot = slot or "10-12"
    try:
        scheduler.schedule_room("Board-2", slot, ["projector", "webcam"])
    except ValueError as error:
        print(f"Booking rejected: {error}")

    scheduler.export_schedule()
    scheduler.log_conflicts()
    print("Equipment left:", scheduler.equipment_pool)
    print("Reservations:", scheduler.reservations)


if __name__ == "__main__":
    main()
