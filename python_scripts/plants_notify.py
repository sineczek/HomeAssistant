plants = [
    {"name": "Viola Alpina", "image": "/local/fiolek-alpejski.jpg",
    "m": float(hass.states.get("sensor.plant_sensor_no11_wilgoc").state),
    "t": float(hass.states.get("sensor.plant_sensor_no11_temperatura").state),
    "c": float(hass.states.get("sensor.plant_sensor_no11_przewodnosc_elektryczna").state),
    "ranges": {"moisture": {"gmin":30,"gmax":50,"ymin":25,"ymax":55},
                "temp":{"gmin":12,"gmax":16,"ymin":10,"ymax":18},
                "cond":{"gmin":500,"gmax":1500,"ymin":350,"ymax":2000}}},

    {"name": "Phalaenopsis", "image": "/local/phalaenopsis_fiolet.png",
    "m": float(hass.states.get("sensor.plant_sensor_no01_wilgoc").state),
    "t": float(hass.states.get("sensor.plant_sensor_no01_temperatura").state),
    "c": float(hass.states.get("sensor.plant_sensor_no01_przewodnosc_elektryczna").state),
    "ranges": {"moisture": {"gmin":30,"gmax":50,"ymin":25,"ymax":55},
                "temp":{"gmin":20,"gmax":24,"ymin":18,"ymax":25},
                "cond":{"gmin":500,"gmax":1000,"ymin":300,"ymax":1200}}},
    
    {"name": "Phalaenopsis (bez kwiatka)", "image": "/local/phalaenopsis_fiolet.png",
     "m": float(hass.states.get("sensor.plant_sensor_no02_wilgoc").state),
     "t": float(hass.states.get("sensor.plant_sensor_no02_temperatura").state),
     "c": float(hass.states.get("sensor.plant_sensor_no02_przewodnosc_elektryczna").state),
     "ranges": {"moisture": {"gmin":30,"gmax":50,"ymin":25,"ymax":55},
                "temp":{"gmin":20,"gmax":24,"ymin":18,"ymax":25},
                "cond":{"gmin":500,"gmax":1000,"ymin":300,"ymax":1200}}},

    {"name": "Ficus", "image": "/local/ficus.jpg",
     "m": float(hass.states.get("sensor.plant_sensor_10_moisture").state),
     "t": float(hass.states.get("sensor.plant_sensor_10_temperature").state),
     "c": float(hass.states.get("sensor.plant_sensor_10_conductivity").state),
     "ranges": {"moisture": {"gmin":25,"gmax":45,"ymin":20,"ymax":50},
                "temp":{"gmin":20,"gmax":23,"ymin":18,"ymax":24},
                "cond":{"gmin":500,"gmax":1500,"ymin":350,"ymax":2000}}},

    {"name": "Viola Alpina (2gi od lewej)", "image": "/local/fiolek-alpejski.jpg",
     "m": float(hass.states.get("sensor.plant_sensor_no04_wilgoc").state),
     "t": float(hass.states.get("sensor.plant_sensor_no04_temperatura").state),
     "c": float(hass.states.get("sensor.plant_sensor_no04_przewodnosc_elektryczna").state),
     "ranges": {"moisture": {"gmin":30,"gmax":50,"ymin":25,"ymax":55},
                "temp":{"gmin":12,"gmax":16,"ymin":10,"ymax":18},
                "cond":{"gmin":500,"gmax":1500,"ymin":350,"ymax":2000}}},

    {"name": "Viola Alpina (1szy od lewej)", "image": "/local/fiolek-alpejski.jpg",
     "m": float(hass.states.get("sensor.plant_sensor_no05_wilgoc").state),
     "t": float(hass.states.get("sensor.plant_sensor_no05_temperatura").state),
     "c": float(hass.states.get("sensor.plant_sensor_no05_przewodnosc_elektryczna").state),
     "ranges": {"moisture": {"gmin":30,"gmax":50,"ymin":25,"ymax":55},
                "temp":{"gmin":12,"gmax":16,"ymin":10,"ymax":18},
                "cond":{"gmin":500,"gmax":1500,"ymin":350,"ymax":2000}}},

    {"name": "Yuka", "image": "/local/juka.webp",
     "m": float(hass.states.get("sensor.plant_sensor_no08_wilgoc").state),
     "t": float(hass.states.get("sensor.plant_sensor_no08_temperatura").state),
     "c": float(hass.states.get("sensor.plant_sensor_no08_przewodnosc_elektryczna").state),
     "ranges": {"moisture": {"gmin":15,"gmax":30,"ymin":12,"ymax":35},
                "temp":{"gmin":21,"gmax":24,"ymin":20,"ymax":25},
                "cond":{"gmin":500,"gmax":1200,"ymin":300,"ymax":1500}}},

    {"name": "Anturium", "image": "/local/anturium.jpg",
     "m": float(hass.states.get("sensor.plant_sensor_no12_wilgoc").state),
     "t": float(hass.states.get("sensor.plant_sensor_no12_temperatura").state),
     "c": float(hass.states.get("sensor.plant_sensor_no12_przewodnosc_elektryczna").state),
     "ranges": {"moisture": {"gmin":35,"gmax":55,"ymin":30,"ymax":60},
                "temp":{"gmin":20,"gmax":26,"ymin":18,"ymax":28},
                "cond":{"gmin":800,"gmax":2000,"ymin":400,"ymax":2500}}}
]

now = hass.states.get('sensor.time').state
hour = int(now.split(':')[0])
evening = hour == 19

def check(val, gmin, gmax, ymin, ymax):
    if val < ymin or val > ymax:
        return "red"
    elif val < gmin or val > gmax:
        return "yellow"
    else:
        return "green"

plants_status = []

for plant in plants:
    m_status = check(
        plant["m"],
        plant["ranges"]["moisture"]["gmin"],
        plant["ranges"]["moisture"]["gmax"],
        plant["ranges"]["moisture"]["ymin"],
        plant["ranges"]["moisture"]["ymax"]
    )

    t_status = check(
        plant["t"],
        plant["ranges"]["temp"]["gmin"],
        plant["ranges"]["temp"]["gmax"],
        plant["ranges"]["temp"]["ymin"],
        plant["ranges"]["temp"]["ymax"]
    )

    c_status = check(
        plant["c"],
        plant["ranges"]["cond"]["gmin"],
        plant["ranges"]["cond"]["gmax"],
        plant["ranges"]["cond"]["ymin"],
        plant["ranges"]["cond"]["ymax"]
    )

    logger.info(f"{plant['name']} - Moisture: {m_status}, Temp: {t_status}, Conductivity: {c_status}")

    has_red = "red" in [m_status, t_status, c_status]
    has_yellow = "yellow" in [m_status, t_status, c_status]

    if has_red or (evening and has_yellow):
        plants_status.append(plant)

if len(plants_status) == 0:
    logger.info("Brak kwiatków wymagających uwagi.")
else:
    if len(plants_status) == 1:
        title = f"{plants_status[0]['name']} wymaga uwagi"
        message = plants_status[0]['name']
        image = plants_status[0]['image']
    else:
        title = f"Kwiatki ({len(plants_status)}) wymagają uwagi"
        message = "\n".join([p['name'] for p in plants_status])
        image = plants_status[0]['image']  # pierwszy obrazek

    # hass.services.call("notify", "mobile_app_iphone", {
    #     "title": title,
    #     "message": message,
    #     "data": {
    #         "attachment": {"url": image, "content-type": "jpg"},
    #         "url": "/lovelace/kwiatki-na-telefon"
    #     }
    # })

    hass.services.call("notify", "mobile_app_igos", {
        "title": title,
        "message": message,
        "data": {
            "attachment": {"url": image, "content-type": "jpg"},
            "url": "/lovelace/kwiatki-dynamic"
        }
    })
