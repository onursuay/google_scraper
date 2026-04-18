"""Unit tests for format_city_locative()."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from marketing.campaigns import format_city_locative


CASES = [
    # (girdi, beklenen çıktı)
    ("İstanbul",  "İstanbul’da"),   # son ünlü: u (kalın)
    ("Ankara",    "Ankara’da"),     # son ünlü: a (kalın)
    ("İzmir",     "İzmir’de"),      # son ünlü: i (ince)
    ("Bursa",     "Bursa’da"),      # son ünlü: a (kalın)
    ("Eskişehir", "Eskişehir’de"),  # son ünlü: i (ince)
    ("Ordu",      "Ordu’da"),       # son ünlü: u (kalın)
]

EDGE_CASES = [
    (None,        ""),
    ("",          ""),
    ("   ",       ""),
    ("Çorum",     "Çorum’da"),     # son ünlü: u
    ("Niğde",     "Niğde’de"),     # son ünlü: e
    ("Muğla",     "Muğla’da"),     # son ünlü: a
    ("Gümüşhane", "Gümüşhane’de"), # son ünlü: e
    ("42",        "42"),            # ünlü yok → ham dön
]


def run():
    ok = 0
    fail = 0
    for city, expected in CASES + EDGE_CASES:
        got = format_city_locative(city)
        status = "PASS" if got == expected else "FAIL"
        if got == expected:
            ok += 1
        else:
            fail += 1
        print(f"  [{status}]  {city!r:20s} → {got!r}" + ("" if got == expected else f"  (beklenen: {expected!r})"))
    print(f"\n{ok} passed, {fail} failed")
    return fail == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
