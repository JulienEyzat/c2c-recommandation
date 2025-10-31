# Standard libs
import json
import os
# External libs
import pandas as pd
import tqdm

class OutingsLoader:

    def __init__(self, input_data_directory):
        self.doc_type = "outings"
        self.input_data_directory = input_data_directory
        self.input_doc_directory = os.path.join(self.input_data_directory, self.doc_type)

        self.__init_dict_keys()

    def __init_dict_keys(self):
        self.doc_direct_keys = [
            "document_id",
            "quality",
            "access_condition",
            "condition_rating",
            "date_end",
            "date_start",
            "elevation_access",
            "elevation_down_snow",
            "elevation_max",
            "elevation_min",
            "elevation_up_snow",
            "frequentation",
            "glacier_rating",
            "height_diff_down",
            "height_diff_up",
            "hut_status",
            "length_total",
            "lift_status",
            "partial_trip",
            "participant_count",
            "public_transport",
            "hiking_rating",
            "snow_quality",
            "snow_quantity",
            "global_rating",
            "height_diff_difficulties",
            "engagement_rating",
            "ski_rating",
            "labande_global_rating"
        ]
        self.doc_list_keys = [
            "avalanche_signs",
            "activities"
        ]
        self.cooked_keys = [
            "lang",
            "title",
            "description",
            "summary",
            "access_comment",
            "avalanches",
            "conditions",
            "conditions_levels",
            "hut_comment",
            "participants",
            "route_description",
            "timing",
            "weather"
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
            # Associated routes
            doc["associated_route_ids"] = []
            doc["associated_route_title_prefixes"] = []
            doc["associated_route_titles"] = []
            for associated_route in json_doc["associations"]["routes"]:
                doc["associated_route_ids"].append(associated_route["document_id"])
                doc["associated_route_titles"].append(associated_route["locales"][0]["title"])
                doc["associated_route_title_prefixes"].append(associated_route["locales"][0]["title_prefix"])
            # Associated users
            doc["associated_user_ids"] = []
            doc["associated_user_names"] = []    
            doc["associated_forum_usernames"] = []
            for associated_user in json_doc["associations"]["users"]:
                doc["associated_user_ids"].append(associated_user["document_id"])
                doc["associated_user_names"].append(associated_user["name"])
                doc["associated_forum_usernames"].append(associated_user["forum_username"])
            # Postition
            for area in json_doc["areas"]:
                key = area["area_type"]
                value = area["locales"][0]["title"]
                doc[key] = value
            # Text
            for cooked_key in self.cooked_keys:
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