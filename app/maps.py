# python for_flask.py
from typing import Union
import branca
import folium
import geopandas as gpd

CITY_CENTROIDS = {
    "birmingham": (52.4862, -1.8904),
    "bristol": (51.4545, -2.5879),
    "leeds": (53.798387, -1.547270),
    "london": (51.509505, -0.113977),
    # "greater london": (51.509505, -0.113977),
    "manchester": (53.4808, -2.2426),
}

SPECTRAL = {
    3: ['#fc8d59', '#ffffbf', '#99d594'],
    4: ['#d7191c', '#fdae61', '#abdda4', '#2b83ba'],
    5: ['#d7191c', '#fdae61', '#ffffbf', '#abdda4', '#2b83ba'],
    6: ['#d53e4f', '#fc8d59', '#fee08b', '#e6f598', '#99d594', '#3288bd'],
    7: ['#d53e4f', '#fc8d59', '#fee08b', '#ffffbf', '#e6f598', '#99d594', '#3288bd'],
    8: ['#d53e4f', '#f46d43', '#fdae61', '#fee08b', '#e6f598', '#abdda4', '#66c2a5', '#3288bd'],
    9: ['#d53e4f', '#f46d43', '#fdae61', '#fee08b', '#ffffbf', '#e6f598', '#abdda4', '#66c2a5', '#3288bd'],
    10: ['#9e0142', '#d53e4f', '#f46d43', '#fdae61', '#fee08b', '#e6f598', '#abdda4', '#66c2a5', '#3288bd', '#5e4fa2'],
    11: ['#9e0142', '#d53e4f', '#f46d43', '#fdae61', '#fee08b', '#ffffbf', '#e6f598', '#abdda4', '#66c2a5', '#3288bd', '#5e4fa2']
}

SPECTRAL_R = {k: v[::-1] for k, v in SPECTRAL.items()}


def generate_map(
    data: gpd.GeoDataFrame,
    city: str,
    data_col: str = "weightings",
    colours: list = SPECTRAL_R[10],
    index: list = None,  # values to show on colour bar
    vmin: Union[int, float] = None,  # min value on scale
    vmax: Union[int, float] = None,  # max value on scale
    caption: str = None,  # scale caption
    max_labels: int = 10,  # for scale
    num_steps: int = None,  # set to int for discrete scale
    save_path: str = None,
    zoom_start: int = None,
):
    if isinstance(data, gpd.GeoDataFrame):
        vmin = vmin or data[data_col].min()
        vmax = vmax or data[data_col].max()
        data = data.to_json()
    # add back later
    # elif isinstance(data, dict):
    #     data = json.dumps(data)
    # elif not isinstance(data, str):
    #     raise TypeError("data must be a gdf, dict or json str")
    else:
        raise TypeError("data must be a gdf for now")

    if zoom_start is None:
        zoom_start = 12  # if city in ["birmingham", "london"] else 13

    m = folium.Map(
        location=CITY_CENTROIDS[city],
        zoom_start=zoom_start,
        control_scale=True,
        tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        attr="Google",
    )

    scale = branca.colormap.LinearColormap(
        colors=colours, index=index, vmin=vmin, vmax=vmax, caption=caption, max_labels=max_labels
    )

    if num_steps:
        scale = scale.to_step(num_steps)

    folium.GeoJson(
        data,
        style_function=lambda feature: {
            "fillColor": scale(feature["properties"][data_col]),
            "fillOpacity": 0.7,
            "color": "black",  # border color for the color fills
            "weight": 0.5,  # how thick the border has to be
            "dashArray": "5, 3",  # dashed lines length,space between them
        },
    ).add_to(m)

    scale.add_to(m)

    if save_path:
        m.save(save_path)
        print(" -- saved --")
        print(save_path)

    return m



PARAMS = {
    "rent_weight":0.1,
    "supply_weight":0.2,
    "demand_weight":0.3,
    "num_joints_weight":0.4,
    "num_users_weight":0.5,
    "num_trans_weight":0.7
}
def find_location(params=PARAMS):
    gdf = gpd.read_file("./final_combined_norm.geojson")
    gdf = gdf.fillna(0)
    
    print(params)
    
    rent_weight = float(params["rent_weight"])
    supply_weight = float(params["supply_weight"])
    demand_weight = float(params["demand_weight"])
    num_joints_weight = float(params["num_joints_weight"])
    num_users_weight = float(params["num_users_weight"])
    num_trans_weight = float(params["num_trans_weight"])

    gdf["rent_psf"] = gdf["rent_psf"] * rent_weight
    gdf["supply"] = gdf["supply"] * supply_weight
    gdf["demand"] = gdf["demand"] * demand_weight
    gdf["num_joints"] = gdf["num_joints"] * num_joints_weight
    gdf["num_users"] = gdf["num_users"] * num_users_weight
    gdf["num_trans_weight"] = gdf["num_trans"] * num_trans_weight

    gdf["weightings"] = gdf["rent_psf"]+gdf["supply"]+gdf["demand"]+gdf["num_joints"]
    gdf["weightings"] += gdf["num_users"] + gdf["num_trans_weight"]



    generate_map(
        gdf,
        "london",
        save_path="./templates/temp.html",
        vmax=None,
        num_steps=12,
        caption="Place Index")


