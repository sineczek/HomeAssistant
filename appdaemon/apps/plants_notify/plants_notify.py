import appdaemon.plugins.hass.hassapi as hass
import yaml

class PlantsNotify(hass.Hass):

    def initialize(self):
        self.run_daily(self.check_plants, "19:00:00")
        self.log("PlantsNotify initialized and scheduled for 19:00")

    def check_plants(self, kwargs):
        try:
            with open("/config/packages/sensors/plants.yaml", "r") as f:
                config = yaml.safe_load(f)

            plants = config["plants"]

            def check(val, gmin, gmax, ymin, ymax):
                if val < ymin or val > ymax:
                    return "red"
                elif val < gmin or val > gmax:
                    return "yellow"
                else:
                    return "green"

            plants_status = []

            for plant in plants:
                m = float(self.get_state(plant["sensors"]["moisture"]))
                t = float(self.get_state(plant["sensors"]["temp"]))
                c = float(self.get_state(plant["sensors"]["cond"]))

                m_status = check(m, **plant["ranges"]["moisture"])
                t_status = check(t, **plant["ranges"]["temp"])
                c_status = check(c, **plant["ranges"]["cond"])

                has_red = "red" in [m_status, t_status, c_status]
                has_yellow = "yellow" in [m_status, t_status, c_status]

                if has_red or has_yellow: 
                    plants_status.append(plant)

            if len(plants_status) == 0:
                self.log("Brak kwiatków wymagających uwagi.")
            else:
                if len(plants_status) == 1:
                    title = f"{plants_status[0]['name']} wymaga uwagi"
                    message = plants_status[0]['name']
                    image = plants_status[0]['image']
                else:
                    title = f"Kwiatki ({len(plants_status)}) wymagają uwagi"
                    message = "\n".join([p['name'] for p in plants_status])
                    image = plants_status[0]['image']

                self.call_service("notify/mobile_app_igos", title=title, message=message, data={
                    "attachment": {"url": image, "content-type": "jpg"},
                    "url": "/lovelace/kwiatki-dynamic"
                })

        except Exception as e:
            self.log(f"Błąd w PlantsNotify: {e}", level="ERROR")