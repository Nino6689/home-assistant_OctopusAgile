"""OctopusAgile sensor platform (async, modernized)."""
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from datetime import datetime, timedelta
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up OctopusAgile sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
    OctopusAgileRateSensor(coordinator, "previous"),
    OctopusAgileRateSensor(coordinator, "current"),
    OctopusAgileRateSensor(coordinator, "next"),
        OctopusAgileRateSensor(coordinator, "min"),
    ])

class OctopusAgileRateSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, rate_type):
        super().__init__(coordinator)
        self._rate_type = rate_type
    self._attr_name = f"Octopus Agile {rate_type.capitalize()} Rate"
    self._attr_unique_id = f"octopus_agile_{rate_type}_rate"
    self._attr_unit_of_measurement = "p/kWh"
    @property
    def state(self):
        rates = self.coordinator.data.get("rates", {})
        if not rates:
            return None
        now = datetime.utcnow()
    rounded = now.replace(second=0, microsecond=0, minute=(0 if now.minute < 30 else 30))
    rounded_str = rounded.strftime("%Y-%m-%dT%H:%M:%SZ")
    if self._rate_type == "previous":
            prev = rounded - timedelta(minutes=30)
            prev_str = prev.strftime("%Y-%m-%dT%H:%M:%SZ")
            return round(rates.get(prev_str, 0), 2)
        elif self._rate_type == "current":
            return round(rates.get(rounded_str, 0), 2)
        elif self._rate_type == "next":
            next_ = rounded + timedelta(minutes=30)
            next_str = next_.strftime("%Y-%m-%dT%H:%M:%SZ")
            return round(rates.get(next_str, 0), 2)
        elif self._rate_type == "min":
            return round(min(rates.values()), 2) if rates else None
        return None
    @property
    def extra_state_attributes(self):
        return {}
def setup_platform(hass, config, add_entities, discovery_info=None):

"""OctopusAgile sensor platform (async, modernized)."""
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up OctopusAgile sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        OctopusAgileRateSensor(coordinator, "previous"),
        OctopusAgileRateSensor(coordinator, "current"),
        OctopusAgileRateSensor(coordinator, "next"),
        OctopusAgileRateSensor(coordinator, "min"),
    ])



from datetime import datetime, timedelta

class OctopusAgileRateSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, rate_type):
        super().__init__(coordinator)
        self._rate_type = rate_type
        self._attr_name = f"Octopus Agile {rate_type.capitalize()} Rate"
        self._attr_unique_id = f"octopus_agile_{rate_type}_rate"
        self._attr_unit_of_measurement = "p/kWh"

    @property
    def state(self):
        rates = self.coordinator.data.get("rates", {})
        if not rates:
            return None
        now = datetime.utcnow()
        rounded = now.replace(second=0, microsecond=0, minute=(0 if now.minute < 30 else 30))
        rounded_str = rounded.strftime("%Y-%m-%dT%H:%M:%SZ")
        if self._rate_type == "previous":
            prev = rounded - timedelta(minutes=30)
            prev_str = prev.strftime("%Y-%m-%dT%H:%M:%SZ")
            return round(rates.get(prev_str, 0), 2)
        elif self._rate_type == "current":
            return round(rates.get(rounded_str, 0), 2)
        elif self._rate_type == "next":
            next_ = rounded + timedelta(minutes=30)
            next_str = next_.strftime("%Y-%m-%dT%H:%M:%SZ")
            return round(rates.get(next_str, 0), 2)
        elif self._rate_type == "min":
            return round(min(rates.values()), 2) if rates else None
        return None

    @property
    def extra_state_attributes(self):
        return {}


class PreviousRate(Entity):
    """Representation of a Sensor."""

    def __init__(self, hass):
        """Initialize the sensor."""
        self.hass = hass
        self.entity_id = "sensor.octopus_agile_previous_rate"
        self._state = None
        # self._hass = hass
        self._attributes = {}
        # if "region_code" not in self.config["OctopusAgile"]:
        #     _LOGGER.error("region_code must be set for OctopusAgile")
        # else:
        region_code = hass.states.get("octopusagile.region_code").state
        self.myrates = Agile(region_code)

        self.timer(dt_util.utcnow())


    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Octopus Agile Previous Rate'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "p/kWh"

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        return self._attributes

    @property    
    def should_poll(self):
        """Return if polling is required."""
        # Disable polling as we're going to update 
        # with the octopusagile.half_hour service
        return False

    def timer(self, nowtime):
        roundedtime = self.myrates.round_time(nowtime)
        nexttime = roundedtime + timedelta(minutes=30)
        self.schedule_update_ha_state(True)
        # Setup timer to run again in 30
        track_point_in_time(self.hass, self.timer, nexttime)

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        # attributes = {}
        # attributes['mac'] = 'some data'
        # attributes['sn'] = 'some other data'
        # # attributes['date_to']
        # self._attributes = attributes
        nowtime = self.myrates.round_time(dt_util.utcnow())
        prevtime = nowtime - timedelta(minutes=30)
        rounded_time_str = prevtime.strftime("%Y-%m-%dT%H:%M:%SZ")
        prev_rate = self.hass.states.get("octopusagile.all_rates").attributes.get(rounded_time_str)
        if prev_rate == None:
            _LOGGER.error("Error updating sensor.octopus_agile_previous_rate, check that octopusagile.all_rates populated")
            self._state = "Unknown"
        else:
            prev_rate = round(prev_rate, 2)
            self._state = prev_rate

class CurrentRate(Entity):
    """Representation of a Sensor."""

    def __init__(self, hass):
        """Initialize the sensor."""
        self._state = None
        # self._hass = hass
        self._attributes = {}
        self.hass = hass
        self.entity_id = "sensor.octopus_agile_current_rate"
        # if "region_code" not in self.config["OctopusAgile"]:
        #     _LOGGER.error("region_code must be set for OctopusAgile")
        # else:
        region_code = hass.states.get("octopusagile.region_code").state
        self.myrates = Agile(region_code)
        self.timer(dt_util.utcnow())

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Octopus Agile Current Rate'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "p/kWh"

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        return self._attributes

    @property    
    def should_poll(self):
        """Return if polling is required."""
        # Disable polling as we're going to update 
        # with the octopusagile.half_hour service
        return False

    def timer(self, nowtime):
        roundedtime = self.myrates.round_time(nowtime)
        nexttime = roundedtime + timedelta(minutes=30)
        self.schedule_update_ha_state(True)
        # Setup timer to run again in 30
        track_point_in_time(self.hass, self.timer, nexttime)

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        # attributes = {}
        # attributes['mac'] = 'some data'
        # attributes['sn'] = 'some other data'
        # # attributes['date_to']
        # self._attributes = attributes
        nowtime = self.myrates.round_time(dt_util.utcnow())
        rounded_time_str = nowtime.strftime("%Y-%m-%dT%H:%M:%SZ")
        current_rate = self.hass.states.get("octopusagile.all_rates").attributes.get(rounded_time_str)
        current_rate = round(current_rate, 2)
        self._state = current_rate

class NextRate(Entity):
    """Representation of a Sensor."""

    def __init__(self, hass):
        """Initialize the sensor."""
        self._state = None
        # self._hass = hass
        self._attributes = {}
        self.hass = hass
        self.entity_id = "sensor.octopus_agile_next_rate"
        # if "region_code" not in self.config["OctopusAgile"]:
        #     _LOGGER.error("region_code must be set for OctopusAgile")
        # else:
        region_code = hass.states.get("octopusagile.region_code").state
        self.myrates = Agile(region_code)
        self.timer(dt_util.utcnow())

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Octopus Agile Next Rate'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "p/kWh"

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        return self._attributes

    @property    
    def should_poll(self):
        """Return if polling is required."""
        # Disable polling as we're going to update 
        # with the octopusagile.half_hour service
        return False

    def timer(self, nowtime):
        roundedtime = self.myrates.round_time(nowtime)
        nexttime = roundedtime + timedelta(minutes=30)
        self.schedule_update_ha_state(True)
        # Setup timer to run again in 30
        track_point_in_time(self.hass, self.timer, nexttime)

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        # attributes = {}
        # attributes['mac'] = 'some data'
        # attributes['sn'] = 'some other data'
        # # attributes['date_to']
        # self._attributes = attributes
        nowtime = self.myrates.round_time(dt_util.utcnow())
        nexttime = nowtime + timedelta(minutes=30)
        rounded_time_str = nexttime.strftime("%Y-%m-%dT%H:%M:%SZ")
        next_rate = self.hass.states.get("octopusagile.all_rates").attributes.get(rounded_time_str)
        next_rate = round(next_rate, 2)
        self._state = next_rate

class MinRate(Entity):
    """Representation of a Sensor."""

    def __init__(self, hass):
        """Initialize the sensor."""
        self._state = None
        # self._hass = hass
        self._attributes = {}
        self.hass = hass
        self.entity_id = "sensor.octopus_agile_min_rate"
        # if "region_code" not in self.config["OctopusAgile"]:
        #     _LOGGER.error("region_code must be set for OctopusAgile")
        # else:
        region_code = hass.states.get("octopusagile.region_code").state
        self.myrates = Agile(region_code)
        self.timer(dt_util.utcnow())

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Octopus Agile Minimum Rate'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "p/kWh"

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        return self._attributes

    @property    
    def should_poll(self):
        """Return if polling is required."""
        # Disable polling as we're going to update 
        # with the octopusagile.half_hour service
        return False

    def timer(self, nowtime):
        roundedtime = self.myrates.round_time(nowtime)
        nexttime = roundedtime + timedelta(minutes=30)
        self.schedule_update_ha_state(True)
        # Setup timer to run again in 30
        track_point_in_time(self.hass, self.timer, nexttime)

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        # attributes = {}
        # attributes['mac'] = 'some data'
        # attributes['sn'] = 'some other data'
        # # attributes['date_to']
        # self._attributes = attributes
        new_rates = self.myrates.get_new_rates()["date_rates"]
        rate_dict = self.myrates.get_min_times(1, new_rates, [])
        rate = round(rate_dict[next(iter(rate_dict))], 2)
        # rate = round(self.myrates.get_next_rate(), 2)
        self._state = rate