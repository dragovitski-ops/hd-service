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
    "head":[64,61,63],
    "ajna":[47,24,4,17,43,11],
    "throat":[62,23,56,35,12,45,33,8,31,7,1,10,25,20,16],
    "g":[1,2,7,10,13,15,25,46],
    "heart":[21,40,26,51],
    "sacral":[5,14,29,59,9,3,42,27,34],
    "spleen":[48,57,44,50,32,28,18],
    "solar":[30,55,49,19,39,41,22,36,37,6],
    "root":[53,60,52,19,39,41,58,38,54]
}

CENTER_BG = {
    "head":"Glava","ajna":"Adjna","throat":"Garllo","g":"Sebe",
    "heart":"Sartse","sacral":"Sakral","spleen":"Dalak",
    "solar":"Solaren pleksus","root":"Koren"
}

CENTER_BG_FULL = {
    "head":"\u0413\u043b\u0430\u0432\u0430",
    "ajna":"\u0410\u0434\u0436\u043d\u0430",
    "throat":"\u0413\u044a\u0440\u043b\u043e",
    "g":"\u0421\u0435\u0431\u0435",
    "heart":"\u0421\u044a\u0440\u0446\u0435",
    "sacral":"\u0421\u0430\u043a\u0440\u0430\u043b",
    "spleen":"\u0414\u0430\u043b\u0430\u043a",
    "solar":"\u0421\u043e\u043b\u0430\u0440\u0435\u043d \u043f\u043b\u0435\u043a\u0441\u0443\u0441",
    "root":"\u041a\u043e\u0440\u0435\u043d"
}

PLANET_IDS = {
    "sun":swe.SUN,"moon":swe.MOON,"mercury":swe.MERCURY,
    "venus":swe.VENUS,"mars":swe.MARS,"jupiter":swe.JUPITER,
    "saturn":swe.SATURN,"uranus":swe.URANUS,"neptune":swe.NEPTUNE,
    "pluto":swe.PLUTO,"north_node":swe.TRUE_NODE
}

CROSS_MAP = {
    "34/20":"\u041a\u0440\u044a\u0441\u0442\u044a\u0442 \u043d\u0430 \u0421\u043f\u044f\u0449\u0438\u044f \u0424\u0435\u043d\u0438\u043a\u0441",
    "20/34":"\u041a\u0440\u044a\u0441\u0442\u044a\u0442 \u043d\u0430 \u0421\u043f\u044f\u0449\u0438\u044f \u0424\u0435\u043d\u0438\u043a\u0441",
    "59/55":"\u041a\u0440\u044a\u0441\u0442\u044a\u0442 \u043d\u0430 \u0421\u043f\u044f\u0449\u0438\u044f \u0424\u0435\u043d\u0438\u043a\u0441",
    "55/59":"\u041a\u0440\u044a\u0441\u0442\u044a\u0442 \u043d\u0430 \u0421\u043f\u044f\u0449\u0438\u044f \u0424\u0435\u043d\u0438\u043a\u0441",
    "1/2":"\u041a\u0440\u044a\u0441\u0442\u044a\u0442 \u043d\u0430 \u0421\u0444\u0438\u043d\u043a\u0441\u0430",
    "2/1":"\u041a\u0440\u044a\u0441\u0442\u044a\u0442 \u043d\u0430 \u0421\u0444\u0438\u043d\u043a\u0441\u0430",
    "13/7":"\u041a\u0440\u044a\u0441\u0442\u044a\u0442 \u043d\u0430 \u0421\u043b\u0443\u0448\u0430\u0442\u0435\u043b\u044f",
    "7/13":"\u041a\u0440\u044a\u0441\u0442\u044a\u0442 \u043d\u0430 \u0421\u043b\u0443\u0448\u0430\u0442\u0435\u043b\u044f",
    "25/46":"\u041a\u0440\u044a\u0441\u0442\u044a\u0442 \u043d\u0430 \u0424\u0435\u043d\u0438\u043a\u0441\u0430",
    "46/25":"\u041a\u0440\u044a\u0441\u0442\u044a\u0442 \u043d\u0430 \u0424\u0435\u043d\u0438\u043a\u0441\u0430",
    "10/15":"\u041a\u0440\u044a\u0441\u0442\u044a\u0442 \u043d\u0430 \u041f\u043e\u0442\u043e\u043a\u0430",
    "15/10":"\u041a\u0440\u044a\u0441\u0442\u044a\u0442 \u043d\u0430 \u041f\u043e\u0442\u043e\u043a\u0430",
    "35/36":"\u041a\u0440\u044a\u0441\u0442\u044a\u0442 \u043d\u0430 \u0427\u043e\u0432\u0435\u0447\u043d\u043e\u0441\u0442\u0442\u0430",
    "36/35":"\u041a\u0440\u044a\u0441\u0442\u044a\u0442 \u043d\u0430 \u0427\u043e\u0432\u0435\u0447\u043d\u043e\u0441\u0442\u0442\u0430",
    "29/30":"\u041a\u0440\u044a\u0441\u0442\u044a\u0442 \u043d\u0430 \u0416\u0435\u0440\u0442\u0432\u0430\u0442\u0430",
    "30/29":"\u041a\u0440\u044a\u0441\u0442\u044a\u0442 \u043d\u0430 \u0416\u0435\u0440\u0442\u0432\u0430\u0442\u0430",
    "18/17":"\u041a\u0440\u044a\u0441\u0442\u044a\u0442 \u043d\u0430 \u041f\u0440\u043e\u043c\u0438\u0448\u043b\u0435\u043d\u043e\u0441\u0442\u0442\u0430",
    "17/18":"\u041a\u0440\u044a\u0441\u0442\u044a\u0442 \u043d\u0430 \u041f\u0440\u043e\u043c\u0438\u0448\u043b\u0435\u043d\u043e\u0441\u0442\u0442\u0430",
    "19/33":"\u041a\u0440\u044a\u0441\u0442\u044a\u0442 \u043d\u0430 \u041d\u0443\u0436\u0434\u0430\u0442\u0430",
    "33/19":"\u041a\u0440\u044a\u0441\u0442\u044a\u0442 \u043d\u0430 \u041d\u0443\u0436\u0434\u0430\u0442\u0430",
    "38/39":"\u041a\u0440\u044a\u0441\u0442\u044a\u0442 \u043d\u0430 \u0422\u0435\u043d\u0441\u0438\u044f\u0442\u0430",
    "39/38":"\u041a\u0440\u044a\u0441\u0442\u044a\u0442 \u043d\u0430 \u0422\u0435\u043d\u0441\u0438\u044f\u0442\u0430",
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
    # Primary: center defined if it has a complete channel
    for g1,g2 in CHANNELS:
        if g1 in active and g2 in active:
            for c,cg in CENTER_GATES.items():
                if g1 in cg or g2 in cg:
                    defined.add(c)
    # Secondary: G center defined if 2+ of its gates are active
    # (mybodygraph behavior - G can be defined via multiple active gates)
    g_active = [g for g in CENTER_GATES["g"] if g in active]
    if len(g_active) >= 2:
        defined.add("g")
    # Head/Ajna defined if they have a complete channel
    # (already handled above via 47-64, 4-63, 17-62 etc)
    return defined

def get_definition(defined, active_gates):
    if len(defined) == 0: return "\u041e\u0442\u0432\u043e\u0440\u0435\u043d\u0430"
    adj = {c: set() for c in defined}
    for g1, g2 in CHANNELS:
        if g1 in active_gates and g2 in active_gates:
            c1s = [c for c,cg in CENTER_GATES.items() if g1 in cg and c in defined]
            c2s = [c for c,cg in CENTER_GATES.items() if g2 in cg and c in defined]
            for c1 in c1s:
                for c2 in c2s:
                    if c1 != c2:
                        adj[c1].add(c2)
                        adj[c2].add(c1)
    visited = set()
    components = 0
    for start in defined:
        if start not in visited:
            components += 1
            queue = [start]
            while queue:
                node = queue.pop(0)
                if node not in visited:
                    visited.add(node)
                    queue.extend(adj[node] - visited)
    if components == 1: return "\u0426\u044f\u043b\u043e\u0441\u0442\u043d\u0430"
    if components == 2: return "\u0420\u0430\u0437\u0434\u0435\u043b\u0435\u043d\u0430"
    if components == 3: return "\u0422\u0440\u043e\u0439\u043d\u043e \u0440\u0430\u0437\u0434\u0435\u043b\u0435\u043d\u0430"
    return "\u0427\u0435\u0442\u0432\u043e\u0440\u043d\u043e \u0440\u0430\u0437\u0434\u0435\u043b\u0435\u043d\u0430"

def get_type(defined):
    hs = "sacral" in defined
    ht = "throat" in defined
    hso = "solar" in defined
    hh = "heart" in defined
    hsp = "spleen" in defined
    hr = "root" in defined
    if hs and ht: return "\u041c\u0430\u043d\u0438\u0444\u0435\u0441\u0442\u0438\u0440\u0430\u0449 \u0413\u0435\u043d\u0435\u0440\u0430\u0442\u043e\u0440","\u0418\u0437\u0447\u0430\u043a\u0430\u0439 \u0434\u0430 \u043e\u0442\u043a\u043b\u0438\u043a\u043d\u0435\u0448","\u041d\u0435\u0443\u0434\u043e\u0432\u043b\u0435\u0442\u0432\u043e\u0440\u0435\u043d\u0438\u0435 / \u0413\u043d\u044f\u0432"
    if hs: return "\u0413\u0435\u043d\u0435\u0440\u0430\u0442\u043e\u0440","\u0418\u0437\u0447\u0430\u043a\u0430\u0439 \u0434\u0430 \u043e\u0442\u043a\u043b\u0438\u043a\u043d\u0435\u0448","\u041d\u0435\u0443\u0434\u043e\u0432\u043b\u0435\u0442\u0432\u043e\u0440\u0435\u043d\u0438\u0435"
    if ht and not hs and (hh or hso or hr): return "\u041c\u0430\u043d\u0438\u0444\u0435\u0441\u0442\u043e\u0440","\u0418\u043d\u0444\u043e\u0440\u043c\u0438\u0440\u0430\u0439 \u043f\u0440\u0435\u0434\u0438 \u0434\u0430 \u0434\u0435\u0439\u0441\u0442\u0432\u0430\u0448","\u0413\u043d\u044f\u0432"
    if len(defined)==0: return "\u0420\u0435\u0444\u043b\u0435\u043a\u0442\u043e\u0440","\u0418\u0437\u0447\u0430\u043a\u0430\u0439 \u043b\u0443\u043d\u0435\u043d \u0446\u0438\u043a\u044a\u043b","\u0420\u0430\u0437\u043e\u0447\u0430\u0440\u043e\u0432\u0430\u043d\u0438\u0435"
    return "\u041f\u0440\u043e\u0435\u043a\u0442\u043e\u0440","\u0418\u0437\u0447\u0430\u043a\u0430\u0439 \u043f\u043e\u043a\u0430\u043d\u0430","\u0413\u043e\u0440\u0447\u0438\u0432\u0438\u043d\u0430"

def get_authority(defined):
    for c,a in [("solar","\u0415\u043c\u043e\u0446\u0438\u043e\u043d\u0430\u043b\u0435\u043d"),
                ("sacral","\u0421\u0430\u043a\u0440\u0430\u043b\u0435\u043d"),
                ("spleen","\u0414\u0430\u043b\u0430\u0447\u0435\u043d"),
                ("heart","\u0421\u044a\u0440\u0434\u0435\u0447\u0435\u043d"),
                ("g","\u0421\u0435\u0431\u0435-\u043f\u0440\u043e\u0435\u043a\u0442\u0438\u0440\u0430\u043d")]:
        if c in defined: return a
    return "\u041b\u0443\u043d\u0435\u043d" if len(defined)==0 else "\u041c\u0435\u043d\u0442\u0430\u043b\u0435\u043d"

class BirthData(BaseModel):
    year:int; month:int; day:int; hour:int; minute:int; utc_offset:float=2.0

@app.get("/")
def root(): return {"status":"Human Design API running"}

@app.post("/calculate")
def calculate(data: BirthData):
    try:
        ut = data.hour - data.utc_offset + data.minute/60
        jd = swe.julday(data.year, data.month, data.day, ut)
        p_pos = get_positions(jd)

        # Precise solar arc design (Newton-Raphson)
        p_sun_lon = p_pos["sun"]
        design_sun_target = (p_sun_lon - 88) % 360
        design_jd = jd - 88.0 / 0.9856
        for _ in range(30):
            test_lon = swe.calc_ut(design_jd, swe.SUN)[0][0]
            diff = ((test_lon - design_sun_target + 180) % 360) - 180
            if abs(diff) < 0.0001: break
            test_lon2 = swe.calc_ut(design_jd + 0.01, swe.SUN)[0][0]
            speed = (test_lon2 - test_lon) / 0.01
            if abs(speed) < 0.001: speed = 0.9856
            design_jd -= diff / speed
        d_pos = get_positions(design_jd)

        p_sun_g, p_sun_l = get_gate_line(p_pos["sun"])
        p_earth_g, p_earth_l = get_gate_line((p_pos["sun"]+180)%360)
        d_sun_g, d_sun_l = get_gate_line(d_pos["sun"])
        d_earth_g, d_earth_l = get_gate_line((d_pos["sun"]+180)%360)

        profile = f"{p_sun_l}/{d_earth_l}"

        p_gates = get_gates(p_pos)
        d_gates = get_gates(d_pos)
        all_gates = p_gates | d_gates
        defined = get_defined(all_gates)

        hd_type, strategy, not_self = get_type(defined)
        authority = get_authority(defined)
        definition = get_definition(defined, all_gates)

        cross_key = f"{p_sun_g}/{p_earth_g}"
        cross_name = CROSS_MAP.get(cross_key, f"\u041a\u0440\u044a\u0441\u0442\u044a\u0442 \u043d\u0430 \u041f\u043e\u0440\u0442\u0430 {p_sun_g}/{p_earth_g}")
        angle = "\u0414\u0435\u0441\u0435\u043d \u042a\u0433\u044a\u043b" if p_sun_l<=3 else ("\u0421\u044a\u043f\u043e\u0441\u0442\u0430\u0432\u0435\u043d" if p_sun_l==4 else "\u041b\u044f\u0432 \u042a\u0433\u044a\u043b")
        cross = f"{angle} \u2014 {cross_name} ({p_sun_g}/{p_earth_g} | {d_sun_g}/{d_earth_g})"

        return {
            "type": hd_type,
            "profile": profile,
            "authority": authority,
            "definition": definition,
            "strategy": strategy,
            "notSelf": not_self,
            "cross": cross,
            "definedCenters": [CENTER_BG_FULL[c] for c in defined],
            "activeGates": sorted(list(all_gates)),
            "personalityGates": sorted(list(p_gates)),
            "designGates": sorted(list(d_gates)),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/debug")
def debug(data: BirthData):
    try:
        ut = data.hour - data.utc_offset + data.minute/60
        jd = swe.julday(data.year, data.month, data.day, ut)
        p_pos = get_positions(jd)
        p_sun_lon = p_pos["sun"]
        design_sun_target = (p_sun_lon - 88) % 360
        design_jd = jd - 88.0 / 0.9856
        for _ in range(30):
            test_lon = swe.calc_ut(design_jd, swe.SUN)[0][0]
            diff = ((test_lon - design_sun_target + 180) % 360) - 180
            if abs(diff) < 0.0001: break
            test_lon2 = swe.calc_ut(design_jd + 0.01, swe.SUN)[0][0]
            speed = (test_lon2 - test_lon) / 0.01
            if abs(speed) < 0.001: speed = 0.9856
            design_jd -= diff / speed
        d_pos = get_positions(design_jd)
        p_gates_detail = {}
        for name, lon in p_pos.items():
            g, l = get_gate_line(lon)
            p_gates_detail[name] = {"lon": round(lon,3), "gate": g, "line": l}
            if name == "sun":
                eg, el = get_gate_line((lon+180)%360)
                p_gates_detail["earth"] = {"lon": round((lon+180)%360,3), "gate": eg, "line": el}
        d_gates_detail = {}
        for name, lon in d_pos.items():
            g, l = get_gate_line(lon)
            d_gates_detail[name] = {"lon": round(lon,3), "gate": g, "line": l}
            if name == "sun":
                eg, el = get_gate_line((lon+180)%360)
                d_gates_detail["earth"] = {"lon": round((lon+180)%360,3), "gate": eg, "line": el}
        p_gates = get_gates(p_pos)
        d_gates = get_gates(d_pos)
        all_gates = p_gates | d_gates
        defined = get_defined(all_gates)
        return {
            "personality": p_gates_detail,
            "design": d_gates_detail,
            "p_gates": sorted(p_gates),
            "d_gates": sorted(d_gates),
            "all_gates": sorted(all_gates),
            "defined_centers": list(defined),
            "active_channels": [[g1,g2] for g1,g2 in CHANNELS if g1 in all_gates and g2 in all_gates]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT",8000)))
