from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import swisseph as swe
import math
import os

app = FastAPI(title="Human Design API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# HD Gate wheel — sequence starting at 0° Aries
HD_WHEEL = [
    41,19,13,49,30,55,37,63,22,36,25,17,21,51,42,3,
    27,24,2,23,8,20,16,35,45,12,15,52,39,53,62,56,
    31,33,7,4,29,59,40,64,47,6,46,18,48,57,32,50,
    28,44,1,43,14,34,9,5,26,11,10,58,38,54,61,60
]

# Channels (gate pairs)
CHANNELS = [
    (1,8),(2,14),(3,60),(4,63),(5,15),(6,59),(7,31),(9,52),
    (10,20),(11,56),(12,22),(13,33),(16,48),(17,62),(18,58),
    (19,49),(20,34),(21,45),(23,43),(24,61),(25,51),(26,44),
    (27,50),(28,38),(29,46),(30,41),(32,54),(35,36),(37,40),
    (39,55),(42,53),(47,64),(57,20),(57,34)
]

# Centers and their gates
CENTER_GATES = {
    "head":   [64,61,63],
    "ajna":   [47,24,4,17,43,11],
    "throat": [62,23,56,35,12,45,33,8,31,7,1,10,25,20,16],
    "g":      [1,2,7,10,13,15,25,46],
    "heart":  [21,40,26,51],
    "sacral": [5,14,29,59,9,3,42,27,34],
    "spleen": [48,57,44,50,32,28,18],
    "solar":  [30,55,49,19,39,41,22,36,37],
    "root":   [53,60,52,19,39,41,58,38,54]
}

CENTER_BG = {
    "head": "Глава", "ajna": "Аджна", "throat": "Гърло",
    "g": "Себе", "heart": "Сърце", "sacral": "Сакрал",
    "spleen": "Далак", "solar": "Соларен плексус", "root": "Корен"
}

PLANET_IDS = {
    "sun": swe.SUN, "moon": swe.MOON, "mercury": swe.MERCURY,
    "venus": swe.VENUS, "mars": swe.MARS, "jupiter": swe.JUPITER,
    "saturn": swe.SATURN, "uranus": swe.URANUS, "neptune": swe.NEPTUNE,
    "pluto": swe.PLUTO, "north_node": swe.TRUE_NODE
}

def get_gate_line(abs_lon: float):
    norm = abs_lon % 360
    idx = int(norm / 5.625) % 64
    gate = HD_WHEEL[idx]
    pos_in_gate = norm % 5.625
    line = min(int(pos_in_gate / 0.9375) + 1, 6)
    return gate, line

def get_planet_positions(jd: float):
    positions = {}
    for name, pid in PLANET_IDS.items():
        result = swe.calc_ut(jd, pid)
        positions[name] = result[0][0]  # longitude
    return positions

def calculate_active_gates(positions: dict):
    gates = set()
    for name, lon in positions.items():
        gate, _ = get_gate_line(lon)
        gates.add(gate)
        # Earth = opposite of Sun
        if name == "sun":
            earth_gate, _ = get_gate_line((lon + 180) % 360)
            gates.add(earth_gate)
    return gates

def get_defined_centers(active_gates: set):
    defined = set()
    for center, c_gates in CENTER_GATES.items():
        for g1, g2 in CHANNELS:
            if (g1 in c_gates or g2 in c_gates):
                if g1 in active_gates and g2 in active_gates:
                    defined.add(center)
                    # Also define connected centers
                    for c2, cg2 in CENTER_GATES.items():
                        if c2 != center and (g1 in cg2 or g2 in cg2):
                            defined.add(c2)
    return defined

def determine_type(defined: set):
    has_sacral = "sacral" in defined
    has_throat = "throat" in defined
    has_solar = "solar" in defined
    has_heart = "heart" in defined
    has_spleen = "spleen" in defined
    has_root = "root" in defined

    if has_sacral and has_throat:
        return "Манифестиращ Генератор", "Изчакай да откликнеш", "Неудовлетворение / Гняв"
    elif has_sacral:
        return "Генератор", "Изчакай да откликнеш", "Неудовлетворение"
    elif has_throat and (has_heart or has_solar or has_spleen or has_root):
        return "Манифестор", "Информирай преди да действаш", "Гняв"
    elif len(defined) == 0:
        return "Рефлектор", "Изчакай лунен цикъл", "Разочарование"
    else:
        return "Проектор", "Изчакай покана", "Горчивина"

def determine_authority(defined: set):
    if "solar" in defined: return "Емоционален"
    if "sacral" in defined: return "Сакрален"
    if "spleen" in defined: return "Далачен"
    if "heart" in defined: return "Сърдечен"
    if "g" in defined: return "Себе-проектиран"
    if len(defined) == 0: return "Лунен"
    return "Ментален"

def determine_definition(defined: set):
    n = len(defined)
    if n == 0: return "Отворена"
    if n <= 2: return "Единична"
    if n <= 5: return "Разделена"
    if n <= 7: return "Тройно разделена"
    return "Цялостна"

CROSS_MAP = {
    "34/20": "Кръстът на Спящия Феникс",
    "20/34": "Кръстът на Спящия Феникс",
    "59/55": "Кръстът на Спящия Феникс",
    "1/2":   "Кръстът на Сфинкса",
    "2/1":   "Кръстът на Сфинкса",
    "13/7":  "Кръстът на Слушателя",
    "7/13":  "Кръстът на Слушателя",
    "25/46": "Кръстът на Феникса",
    "46/25": "Кръстът на Феникса",
    "10/15": "Кръстът на Потока",
    "15/10": "Кръстът на Потока",
    "35/36": "Кръстът на Човечността",
    "36/35": "Кръстът на Човечността",
    "29/30": "Кръстът на Жертвата",
    "30/29": "Кръстът на Жертвата",
    "47/22": "Кръстът на Разпятието",
    "22/47": "Кръстът на Разпятието",
    "18/17": "Кръстът на Промишлеността",
    "17/18": "Кръстът на Промишлеността",
}

class BirthData(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    minute: int
    utc_offset: float = 2.0

@app.get("/")
def root():
    return {"status": "Human Design API running"}

@app.post("/calculate")
def calculate(data: BirthData):
    try:
        # Convert to Julian Day (UTC)
        ut_hour = data.hour - data.utc_offset + data.minute / 60
        jd = swe.julday(data.year, data.month, data.day, ut_hour)

        # Personality positions (birth)
        p_pos = get_planet_positions(jd)
        p_sun_gate, p_sun_line = get_gate_line(p_pos["sun"])
        p_earth_gate, p_earth_line = get_gate_line((p_pos["sun"] + 180) % 360)

        # Design positions (~88° before birth Sun)
        design_sun_lon = (p_pos["sun"] - 88 + 360) % 360
        # Find JD when Sun was at design position (approx 88 days before)
        design_jd = jd - 88
        d_pos = get_planet_positions(design_jd)
        d_sun_gate, _ = get_gate_line(d_pos["sun"])
        d_earth_gate, _ = get_gate_line((d_pos["sun"] + 180) % 360)

        # Collect ALL active gates (personality + design)
        p_gates = calculate_active_gates(p_pos)
        d_gates = calculate_active_gates(d_pos)
        all_gates = p_gates | d_gates

        # Determine defined centers
        defined = get_defined_centers(all_gates)

        # Type, authority, definition
        hd_type, strategy, not_self = determine_type(defined)
        authority = determine_authority(defined)
        definition = determine_definition(defined)

        # Profile
        profile = f"{p_sun_line}/{p_earth_line}"

        # Incarnation cross
        cross_key = f"{p_sun_gate}/{p_earth_gate}"
        cross_name = CROSS_MAP.get(cross_key, f"Кръстът на Порта {p_sun_gate}/{p_earth_gate}")
        angle = "Десен Ъгъл" if p_sun_line <= 3 else ("Съединение" if p_sun_line == 4 else "Ляв Ъгъл")
        cross = f"{angle} — {cross_name} ({p_sun_gate}/{p_earth_gate} | {d_sun_gate}/{d_earth_gate})"

        return {
            "type": hd_type,
            "profile": profile,
            "authority": authority,
            "definition": definition,
            "strategy": strategy,
            "notSelf": not_self,
            "cross": cross,
            "definedCenters": [CENTER_BG[c] for c in defined],
            "activeGates": sorted(list(all_gates)),
            "personalityGates": sorted(list(p_gates)),
            "designGates": sorted(list(d_gates)),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
