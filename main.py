from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import swisseph as swe
import os

app = FastAPI(title="Human Design API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["POST","GET"], allow_headers=["*"])

GATE_DEGREES = [
    (0.0,25),(3.875,17),(9.5,21),(15.125,51),(20.75,42),(26.375,3),
    (32.0,27),(37.625,24),(43.25,2),(48.875,23),(54.5,8),
    (60.125,20),(65.75,16),(71.375,35),(77.0,45),(82.625,12),(88.25,15),
    (93.875,52),(99.5,39),(105.125,53),(110.75,62),(116.375,56),
    (122.0,31),(127.625,33),(133.25,7),(138.875,4),(144.5,29),
    (150.125,59),(155.75,40),(161.375,64),(167.0,47),(172.625,6),(178.25,46),
    (183.875,18),(189.5,48),(195.125,57),(200.75,32),(206.375,50),
    (212.0,28),(217.625,44),(223.25,1),(228.875,43),(234.5,14),
    (240.125,34),(245.75,9),(251.375,5),(257.0,26),(262.625,11),(268.25,10),
    (273.875,58),(279.5,38),(285.125,54),(290.75,61),(296.375,60),
    (302.0,41),(307.625,19),(313.25,13),(318.875,49),(324.5,30),
    (330.125,55),(335.75,37),(341.375,63),(347.0,22),(352.625,36),(358.25,25),
]

CHANNELS = [
    (1,8),(2,14),(3,60),(4,63),(5,15),(6,59),(7,31),(9,52),
    (10,20),(11,56),(12,22),(13,33),(16,48),(17,62),(18,58),
    (19,49),(20,34),(21,45),(23,43),(24,61),(25,51),(26,44),
    (27,50),(28,38),(29,46),(30,41),(32,54),(35,36),(37,40),
    (39,55),(42,53),(47,64),(57,20),(57,34)
]

CENTER_GATES = {
    "head":[64,61,63],"ajna":[47,24,4,17,43,11],
    "throat":[62,23,56,35,12,45,33,8,31,7,1,10,25,20,16],
    "g":[1,2,7,10,13,15,25,46],"heart":[21,40,26,51],
    "sacral":[5,14,29,59,9,3,42,27,34],"spleen":[48,57,44,50,32,28,18],
    "solar":[30,55,49,19,39,41,22,36,37,6],"root":[53,60,52,19,39,41,58,38,54]
}

CENTER_BG = {
    "head":"Глава","ajna":"Аджна","throat":"Гърло","g":"Себе",
    "heart":"Сърце","sacral":"Сакрал","spleen":"Далак",
    "solar":"Соларен плексус","root":"Корен"
}

PLANET_IDS = {
    "sun":swe.SUN,"moon":swe.MOON,"mercury":swe.MERCURY,
    "venus":swe.VENUS,"mars":swe.MARS,"jupiter":swe.JUPITER,
    "saturn":swe.SATURN,"uranus":swe.URANUS,"neptune":swe.NEPTUNE,
    "pluto":swe.PLUTO,"north_node":swe.TRUE_NODE
}

CROSS_MAP = {
    "34/20":"Кръстът на Спящия Феникс","20/34":"Кръстът на Спящия Феникс",
    "59/55":"Кръстът на Спящия Феникс","55/59":"Кръстът на Спящия Феникс",
    "1/2":"Кръстът на Сфинкса","2/1":"Кръстът на Сфинкса",
    "13/7":"Кръстът на Слушателя","7/13":"Кръстът на Слушателя",
    "25/46":"Кръстът на Феникса","46/25":"Кръстът на Феникса",
    "10/15":"Кръстът на Потока","15/10":"Кръстът на Потока",
    "35/36":"Кръстът на Човечността","36/35":"Кръстът на Човечността",
    "29/30":"Кръстът на Жертвата","30/29":"Кръстът на Жертвата",
    "47/22":"Кръстът на Разпятието","22/47":"Кръстът на Разпятието",
    "18/17":"Кръстът на Промишлеността","17/18":"Кръстът на Промишлеността",
    "38/39":"Кръстът на Тенсията","39/38":"Кръстът на Тенсията",
    "57/51":"Кръстът на Проникновението","51/57":"Кръстът на Проникновението",
}

def get_gate_line(lon):
    norm = lon % 360
    for i in range(len(GATE_DEGREES)):
        start = GATE_DEGREES[i][0]
        end = GATE_DEGREES[i+1][0] if i+1 < len(GATE_DEGREES) else 360.0
        if start <= norm < end:
            gate = GATE_DEGREES[i][1]
            line = min(int((norm - start) / (5.625/6)) + 1, 6)
            return gate, line
    gate = GATE_DEGREES[-1][1]
    line = min(int((norm - GATE_DEGREES[-1][0]) / (5.625/6)) + 1, 6)
    return gate, line

def get_positions(jd):
    pos = {}
    for name, pid in PLANET_IDS.items():
        pos[name] = swe.calc_ut(jd, pid)[0][0]
    return pos

def get_gates(pos):
    gates = set()
    for name, lon in pos.items():
        g, _ = get_gate_line(lon)
        gates.add(g)
        if name == "sun":
            eg, _ = get_gate_line((lon+180)%360)
            gates.add(eg)
    return gates

def get_defined(active):
    defined = set()
    for g1,g2 in CHANNELS:
        if g1 in active and g2 in active:
            for c,cg in CENTER_GATES.items():
                if g1 in cg or g2 in cg:
                    defined.add(c)
    return defined

def get_type(defined):
    hs,ht,hso,hh,hsp,hr = ("sacral" in defined,"throat" in defined,
        "solar" in defined,"heart" in defined,"spleen" in defined,"root" in defined)
    if hs and ht: return "Манифестиращ Генератор","Изчакай да откликнеш","Неудовлетворение / Гняв"
    if hs: return "Генератор","Изчакай да откликнеш","Неудовлетворение"
    if ht and (hh or hso or hsp or hr): return "Манифестор","Информирай преди да действаш","Гняв"
    if len(defined)==0: return "Рефлектор","Изчакай лунен цикъл","Разочарование"
    return "Проектор","Изчакай покана","Горчивина"

def get_authority(defined):
    for c,a in [("solar","Емоционален"),("sacral","Сакрален"),("spleen","Далачен"),
                ("heart","Сърдечен"),("g","Себе-проектиран")]:
        if c in defined: return a
    return "Лунен" if len(defined)==0 else "Ментален"

def get_definition(defined):
    n = len(defined)
    if n==0: return "Отворена"
    if n<=2: return "Единична"
    if n<=5: return "Разделена"
    if n<=7: return "Тройно разделена"
    return "Цялостна"

class BirthData(BaseModel):
    year:int; month:int; day:int; hour:int; minute:int; utc_offset:float=2.0

@app.get("/")
def root(): return {"status":"Human Design API running"}

@app.post("/calculate")
def calculate(data:BirthData):
    try:
        ut = data.hour - data.utc_offset + data.minute/60
        jd = swe.julday(data.year, data.month, data.day, ut)
        p_pos = get_positions(jd)
        # Design = 88 solar arc degrees before birth sun
        p_sun_lon = swe.calc_ut(jd, swe.SUN)[0][0]
        design_sun_target = (p_sun_lon - 88) % 360
        design_jd = jd - 89
        for _ in range(20):
            test_lon = swe.calc_ut(design_jd, swe.SUN)[0][0]
            diff = ((test_lon - design_sun_target + 180) % 360) - 180
            if abs(diff) < 0.001: break
            design_jd -= diff / 0.9856
        d_pos = get_positions(design_jd)

        p_sun_g, p_sun_l = get_gate_line(p_pos["sun"])
        p_earth_g, p_earth_l = get_gate_line((p_pos["sun"]+180)%360)
        d_sun_g, d_sun_l = get_gate_line(d_pos["sun"])
        d_earth_g, d_earth_l = get_gate_line((d_pos["sun"]+180)%360)

        # Profile = Personality Sun line / Design Earth line
        profile = f"{p_sun_l}/{d_earth_l}"

        all_gates = get_gates(p_pos) | get_gates(d_pos)
        defined = get_defined(all_gates)
        hd_type, strategy, not_self = get_type(defined)
        authority = get_authority(defined)
        definition = get_definition(defined)

        cross_key = f"{p_sun_g}/{p_earth_g}"
        cross_name = CROSS_MAP.get(cross_key, f"Кръстът на Порта {p_sun_g}/{p_earth_g}")
        angle = "Десен Ъгъл" if p_sun_l<=3 else ("Съединение" if p_sun_l==4 else "Ляв Ъгъл")
        cross = f"{angle} — {cross_name} ({p_sun_g}/{p_earth_g} | {d_sun_g}/{d_earth_g})"

        return {
            "type":hd_type,"profile":profile,"authority":authority,
            "definition":definition,"strategy":strategy,"notSelf":not_self,
            "cross":cross,"definedCenters":[CENTER_BG[c] for c in defined],
            "activeGates":sorted(list(all_gates)),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT",8000)))
