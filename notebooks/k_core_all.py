# Not a notebook, but made for data analysis
# Jupyter would crash if I tried to run this in a notebook, by looking I found out that it didn't have enough memory (I have 16GB of RAM)
from ip_analysis_tool.util.graph_getter import get_graph_by_date
from ip_analysis_tool.util.date_util import get_date_object
from ip_analysis_tool.k_core import get_max_k_core, k_core_decomposition
from ip_analysis_tool.visualize.graph import visualize_graph, visualize_graph_map

# All time
from ip_analysis_tool.enums import TimeInterval
all_time_graph = get_graph_by_date(time_interval=TimeInterval.ALL)
k_core_dec = k_core_decomposition(all_time_graph)
all_time_graph_k_core = get_max_k_core(
    k_core_dec
)

print("K-core decomposition done")

visualize_graph_map(all_time_graph_k_core, name="scratchpad/K-jadro zo všetkých záznamov na mape.png", save=False)
visualize_graph(all_time_graph_k_core, name="scratchpad/K-jadro zo všetkých záznamov.png", output_size=(2000, 2000))

from ip_analysis_tool.enums import TimeInterval
from ip_analysis_tool.util.geo_data_util import get_geo_data
data : dict = get_geo_data(all_time_graph_k_core.vp.ip[v] for v in all_time_graph_k_core.vertices())
for entry in (all_time_graph_k_core.vp.ip[v] for v in all_time_graph_k_core.vertices()):
    print(
        "IP Address:", entry,
        ", City:", data[entry]["city"]["names"]["en"],
        "Country:", data[entry]["country"]["names"]["en"],
        "Province:",
        (data[entry].get("subdivisions") and data[entry]["subdivisions"][0].get("names", {}).get("en")) or "N/A",
        "Location:", data[entry]["location"]
    )