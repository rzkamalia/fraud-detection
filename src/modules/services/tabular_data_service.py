import pandas as pd

from datetime import datetime

from src.core.config import app_config
from src.database import Database


class TabularDataService:

    def __init__(self, db: Database):
        self._db = db

    def _transform(self) -> pd.DataFrame:
        """Transform data.

        Returns:
            pd.DataFrame: Transformed DataFrame.
        """
        df = pd.read_csv(app_config.tabular_filename)

        transformed_df = df.copy()
        
        # transform

        transformed_df["transaction_date"] = pd.to_datetime(transformed_df["trans_date_trans_time"]).dt.strftime("%Y-%m-%d")    
        transformed_df["gender"] = transformed_df["gender"].map({"M": "male", "F": "female"})
        transformed_df["job"] = transformed_df["job"].str.lower().str.strip()

        current_year = datetime.now().year
        transformed_df["dob"] = pd.to_datetime(transformed_df["dob"])
        transformed_df["age"] = current_year - transformed_df["dob"].dt.year
        transformed_df = transformed_df.drop("dob", axis=1)
        
        transformed_df["fraud_flag"] = transformed_df["is_fraud"].map({0: False, 1: True})
        
        # select the column that will be used

        transformed_df = transformed_df.rename(columns={
            "category": "merchant_category",
        })
        
        columns_to_select = ["transaction_date", "merchant", "merchant_category", "gender", "state", "job", "age", "fraud_flag"]
        
        return transformed_df[columns_to_select]

    async def _create_table(self) -> None:
        """Create the fraud_detection table if it doesn't exist.
        """
        async with self._db.get_postgres_db() as db_conn, db_conn.cursor() as cursor:
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS fraud_detection (
                    id SERIAL PRIMARY KEY,
                    transaction_date DATE NOT NULL,
                    merchant VARCHAR(255) NOT NULL,
                    merchant_category VARCHAR(255) NOT NULL,
                    gender VARCHAR(10) NOT NULL,
                    state VARCHAR(50) NOT NULL,
                    job VARCHAR(255) NOT NULL,
                    age INTEGER NOT NULL,
                    fraud_flag BOOLEAN NOT NULL
                )
                """
            )
            await db_conn.commit()

    async def _load(self) -> None:
        """Load transformed data to database.
        """
        transformed_df = self._transform()
        
        data = [tuple(row) for row in transformed_df.values]
        
        if not data:
            raise ValueError("No data to insert into database.")
        
        async with self._db.get_postgres_db() as db_conn, db_conn.cursor() as cursor:
            await cursor.executemany(
                """
                INSERT INTO fraud_detection (transaction_date, merchant, merchant_category, gender, state, job, age, fraud_flag)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                data,
            )
            await db_conn.commit()
                
    async def process(self) -> None:
        """Process the tabular data by creating table, transforming and loading it into the database.
        """
        await self._create_table()
        await self._load()