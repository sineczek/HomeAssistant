threshold = 15
low_battery_devices = []

exclude_keywords = ['phone', 'laptop', 'tablet', 'komputer', 'smartfon']

for entity_id in hass.states.entity_ids():
    state = hass.states.get(entity_id)
    friendly_name = state.attributes.get('friendly_name', entity_id)
    
    if any(keyword.lower() in entity_id.lower() for keyword in exclude_keywords):
        continue

    if 'battery' in entity_id.lower() or 'bateria' in entity_id.lower():
        try:
            battery_level = float(state.state)
            if battery_level < threshold:
                low_battery_devices.append(f"{friendly_name}: {battery_level}%")
        except ValueError:
            continue

if low_battery_devices:
    message = "Urządzenia z niskim stanem baterii:\n" + "\n".join(low_battery_devices)
    hass.services.call('persistent_notification', 'create', {
        'title': 'Bateria - alert',
        'message': message
    })
