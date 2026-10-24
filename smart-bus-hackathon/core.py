from copy import deepcopy

_STARTER_ROUTES = [
    {"route_id": "R101", "departure": "Karachi", "destination": "Hyderabad",
     "departure_time": "08:00 AM", "fare": 1200, "total_seats": 40, "available_seats": 40},
    {"route_id": "R102", "departure": "Karachi", "destination": "Sukkur",
     "departure_time": "09:30 AM", "fare": 2000, "total_seats": 36, "available_seats": 36},
    {"route_id": "R103", "departure": "Hyderabad", "destination": "Mirpur Khas",
     "departure_time": "11:00 AM", "fare": 800, "total_seats": 32, "available_seats": 32},
    {"route_id": "R104", "departure": "Karachi", "destination": "Lahore",
     "departure_time": "07:00 PM", "fare": 5000, "total_seats": 45, "available_seats": 45},
    {"route_id": "R105", "departure": "Sukkur", "destination": "Hyderabad",
     "departure_time": "02:00 PM", "fare": 1500, "total_seats": 30, "available_seats": 30},
]

SUPPORTED_CITIES = ("Karachi", "Hyderabad", "Sukkur", "Mirpur Khas", "Lahore")


class ReservationSystem:
    """All state and rules for the reservation workflow."""

    def __init__(self):
        self.routes = deepcopy(_STARTER_ROUTES)
        self.bookings = []
        self.issued_ids = set()
        self._next_id = 1001

    # ---------- queries ----------
    def find_route(self, route_id):
        rid = str(route_id).strip().upper()
        for r in self.routes:
            if r["route_id"] == rid:
                return r
        return None

    def search(self, term):
        t = str(term).strip().lower()
        if not t:
            return []
        # unique route ID match → stop early
        for r in self.routes:
            if r["route_id"].lower() == t:
                return [r]
        # otherwise match by city (departure or destination)
        return [r for r in self.routes
                if t in r["departure"].lower() or t in r["destination"].lower()]

    def get_booking(self, booking_id):
        bid = str(booking_id).strip().upper()
        for b in self.bookings:
            if b["booking_id"] == bid:
                return b
        return None

    # ---------- commands ----------
    def book(self, name, age, route_id, seats):
        name = str(name).strip()
        if not name:
            raise ValueError("Passenger name cannot be blank.")

        try:
            age = int(age)
        except (ValueError, TypeError):
            raise ValueError("Age must be a positive integer.")
        if age <= 0:
            raise ValueError("Age must be a positive integer.")

        route = self.find_route(route_id)
        if not route:
            raise ValueError(f"Route '{route_id}' does not exist.")

        try:
            seats = int(seats)
        except (ValueError, TypeError):
            raise ValueError("Seat quantity must be a positive integer.")
        if seats <= 0:
            raise ValueError("Seat quantity must be a positive integer.")
        if seats > route["available_seats"]:
            raise ValueError(
                f"Only {route['available_seats']} seat(s) available on "
                f"{route['route_id']}."
            )

        # unique ID — cancelled IDs are never reused
        while True:
            bid = f"B{self._next_id}"
            self._next_id += 1
            if bid not in self.issued_ids:
                self.issued_ids.add(bid)
                break

        booking = {
            "booking_id": bid,
            "passenger_name": name,
            "passenger_age": age,
            "route_id": route["route_id"],
            "seats": seats,
            "total_fare": route["fare"] * seats,
            "status": "Confirmed",
        }
        self.bookings.append(booking)
        route["available_seats"] -= seats
        return booking

    def cancel(self, booking_id):
        booking = self.get_booking(booking_id)
        if not booking:
            raise ValueError(f"Booking '{booking_id}' not found.")
        if booking["status"] == "Cancelled":
            raise ValueError(
                f"Booking {booking['booking_id']} is already cancelled."
            )
        route = self.find_route(booking["route_id"])
        if not route:
            raise ValueError("Route data missing for this booking.")

        booking["status"] = "Cancelled"
        route["available_seats"] += booking["seats"]  # restore exactly once
        return booking, route

    def report(self):
        confirmed = [b for b in self.bookings if b["status"] == "Confirmed"]
        cancelled = [b for b in self.bookings if b["status"] == "Cancelled"]
        return {
            "total_bookings":      len(self.bookings),
            "confirmed_bookings":  len(confirmed),
            "cancelled_bookings":  len(cancelled),
            "seats_reserved":      sum(b["seats"] for b in confirmed),
            "revenue":             sum(b["total_fare"] for b in confirmed),
            "fully_booked_routes": sum(1 for r in self.routes
                                       if r["available_seats"] == 0),
        }

    def schedule(self):
        """City → list of routes departing from that city."""
        return {
            city: [r for r in self.routes
                   if r["departure"].lower() == city.lower()]
            for city in SUPPORTED_CITIES
        }

if __name__ == "__main__":
    print("Running core.py smoke test…\n")
    rs = ReservationSystem()

    assert len(rs.routes) == 5, "Should start with 5 routes"
    assert rs.find_route("r101")["departure"] == "Karachi"
    assert rs.find_route("NOPE") is None
    print("✓ routes + find_route")

    hits = rs.search("Hyderabad")
    assert {r["route_id"] for r in hits} == {"R101", "R103", "R105"}, hits
    assert rs.search("Atlantis") == []
    print("✓ search (by city + no-match)")

    b = rs.book("Ahmed", 24, "R101", 2)
    assert b["booking_id"] == "B1001"
    assert b["total_fare"] == 2400
    assert rs.find_route("R101")["available_seats"] == 38
    print("✓ booking (ID, fare, seat decrement)")

    try:
        rs.book("  ", 20, "R101", 1); raise SystemExit("blank name accepted!")
    except ValueError:
        pass
    try:
        rs.book("X", "abc", "R101", 1); raise SystemExit("bad age accepted!")
    except ValueError:
        pass
    try:
        rs.book("X", 20, "R999", 1); raise SystemExit("bad route accepted!")
    except ValueError:
        pass
    try:
        rs.book("X", 20, "R101", 0); raise SystemExit("zero seats accepted!")
    except ValueError:
        pass
    try:
        rs.book("X", 20, "R101", 999); raise SystemExit("oversell accepted!")
    except ValueError:
        pass
    print("✓ validation rejects blank/age/route/zero/oversell")

    cancelled, route = rs.cancel("B1001")
    assert cancelled["status"] == "Cancelled"
    assert route["available_seats"] == 40
    try:
        rs.cancel("B1001"); raise SystemExit("double-cancel accepted!")
    except ValueError:
        pass
    print("✓ cancel + reject double-cancel + restore seats")

    rep = rs.report()
    assert rep["total_bookings"] == 1
    assert rep["confirmed_bookings"] == 0
    assert rep["cancelled_bookings"] == 1
    assert rep["seats_reserved"] == 0
    assert rep["revenue"] == 0
    print("✓ report excludes cancelled bookings")

    sched = rs.schedule()
    assert len(sched["Karachi"]) == 3
    assert sched["Lahore"] == []
    print("✓ schedule groups by departure city")

    print("\n🎉 ALL CORE TESTS PASSED")