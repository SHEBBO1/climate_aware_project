import time, random, requests, argparse

def random_payload():
    return {
        "soil_moisture": round(random.uniform(0.1, 0.6), 3),
        "soil_temp": round(random.uniform(10, 30), 1),
        "air_temp": round(random.uniform(10, 35), 1),
        "humidity": round(random.uniform(30, 90), 1),
        "rain_24h": round(random.uniform(0, 20), 2),
        "evapotranspiration": round(random.uniform(1, 6), 2)
    }

def run(target="http://localhost:5000/simulate", count=10, delay=2):
    for i in range(count):
        payload = random_payload()
        try:
            r = requests.post(target, json=payload, timeout=10)
            print(i+1, "sent:", payload, "=>", r.status_code, r.text)
        except Exception as e:
            print("error:", e)
        time.sleep(delay)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="http://localhost:5000/simulate")
    ap.add_argument("--count", type=int, default=5)
    ap.add_argument("--delay", type=float, default=1.0)
    args = ap.parse_args()
    run(args.target, args.count, args.delay)
