# Standard libs
import re
import string
# External libs
import anyascii
from nltk.corpus import stopwords
import numpy as np
import pandas as pd
import tqdm

class RoutesPreprocess:

    def __init__(self):
        self.global_rating_order = [
            "F",
            "F+",
            "PD-",
            "PD",
            "PD+",
            "AD-",
            "AD",
            "AD+",
            "D-",
            "D",
            "D+",
            "TD-",
            "TD",
            "TD+",
            "ED-",
            "ED",
            "ED+",
            "ED4",
            "ED5",
            "ED6",
            "ED7"
        ]
        self.hiking_rating_order = [
            "T1",
            "T2",
            "T3",
            "T4",
            "T5"
        ]
        self.engagement_rating_order = [
            "I",
            "II",
            "III",
            "IV",
            "V",
            "VI"
        ]
        self.ski_rating_order = [
            "1.1",
            "1.2",
            "1.3",
            "2.1",
            "2.2",
            "2.3",
            "3.1",
            "3.2",
            "3.3",
            "4.1",
            "4.2",
            "4.3",
            "5.1",
            "5.2",
            "5.3",
            "5.4",
            "5.5",
            "5.6"
        ]
        self.frequentation_order = [
            "quiet",
            "some",
            "crowded",
            "overcrowded"
        ]
        self.condition_rating_order = [
            "awful",
            "poor",
            "average",
            "good",
            "excellent"
        ]
        self.quality_order = [
            "empty",
            "draft",
            "medium",
            "fine",
            "great"
        ]
        self.glacier_rating_order = [
            "easy",
            "possible",
            "difficult",
            "impossible"
        ]
        self.ski_exposition_order = [
            "E1",
            "E2",
            "E3",
            "E4"
        ]
        self.labande_ski_rating_order = [
            "S1",
            "S2",
            "S3",
            "S4",
            "S5",
            "S6",
            "S7"
        ]
        self.risk_rating_order = [
            "X1",
            "X2",
            "X3",
            "X4",
            "X5"
        ]
        self.equipment_rating_order = [
            "P1",
            "P1+",
            "P2",
            "P2+",
            "P3",
            "P3+",
            "P4",
            "P4+"
        ]
        self.ice_rating_order = [
            "1",
            "2",
            "3",
            "3+",
            "4",
            "4+",
            "5",
            "5+",
            "6",
            "6+",
            "7"
        ]
        self.mixed_rating_order = [
            "M1",
            "M2",
            "M3",
            "M3+",
            "M4",
            "M4+",
            "M5",
            "M5+",
            "M6",
            "M6+",
            "M7",
            "M7+",
            "M8"
        ]

    def __ordered_str_to_int(self, df, col, order):
        ordered_str_to_int = { order_str:str(i) for order_str, i in zip(order, range(len(order))) }
        ordered_str_to_int["None"] = np.nan
        df[col] = df[col].astype(str).replace(ordered_str_to_int).astype(float)
        return df

    def __circular_str_to_complexe(self, df, col, order):
        step = 360 / len(order)
        angles_deg = {col_value: i * step for i, col_value in enumerate(order)}
        angles_rad = {col_value: np.deg2rad(angle_deg) for col_value, angle_deg in angles_deg.items()}
        angles_rad_series = df[col].map(angles_rad)
        df[f"{col}_real_part"] = np.cos(angles_rad_series)
        df[f"{col}_imag_part"] = np.sin(angles_rad_series)
        return df

    def __circular_str_list_to_complexe_mean(self, df, col, order):
        pass

    def __cat_to_dummies(self, df, col):
        dummies = pd.get_dummies(df[col], prefix=col)
        df = df.merge(dummies, left_index=True, right_index=True)
        return df

    def __cat_list_to_dummies(self, df, col):
        # col must be a list of values separated by a ","
        df.loc[df[col] == "", col] = None
        df_dummies = df[col].str.split(',',expand=True)
        df_dummies = pd.get_dummies(df_dummies)
        # Get same columns
        unique_cols = {}
        for dcol in df_dummies.columns:
            if not dcol[2:] in unique_cols:
                unique_cols[dcol[2:]] = []
            unique_cols[dcol[2:]].append(dcol)
        # Merge same columns
        for col_base, col_list in unique_cols.items():
            df_dummies[col_base] = df_dummies[col_list].sum(axis=1)
        # Filter columns
        df_dummies = df_dummies[unique_cols.keys()]
        # To bool
        df_dummies = df_dummies.astype(bool)
        # Add prefix
        df_dummies.columns = [f"{col}_{dcol}" for dcol in df_dummies.columns]
        # Merge
        df = df.merge(df_dummies, left_index=True, right_index=True)
        return df

    def __int_list_to_mean(self, df, col):
        df.loc[df[col] == "", col] = None
        df_cols = df[col].str.split(',',expand=True)
        df[f"{col}_mean"] = df_cols.astype(float).mean(axis=1)
        return df

    def __normalize_text(self, text):
        if isinstance(text, str):
            # Remove html tags
            CLEANR = re.compile('<.*?>')
            text = re.sub(CLEANR, '', text)
            # Lower
            text = text.lower()
            # Unicode to ascii
            text = anyascii.anyascii(text)
            # Remove punctuation
            for punctuation in string.punctuation:
                text = text.replace(punctuation, " ")
            # Remove \n
            text = text.replace("\n", " ")
            # Whitespaces
            withspace_regex = re.compile(" +")
            text = re.sub(withspace_regex, ' ', text)
            text = text.strip()
            # Remove stop words
            stop_words = set(stopwords.words('french'))
            stop_words.add("nbsp")
            text = [word for word in text.split(" ") if word not in stop_words]
            # Lemmatize
            # TODO
            # Detokenize
            text = " ".join(text)
            # Whitespaces
            text = re.sub(withspace_regex, ' ', text)
            text = text.strip()
        else:
            text = "" 
        return text

    def __process_text(self, df, col):
        df[f"{col}_normalized"] = df[col].apply(self.__normalize_text)
        return df

    def __augment_with_text(self, df, config):
        text_cols = [key for key, value in config.items() if value["type"] == "text"]
        df["full_text_normalized"] = ""
        for text_col in text_cols:
            df["full_text_normalized"] += df[f"{text_col}_normalized"].astype(str) + " "
        df["full_text_normalized"] = df["full_text_normalized"].str.strip()

        df["is_refuge"] = df["full_text_normalized"].str.contains("refuge")
        df["is_cabane"] = df["full_text_normalized"].str.contains("cabane")
        df["is_arete"] = df["full_text_normalized"].str.contains("arete")
        df["is_glacier"] = df["full_text_normalized"].str.contains("glacier")
        df["is_couloir"] = df["full_text_normalized"].str.contains("couloir")
        df["is_goulotte"] = df["full_text_normalized"].str.contains("goulotte")
        return df

    def preprocess(self, df):
        config = {
            "quality": {
                "type": "ordered_str_to_int",
                "order": self.quality_order
            },
            "glacier_gear": {
                "type": "category"
            },
            "ski_rating": {
                "type": "ordered_str_to_int",
                "order": self.ski_rating_order
            },
            "ski_exposition": {
                "type": "ordered_str_to_int",
                "order": self.ski_exposition_order
            },
            "labande_ski_rating": {
                "type": "ordered_str_to_int",
                "order": self.labande_ski_rating_order
            },
            "labande_global_rating": {
                "type": "ordered_str_to_int",
                "order": self.global_rating_order
            },
            "global_rating": {
                "type": "ordered_str_to_int",
                "order": self.global_rating_order
            },
            "engagement_rating": {
                "type": "ordered_str_to_int",
                "order": self.engagement_rating_order
            },
            "risk_rating": {
                "type": "ordered_str_to_int",
                "order": self.risk_rating_order
            },
            "equipment_rating": {
                "type": "ordered_str_to_int",
                "order": self.equipment_rating_order
            },
            "ice_rating": {
                "type": "ordered_str_to_int",
                "order": self.ice_rating_order
            },
            "mixed_rating": {
                "type": "ordered_str_to_int",
                "order": self.mixed_rating_order
            },
            "activities": {
                "type": "category_list"
            },
            "durations": {
                "type": "int_list"
            },
            "route_types": {
                "type": "category_list"
            },
            "orientations": {
                "type": "category_list"
            },
            "configuration": {
                "type": "category_list"
            },
            "rock_types": {
                "type": "category_list"
            },
            "country": {
                "type": "category"
            },
            "admin_limits": {
                "type": "category"
            },
            "range": {
                "type": "category"
            },
            "cooked_title": {
                "type": "text"
            },
            "cooked_description": {
                "type": "text"
            },
            "cooked_summary": {
                "type": "text"
            },
            "cooked_slope": {
                "type": "text"
            },
            "cooked_remarks": {
                "type": "text"
            },
            "cooked_gear": {
                "type": "text"
            },
            "cooked_external_resources": {
                "type": "text"
            },
            "cooked_route_history": {
                "type": "text"
            },
            "cooked_title_prefix": {
                "type": "text"
            }
        }
        for column, preprocess in tqdm.tqdm(config.items()):
            if preprocess["type"] == "ordered_str_to_int":
                df = self.__ordered_str_to_int(df, column, preprocess["order"])
            elif preprocess["type"] == "category":
                df = self.__cat_to_dummies(df, column)
            elif preprocess["type"] == "category_list":
                df = self.__cat_list_to_dummies(df, column)
            elif preprocess["type"] == "text":
                df = self.__process_text(df, column)
            elif preprocess["type"] == "int_list":
                df = self.__int_list_to_mean(df, column)
        df = self.__augment_with_text(df, config)
        return df