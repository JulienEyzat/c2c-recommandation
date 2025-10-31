# Standard libs
import re
import string
# External libs
import anyascii
from nltk.corpus import stopwords
import numpy as np
import pandas as pd
import tqdm

class OutingsPreprocess:

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

    def __ordered_str_to_int(self, df, col, order):
        ordered_str_to_int = { order_str:str(i) for order_str, i in zip(order, range(len(order))) }
        ordered_str_to_int["None"] = np.nan
        df[col] = df[col].astype(str).replace(ordered_str_to_int).astype(float)
        return df

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
            "access_condition": {
                "type": "category"
            },
            "avalanche_signs": {
                "type": "category_list"
            },
            "condition_rating": {
                "type": "ordered_str_to_int",
                "order": self.condition_rating_order
            },
            "frequentation": {
                "type": "ordered_str_to_int",
                "order": self.frequentation_order
            },
            "glacier_rating": {
                "type": "ordered_str_to_int",
                "order": self.glacier_rating_order
            },
            "hut_status": {
                "type": "category"
            },
            "lift_status": {
                "type": "category"
            },
            "hiking_rating": {
                "type": "ordered_str_to_int",
                "order": self.hiking_rating_order
            },
            "snow_quality": {
                "type": "ordered_str_to_int",
                "order": self.condition_rating_order
            },
            "snow_quantity": {
                "type": "ordered_str_to_int",
                "order": self.condition_rating_order
            },
            "global_rating": {
                "type": "ordered_str_to_int",
                "order": self.global_rating_order
            },
            "engagement_rating": {
                "type": "ordered_str_to_int",
                "order": self.engagement_rating_order
            },
            "ski_rating": {
                "type": "ordered_str_to_int",
                "order": self.ski_rating_order
            },
            "labande_global_rating": {
                "type": "ordered_str_to_int",
                "order": self.global_rating_order
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
            "cooked_access_comment": {
                "type": "text"
            },
            "cooked_avalanches": {
                "type": "text"
            },
            "cooked_conditions": {
                "type": "text"
            },
            "cooked_conditions_levels": {
                "type": "text"
            },
            "cooked_hut_comment": {
                "type": "text"
            },
            "cooked_route_description": {
                "type": "text"
            },
            "cooked_timing": {
                "type": "text"
            },
            "cooked_weather": {
                "type": "text"
            },
            "activities": {
                "type": "category_list"
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
        df = self.__augment_with_text(df, config)
        return df