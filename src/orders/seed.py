from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


def seed_orders() -> None:
    path = (Path(__file__).resolve().parent / "orders.csv").resolve()
    # sql_engine = create_engine("sqlite:///../orders.db")

    print(path)


seed_orders()
