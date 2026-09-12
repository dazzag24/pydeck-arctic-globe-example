"""Create an interactive Arc Layer map of Arctic research connections."""

from pathlib import Path

import pandas as pd
import pydeck as pdk


OUTPUT_PATH = Path(__file__).with_name("arctic_globe_view.html")
DATA_PATH = Path(__file__).with_name("data") / "20261109_Data.csv"
COUNTRIES_URL = "https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_50m_admin_0_scale_rank.geojson"


REQUIRED_COLUMNS = [
    "prev_lat",
    "prev_long",
    "dest_lat",
    "dest_long",
    "frame1_pct",
    "Journey",
]


def frame1_color(value: float | None) -> list[int]:
    if value is None or pd.isna(value):
        return [145, 145, 145]

    fraction = max(0.0, min(float(value), 100.0)) / 100.0
    low = (44, 123, 182)
    high = (215, 48, 39)
    return [round(start + fraction * (end - start)) for start, end in zip(low, high)]


def build_route_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    data = pd.read_csv(DATA_PATH)
    missing_columns = set(REQUIRED_COLUMNS) - set(data.columns)
    if missing_columns:
        raise ValueError(f"Missing required CSV columns: {sorted(missing_columns)}")

    numeric_columns = ["prev_lat", "prev_long", "dest_lat", "dest_long", "frame1_pct"]
    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    route_columns = ["prev_lat", "prev_long", "dest_lat", "dest_long"]
    routes = data.dropna(subset=route_columns).copy()
    routes["Journey"] = routes["Journey"].fillna("Journey unavailable")
    routes["route_color"] = routes["frame1_pct"].apply(frame1_color)
    routes = routes.rename(
        columns={
            "prev_long": "source_longitude",
            "prev_lat": "source_latitude",
            "dest_long": "target_longitude",
            "dest_lat": "target_latitude",
        }
    )

    source_hubs = routes[["source_latitude", "source_longitude"]].rename(
        columns={"source_latitude": "latitude", "source_longitude": "longitude"}
    )
    target_hubs = routes[["target_latitude", "target_longitude"]].rename(
        columns={"target_latitude": "latitude", "target_longitude": "longitude"}
    )
    hubs = pd.concat([source_hubs, target_hubs], ignore_index=True).drop_duplicates()
    return hubs, routes


def build_deck() -> pdk.Deck:
    hubs, routes = build_route_data()

    arc_layer = pdk.Layer(
        "ArcLayer",
        data=routes,
        get_source_position="[source_longitude, source_latitude]",
        get_target_position="[target_longitude, target_latitude]",
        get_source_color="route_color",
        get_target_color="route_color",
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
            "html": "<b>{Journey}</b>",
            "style": {"backgroundColor": "#102a30", "color": "#f6eed0"},
        },
        description="Arctic research and logistics connections",
    )


if __name__ == "__main__":
    deck = build_deck()
    deck.to_html(str(OUTPUT_PATH), notebook_display=False, css_background_color="black")
    print(f"Wrote {OUTPUT_PATH}")