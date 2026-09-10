"""Create an interactive Arc Layer map of Arctic research connections."""

from pathlib import Path

import pandas as pd
import pydeck as pdk


OUTPUT_PATH = Path(__file__).with_name("arctic_globe_view.html")
COUNTRIES_URL = "https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_50m_admin_0_scale_rank.geojson"


HUBS = [
    {"name": "Longyearbyen", "country": "Norway", "longitude": 15.6469, "latitude": 78.2232},
    {"name": "Reykjavik", "country": "Iceland", "longitude": -21.9426, "latitude": 64.1466},
    {"name": "Nuuk", "country": "Greenland", "longitude": -51.7216, "latitude": 64.1835},
    {"name": "Tromso", "country": "Norway", "longitude": 18.9553, "latitude": 69.6492},
    {"name": "Murmansk", "country": "Russia", "longitude": 33.0749, "latitude": 68.9707},
    {"name": "Kiruna", "country": "Sweden", "longitude": 20.2253, "latitude": 67.8558},
    {"name": "Fairbanks", "country": "United States", "longitude": -147.7164, "latitude": 64.8378},
    {"name": "Utqiagvik", "country": "United States", "longitude": -156.7887, "latitude": 71.2906},
    {"name": "Inuvik", "country": "Canada", "longitude": -133.7218, "latitude": 68.3607},
    {"name": "Cambridge Bay", "country": "Canada", "longitude": -105.0597, "latitude": 69.1169},
    {"name": "Svalbard", "country": "Norway", "longitude": 16.0, "latitude": 80.0},
    {"name": "Tiksi", "country": "Russia", "longitude": 128.8694, "latitude": 71.6366},
]


ROUTES = [
    ("Reykjavik", "Nuuk", "North Atlantic observations"),
    ("Reykjavik", "Longyearbyen", "Polar climate monitoring"),
    ("Tromso", "Longyearbyen", "Research vessel support"),
    ("Tromso", "Kiruna", "Aurora and atmosphere studies"),
    ("Murmansk", "Longyearbyen", "Arctic logistics"),
    ("Murmansk", "Tiksi", "Northern Sea Route logistics"),
    ("Fairbanks", "Utqiagvik", "Alaska field research"),
    ("Fairbanks", "Inuvik", "Permafrost observations"),
    ("Utqiagvik", "Cambridge Bay", "Sea ice observations"),
    ("Inuvik", "Cambridge Bay", "Northwest Passage monitoring"),
    ("Longyearbyen", "Svalbard", "High Arctic observatory access"),
    ("Svalbard", "Tiksi", "Pan-Arctic data exchange"),
]


def build_route_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    hubs = pd.DataFrame(HUBS)
    coordinates = hubs.set_index("name")
    routes = pd.DataFrame(
        [
            {
                "source_name": source,
                "target_name": target,
                "route": route,
                "source_longitude": coordinates.loc[source, "longitude"],
                "source_latitude": coordinates.loc[source, "latitude"],
                "target_longitude": coordinates.loc[target, "longitude"],
                "target_latitude": coordinates.loc[target, "latitude"],
            }
            for source, target, route in ROUTES
        ]
    )
    return hubs, routes


def build_deck() -> pdk.Deck:
    hubs, routes = build_route_data()

    arc_layer = pdk.Layer(
        "ArcLayer",
        data=routes,
        get_source_position="[source_longitude, source_latitude]",
        get_target_position="[target_longitude, target_latitude]",
        get_source_color=[71, 191, 190],
        get_target_color=[244, 126, 88],
        get_width=2.5,
        great_circle=True,
        auto_highlight=True,
        pickable=True,
        parameters={"cullMode": "none"},
    )

    hub_layer = pdk.Layer(
        "ScatterplotLayer",
        data=hubs,
        get_position="[longitude, latitude]",
        get_fill_color=[246, 238, 208],
        get_line_color=[35, 58, 64],
        get_radius=28000,
        line_width_min_pixels=1,
        stroked=True,
        pickable=True,
    )

    country_layer = pdk.Layer(
        "GeoJsonLayer",
        id="arctic-globe-base",
        data=COUNTRIES_URL,
        stroked=False,
        filled=True,
        get_fill_color=[38, 76, 82],
    )

    view_state = pdk.ViewState(latitude=73, longitude=0, zoom=1.8)
    return pdk.Deck(
        layers=[country_layer, arc_layer, hub_layer],
        views=[pdk.View(type="_GlobeView", controller=True, width=1000, height=700)],
        initial_view_state=view_state,
        map_provider=None,
        parameters={"cull": True},
        tooltip={
            "html": "<b>{source_name} to {target_name}</b><br/>{route}",
            "style": {"backgroundColor": "#102a30", "color": "#f6eed0"},
        },
        description="Arctic research and logistics connections",
    )


if __name__ == "__main__":
    deck = build_deck()
    deck.to_html(str(OUTPUT_PATH), notebook_display=False, css_background_color="black")
    print(f"Wrote {OUTPUT_PATH}")