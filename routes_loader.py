# Standard libs
import json
import os
# External libs
import pandas as pd
import tqdm

class RoutesLoader:

    def __init__(self, input_data_directory):
        self.doc_type = "routes"
        self.input_data_directory = input_data_directory
        self.input_doc_directory = os.path.join(self.input_data_directory, self.doc_type)

        self.__init_dict_keys()

    def __init_dict_keys(self):
        self.doc_direct_keys = [
            "document_id",
            "quality",
            "main_waypoint_id",
            "elevation_min",
            "elevation_max",
            "height_diff_up",
            "height_diff_down",
            "route_length",
            "difficulties_height",
            "height_diff_access",
            "height_diff_difficulties",
            "glacier_gear",
            "lift_access",
            "ski_rating",
            "ski_exposition",
            "labande_ski_rating",
            "labande_global_rating",
            "global_rating",
            "engagement_rating",
            "risk_rating",
            "equipment_rating",
            "ice_rating",
            "mixed_rating"
        ]
        self.doc_list_keys = [
            "activities",
            "durations",
            "route_types",
            "orientations",
            "configuration",
            "rock_types"
        ]
        self.doc_cooked_keys = [
            "lang",
            "title",
            "description",
            "summary",
            "slope",
            "remarks",
            "gear",
            "external_resources",
            "route_history",
            "title_prefix"
        ]

    def load(self):
        docs = []
        for doc_file in tqdm.tqdm(os.listdir(self.input_doc_directory)):
            # Open outings
            doc_path = os.path.join(self.input_doc_directory, doc_file)
            with open(doc_path) as f:
                json_doc = json.load(f)
            doc = {}
            # General infos
            for doc_direct_key in self.doc_direct_keys:
                doc[doc_direct_key] = json_doc.get(doc_direct_key, None)
            # General infos in lists
            for doc_list_key in self.doc_list_keys:
                if not doc_list_key in json_doc or json_doc[doc_list_key] is None:
                    doc[doc_list_key] = ""
                else:
                    doc[doc_list_key] = ",".join(json_doc[doc_list_key])
            # Position
            doc["geom"] = json_doc["geometry"]["geom"]
            # Postition
            for area in json_doc["areas"]:
                key = area["area_type"]
                value = area["locales"][0]["title"]
                doc[key] = value
            # Text
            for cooked_key in self.doc_cooked_keys:
                doc[f"cooked_{cooked_key}"] = json_doc["cooked"].get(cooked_key, None)
            # Add doc link
            doc["link"] = f"https://www.camptocamp.org/{self.doc_type}/{doc['document_id']}"
            # Save
            docs.append(doc)
        # Create dataframe
        df = pd.DataFrame(docs)
        return df

    def save(self, df, output_directory):
        output_file_path = os.path.join(output_directory, f"{doc_type}.csv")
        df.to_csv(output_file_path, index=False)