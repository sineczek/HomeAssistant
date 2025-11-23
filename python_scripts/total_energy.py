day_price = 1.25
night_price = 0.70
day_start = 6
day_end = 22

hour = datetime.datetime.now().hour
price = day_price if day_start <= hour < day_end else night_price
tariff = 'day' if day_start <= hour < day_end else 'night'
timestamp = datetime.datetime.now().isoformat()

area_totals = {}
area_entities = {}
global_total = 0.0
global_entities = []
common_total = 0.0
common_entities = []

for entity_id in hass.states.entity_ids('sensor'):
    if entity_id.startswith('sensor.total_energy'):
        continue

    state_obj = hass.states.get(entity_id)
    if state_obj is None:
        continue

    if state_obj.attributes.get('device_class') == 'energy':
        try:
            value = float(state_obj.state)
            unit = state_obj.attributes.get('unit_of_measurement', '').lower()
            if unit == 'wh':
                value = value / 1000

            global_total += value
            global_entities.append(entity_id)

            area = state_obj.attributes.get('area_id')
            if area:
                if area not in area_totals:
                    area_totals[area] = 0.0
                    area_entities[area] = []
                area_totals[area] += value
                area_entities[area].append(entity_id)
            else:
                common_total += value
                common_entities.append(entity_id)

        except ValueError:
            continue

hass.states.set(
    'sensor.total_energy',
    round(global_total, 2),
    {
        'unit_of_measurement': 'kWh',
        'device_class': 'energy',
        'state_class': 'total_increasing',
        'friendly_name': 'Total Energy',
        'entities_counted': ', '.join(global_entities),
        'cost_estimate': round(global_total * price, 2),
        'price_used': price,
        'tariff': tariff,
        'area_name': 'Global',
        'last_update': timestamp
    }
)

hass.states.set(
    'sensor.total_energy_common',
    round(common_total, 2),
    {
        'unit_of_measurement': 'kWh',
        'device_class': 'energy',
        'state_class': 'total_increasing',
        'friendly_name': 'Total Energy (No Area)',
        'entities_counted': ', '.join(common_entities),
        'cost_estimate': round(common_total * price, 2),
        'price_used': price,
        'tariff': tariff,
        'area_name': 'Nieprzypisane',
        'last_update': timestamp
    }
)

if common_entities:
    hass.states.set(
        'sensor.unassigned_energy_entities',
        'Found Unassigned',
        {
            'friendly_name': 'Unassigned Energy Entities',
            'entities': ', '.join(common_entities),
            'last_update': timestamp
        }
    )
else:
    hass.states.set(
        'sensor.unassigned_energy_entities',
        'All Good',
        {
            'friendly_name': 'Unassigned Energy Entities',
            'last_update': timestamp
        }
    )

for area, total in area_totals.items():
    hass.states.set(
        f'sensor.total_energy_{area.lower()}',
        round(total, 2),
        {
            'unit_of_measurement': 'kWh',
            'device_class': 'energy',
            'state_class': 'total_increasing',
            'friendly_name': f'Total Energy {area}',
            'entities_counted': ', '.join(area_entities[area]),
            'cost_estimate': round(total * price, 2),
            'price_used': price,
            'tariff': tariff,
            'area_name': area,
            'last_update': timestamp
        }
    )