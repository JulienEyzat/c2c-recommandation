# External libs
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

class OutingsDistancer:

    def __init__(self, df):
        self.cols = [
            "activities_snow_ice_mixed",
            "elevation_access",
            "elevation_down_snow",
            "elevation_max",
            "elevation_min",
            "elevation_up_snow",
            # "frequentation",
            "glacier_rating",
            "height_diff_down",
            "height_diff_up",
            "length_total",
            # "participant_count",
            # "snow_quality",
            # "snow_quantity",
            # "global_rating",
            "height_diff_difficulties",
            "engagement_rating",
            "hiking_rating",
            "ski_rating",
            "labande_global_rating",
            "is_refuge",
            "is_cabane",
            "is_arete",
            "is_glacier",
            "is_couloir",
            "is_goulotte"
        ]
        self.df = df.copy()

        self.__fillna()

    def __fillna(self):
        for col in self.cols:
            if self.df[col].isna().any():
                self.df[col] = self.df[col].fillna(self.df[col].median())

    def get_sim_outings_from_outing(self, outing_id):
        selected_index = self.df[self.df["document_id"] == outing_id].index
        other_index = self.df[~(self.df["document_id"] == outing_id)].index

        scaler = StandardScaler()
        scaler = scaler.fit(self.df[self.cols])
        scaled_data = scaler.transform(self.df[self.cols])

        similary_matrix = cosine_similarity(scaled_data[selected_index], scaled_data[other_index])

        self.df.loc[selected_index, "SUGGESTION"] = 1
        self.df.loc[other_index, "SUGGESTION"] = similary_matrix.max(axis=0)

        sim_outings = self.df.sort_values("SUGGESTION", ascending=False).loc[(self.df["SUGGESTION"] < 1), ["cooked_title", "link", "SUGGESTION"]].head(30)

        return sim_outings.to_markdown(index=False)