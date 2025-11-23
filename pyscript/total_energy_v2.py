
import datetime
import time
import re
import unicodedata
import fnmatch

day_price = 1.25
night_price = 0.70
day_start = 6
day_end = 22

DEFAULT_AREA_FOR_UNASSIGNED = "Ogólne"

MIN_CACHE_REFRESH_SEC = 60
ENTITY_AREA_CACHE = {}
AREA_CACHE_LAST_REFRESH = 0.0

MANUAL_ENTITY_AREA_OVERRIDES = {}
OVERRIDE_PATTERNS = {}

LAST_VALUES: dict[str, float] = {}
TOTAL_ACCUMULATED: float = 0.0
AREA_ACCUMULATED: dict[str, float] = {}

def _slugify(name: str) -> str:
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s)
    return s.strip("_").lower()

def _override_area_for_entity(entity_id: str, default_area_name: str | None) -> str | None:
    if entity_id in MANUAL_ENTITY_AREA_OVERRIDES:
        return MANUAL_ENTITY_AREA_OVERRIDES[entity_id]
    for area_name, patterns in OVERRIDE_PATTERNS.items():
        for pat in patterns:
            if fnmatch.fnmatch(entity_id, pat):
                return area_name
    return default_area_name

def _build_entity_area_map() -> dict[str, str]:
    try:
        from homeassistant.helpers import entity_registry as er
        from homeassistant.helpers import device_registry as dr
        from homeassistant.helpers import area_registry as ar

        ent_reg = er.async_get(hass)
        dev_reg = dr.async_get(hass)
        area_reg = ar.async_get(hass)

        areas_by_id = {area.id: area.name for area in area_reg.areas.values()}
        mapping: dict[str, str] = {}

        for ent in ent_reg.entities.values():
            eid = ent.entity_id
            area_id = ent.area_id
            if area_id is None and ent.device_id:
                dev = dev_reg.async_get(ent.device_id)
                if dev:
                    area_id = dev.area_id
            if area_id and area_id in areas_by_id:
                mapping[eid] = areas_by_id[area_id]

        log.debug(f"_build_entity_area_map: mapped {len(mapping)} entities to areas")
        return mapping
    except Exception as e:
        log.error(f"Error building area mapping: {e}")
        return {}

def _refresh_entity_area_map(force: bool = False) -> dict[str, str]:
    global ENTITY_AREA_CACHE, AREA_CACHE_LAST_REFRESH
    now = time.time()
    if not force and (now - AREA_CACHE_LAST_REFRESH) < MIN_CACHE_REFRESH_SEC and ENTITY_AREA_CACHE:
        return ENTITY_AREA_CACHE
    ENTITY_AREA_CACHE = _build_entity_area_map()
    AREA_CACHE_LAST_REFRESH = now
    return ENTITY_AREA_CACHE

def _get_increment(entity_id: str, current_value: float) -> float:
    prev = LAST_VALUES.get(entity_id, current_value)
    diff = current_value - prev
    LAST_VALUES[entity_id] = current_value
    return diff if diff > 0 else 0.0

def calculate_energy():
    try:
        hour = datetime.datetime.now().hour
        price = day_price if day_start <= hour < day_end else night_price
        tariff = "day" if day_start <= hour < day_end else "night"
        timestamp = datetime.datetime.now().isoformat()

        increment_total = 0.0
        counted_entities: list[str] = []
        area_energy: dict[str, float] = {}
        area_entities: dict[str, list[str]] = {}

        entity_area_map = _refresh_entity_area_map()

        for entity_id in state.names(domain="sensor"):
            if entity_id == "sensor.total_energy" or entity_id.startswith("sensor.total_energy_"):
                continue

            value_str = state.get(entity_id)
            attrs = state.getattr(entity_id)

            device_class = (attrs.get("device_class") or "").lower()
            state_class = (attrs.get("state_class") or "").lower()
            if not (device_class == "energy" and state_class == "total_increasing"):
                continue

            if value_str in (None, "", "unknown", "unavailable"):
                continue

            unit = (attrs.get("unit_of_measurement") or "").lower()
            try:
                value = float(value_str)
            except Exception:
                continue

            if unit == "wh":
                value = value / 1000.0

            area_name = entity_area_map.get(entity_id)
            area_name = _override_area_for_entity(entity_id, area_name)
            if area_name is None:
                area_name = DEFAULT_AREA_FOR_UNASSIGNED

            increment = _get_increment(entity_id, value)
            if increment == 0:
                continue

            increment_total += increment
            counted_entities.append(entity_id)

            prev_area = area_energy.get(area_name, 0.0)
            area_energy[area_name] = prev_area + increment
            lst = area_entities.get(area_name)
            if lst is None:
                lst = []
                area_entities[area_name] = lst
            lst.append(entity_id)

        global TOTAL_ACCUMULATED, AREA_ACCUMULATED
        TOTAL_ACCUMULATED = TOTAL_ACCUMULATED + increment_total

        state.set(
            "sensor.total_energy",
            round(TOTAL_ACCUMULATED, 2),
            {
                "unit_of_measurement": "kWh",
                "device_class": "energy",
                "state_class": "total_increasing",
                "friendly_name": "Total Energy",
                "entities_counted": ", ".join(counted_entities),
                "cost_estimate": round(TOTAL_ACCUMULATED * price, 2),
                "price_used": price,
                "tariff": tariff,
                "last_update": timestamp,
            },
        )

        for area_name, energy in area_energy.items():
            prev_area_total = AREA_ACCUMULATED.get(area_name, 0.0) + energy
            AREA_ACCUMULATED[area_name] = prev_area_total
            sensor_id = f"sensor.total_energy_{_slugify(area_name)}"
            state.set(
                sensor_id,
                round(prev_area_total, 2),
                {
                    "unit_of_measurement": "kWh",
                    "device_class": "energy",
                    "state_class": "total_increasing",
                    "friendly_name": f"Total Energy {area_name}",
                    "entities_counted": ", ".join(area_entities.get(area_name, [])),
                    "cost_estimate": round(prev_area_total * price, 2),
                    "price_used": price,
                    "tariff": tariff,
                    "last_update": timestamp,
                },
            )

        log.info(f"Total energy updated: {round(TOTAL_ACCUMULATED, 2)} kWh, cost: {round(TOTAL_ACCUMULATED * price, 2)} PLN")
        for area_name, energy in area_energy.items():
            log.info(f"➡ {area_name}: {round(AREA_ACCUMULATED[area_name], 2)} kWh")

    except Exception as e:
        log.error(f"Error in calculate_energy: {e}")

@event_trigger("entity_registry_updated")
def _on_entity_registry_updated(**kwargs):
    _refresh_entity_area_map(force=False)

@event_trigger("device_registry_updated")
def _on_device_registry_updated(**kwargs):
    _refresh_entity_area_map(force=False)

@event_trigger("area_registry_updated")
def _on_area_registry_updated(**kwargs):
    _refresh_entity_area_map(force=False)

@time_trigger("cron(* * * * *)")
def total_energy_full():
    calculate_energy()

@service
def total_energy_with_areas_service():
    calculate_energy()


@service
def reset_total_energy():
    global TOTAL_ACCUMULATED, AREA_ACCUMULATED, LAST_VALUES
    TOTAL_ACCUMULATED = 0.0
    AREA_ACCUMULATED = {}
    LAST_VALUES = {}
    log.info("Energy counters reset to zero")
