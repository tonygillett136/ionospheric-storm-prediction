"""
Historical Storm Events Database

Major geomagnetic storms from 2015-2025 with context and real-world impacts.
This data is matched to actual events in our NASA OMNI historical database.
"""

MAJOR_STORM_EVENTS = [
    {
        "id": "st_patricks_day_2015",
        "name": "St. Patrick's Day Storm",
        "date_start": "2015-03-17",
        "date_end": "2015-03-18",
        "severity": "G4 - Severe",
        "max_kp": 8.0,
        "description": "One of the strongest storms of Solar Cycle 24. Two coronal mass ejections (CMEs) hit Earth's magnetosphere in quick succession.",
        "impacts": [
            "Widespread aurora visible as far south as the northern United States",
            "GPS navigation errors reported",
            "Radio communication disruptions",
            "Power grid fluctuations in high-latitude regions"
        ],
        "scientific_context": "This storm was caused by two CMEs that erupted on March 15, combining to create a particularly powerful geomagnetic storm. The sudden storm commencement occurred at 04:45 UTC on March 17.",
        "noaa_report_url": "https://www.swpc.noaa.gov/news/g4-severe-geomagnetic-storm-watch-17-march-2015",
        "peak_timestamp": "2015-03-17T22:47:00Z",
        "category": "solar_storm"
    },
    {
        "id": "halloween_storm_2015",
        "name": "Halloween Storm 2015",
        "date_start": "2015-10-07",
        "date_end": "2015-10-08",
        "severity": "G3 - Strong",
        "max_kp": 7.0,
        "description": "A high-speed solar wind stream triggered auroral displays across northern regions just before Halloween.",
        "impacts": [
            "Aurora visible in northern Europe and Canada",
            "Minor impacts to satellite operations",
            "HF radio absorption at high latitudes"
        ],
        "scientific_context": "This storm was caused by a coronal hole high-speed stream (CH HSS) rather than a CME, demonstrating that not all geomagnetic storms come from solar eruptions.",
        "peak_timestamp": "2015-10-07T12:00:00Z",
        "category": "solar_wind"
    },
    {
        "id": "december_storm_2015",
        "name": "December 2015 Storm",
        "date_start": "2015-12-19",
        "date_end": "2015-12-20",
        "severity": "G3 - Strong",
        "max_kp": 7.0,
        "description": "End-of-year geomagnetic storm that provided spectacular aurora displays as a holiday gift to northern observers.",
        "impacts": [
            "Bright aurora displays across Scandinavia",
            "Minor satellite anomalies reported",
            "Increased radiation exposure on polar flights"
        ],
        "scientific_context": "This storm resulted from a moderate CME impact combined with favorable IMF orientation (sustained southward Bz component).",
        "peak_timestamp": "2015-12-20T00:00:00Z",
        "category": "solar_storm"
    },
    {
        "id": "september_storm_2017",
        "name": "September 2017 Storm Series",
        "date_start": "2017-09-06",
        "date_end": "2017-09-08",
        "severity": "G4 - Severe",
        "max_kp": 8.0,
        "description": "One of the most significant solar events of the decade. Multiple X-class solar flares and CMEs created a multi-day storm period.",
        "impacts": [
            "Emergency responders switched to alternative communication systems",
            "Airlines rerouted polar flights",
            "Power grid operators placed systems on alert",
            "Aurora visible as far south as Arkansas and Southern California"
        ],
        "scientific_context": "Active region AR2673 produced an X9.3 flare (strongest of Solar Cycle 24) on September 6, followed by Earth-directed CMEs. This was part of a two-week period of intense solar activity.",
        "noaa_report_url": "https://www.swpc.noaa.gov/news/g4-severe-geomagnetic-storm-watch-08-september-2017",
        "peak_timestamp": "2017-09-08T01:00:00Z",
        "category": "solar_storm"
    },
    {
        "id": "august_storm_2018",
        "name": "August 2018 Storm",
        "date_start": "2018-08-25",
        "date_end": "2018-08-26",
        "severity": "G3 - Strong",
        "max_kp": 7.0,
        "description": "Late summer geomagnetic storm during the declining phase of Solar Cycle 24.",
        "impacts": [
            "Aurora visible in northern tier US states",
            "Minor power grid fluctuations",
            "Temporary GPS accuracy degradation"
        ],
        "scientific_context": "Despite occurring during solar minimum approach, this storm demonstrated that significant events can occur even during quiet solar periods.",
        "peak_timestamp": "2018-08-26T06:00:00Z",
        "category": "solar_wind"
    },
    {
        "id": "mothers_day_storm_2024",
        "name": "Mother's Day Storm 2024",
        "date_start": "2024-05-10",
        "date_end": "2024-05-13",
        "severity": "G5 - Extreme",
        "max_kp": 9.0,
        "description": "The first G5 (Extreme) geomagnetic storm since 2003. Active region AR3664 produced numerous X-class flares and multiple Earth-directed CMEs.",
        "impacts": [
            "Aurora visible as far south as Mexico and North Africa",
            "Widespread GPS disruptions affecting precision agriculture",
            "Starlink satellites reported degraded service",
            "Multiple power grid voltage control issues",
            "John Deere tractors experienced GPS outages during planting season"
        ],
        "scientific_context": "This storm marked the strongest geomagnetic activity in over 20 years. Multiple CMEs arrived in rapid succession, creating a rare G5 event during Solar Cycle 25's rise to maximum.",
        "noaa_report_url": "https://www.swpc.noaa.gov/news/g5-extreme-geomagnetic-storm-observed-10-may-2024",
        "peak_timestamp": "2024-05-11T02:00:00Z",
        "category": "solar_storm",
        "notable": True
    }
]

def get_storm_by_id(storm_id: str):
    """Get storm event by ID"""
    for storm in MAJOR_STORM_EVENTS:
        if storm['id'] == storm_id:
            return storm
    return None

def get_storms_by_severity(min_severity: str = "G3"):
    """Get storms matching or exceeding severity level"""
    severity_order = {"G1": 1, "G2": 2, "G3": 3, "G4": 4, "G5": 5}
    min_level = severity_order.get(min_severity[:2], 3)

    return [
        storm for storm in MAJOR_STORM_EVENTS
        if severity_order.get(storm['severity'][:2], 0) >= min_level
    ]

def get_storms_by_category(category: str):
    """Get storms by category (solar_storm, solar_wind, etc.)"""
    return [storm for storm in MAJOR_STORM_EVENTS if storm['category'] == category]

def get_notable_storms():
    """Get storms marked as notable"""
    return [storm for storm in MAJOR_STORM_EVENTS if storm.get('notable', False)]
