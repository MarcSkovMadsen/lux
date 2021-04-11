#  Copyright 2019-2020 The Lux Authors.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from lux.interestingness.interestingness import interestingness
from lux.vis.VisList import VisList
import lux
from lux.utils import utils


def univariate(ldf, *args):
    """
    Generates bar chart distributions of different attributes in the dataframe.

    Parameters
    ----------
    ldf : lux.core.frame
            LuxDataFrame with underspecified intent.

    data_type_constraint: str
            Controls the type of distribution chart that will be rendered.

    Returns
    -------
    recommendations : Dict[str,obj]
            object with a collection of visualizations that result from the Distribution action.
    """
    import numpy as np

    if len(args) == 0:
        data_type_constraint = "quantitative"
    else:
        data_type_constraint = args[0][0]

    filter_specs = utils.get_filter_specs(ldf._intent)
    ignore_rec_flag = False
    if data_type_constraint == "quantitative":
        possible_attributes = [
            c for c in ldf.columns if ldf.data_type[c] == "quantitative" and c != "Number of Records"
        ]
        intent = [lux.Clause(possible_attributes)]
        intent.extend(filter_specs)
        examples = ""
        if len(possible_attributes) >= 1:
            examples = f" (e.g., {possible_attributes[0]})"
        recommendation = {
            "action": "Distribution",
            "description": "Show univariate histograms of <p class='highlight-descriptor'>quantitative</p>  attributes.",
            "long_description": f"Distribution displays univariate histogram distributions of all quantitative attributes{examples}. Visualizations are ranked from most to least skewed.",
        }
        # Doesn't make sense to generate a histogram if there is less than 5 datapoints (pre-aggregated)
        if len(ldf) < 5:
            ignore_rec_flag = True
    elif data_type_constraint == "nominal":
        possible_attributes = [
            c for c in ldf.columns if ldf.data_type[c] == "nominal" and c != "Number of Records"
        ]
        examples = ""
        if len(possible_attributes) >= 1:
            examples = f" (e.g., {possible_attributes[0]})"
        intent = [lux.Clause(possible_attributes)]
        intent.extend(filter_specs)
        recommendation = {
            "action": "Occurrence",
            "description": "Show frequency of occurrence for <p class='highlight-descriptor'>categorical</p> attributes.",
            "long_description": f"Occurence displays bar charts of counts for all categorical attributes{examples}. Visualizations are ranked from most to least uneven across the bars. ",
        }
    elif data_type_constraint == "geographical":
        possible_attributes = [
            c for c in ldf.columns if ldf.data_type[c] == "geographical" and c != "Number of Records"
        ]
        examples = ""
        if len(possible_attributes) >= 1:
            examples = f" (e.g., {possible_attributes[0]})"
        intent = [lux.Clause("?", data_type="geographical"), lux.Clause("?", data_model="measure")]
        intent.extend(filter_specs)
        long_description = f"Geographical displays <a href='https://en.wikipedia.org/wiki/Choropleth_map'>choropleths</a> for geographic attribute{examples}, with colors indicating the average measure values. "
        if lux.config.plotting_backend == "matplotlib":
            long_description += "The map visualizations from the 'Geographical' tab are rendered using <a href='https://altair-viz.github.io/'>Altair</a>. Lux does not currently support geographical maps with Matplotlib. If you would like this feature, please leave us a comment at <a href='https://github.com/lux-org/lux/issues/310'>issue #310</a> to let us know!"
        recommendation = {
            "action": "Geographical",
            "description": "Show choropleth maps of <p class='highlight-descriptor'>geographic</p> attributes",
            "long_description": long_description,
        }
    elif data_type_constraint == "temporal":
        intent = [lux.Clause("?", data_type="temporal")]
        intent.extend(filter_specs)
        recommendation = {
            "action": "Temporal",
            "description": "Show trends over <p class='highlight-descriptor'>time-related</p> attributes.",
            "long_description": "Temporal displays line charts for all attributes related to datetimes in the dataframe.",
        }
        # Doesn't make sense to generate a line chart if there is less than 3 datapoints (pre-aggregated)
        if len(ldf) < 3:
            ignore_rec_flag = True
    if ignore_rec_flag:
        recommendation["collection"] = []
        return recommendation
    vlist = VisList(intent, ldf)
    for vis in vlist:
        vis.score = interestingness(vis, ldf)
    vlist.sort()
    recommendation["collection"] = vlist
    return recommendation
