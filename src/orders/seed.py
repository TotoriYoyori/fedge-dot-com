from sqlalchemy import create_engine
import pandas as pd

def seed_orders() -> None:
    path = Path(__file__).parent / "orders.csv".resolve()
    # path = (Path(__file__).parent / "orders.csv").resolve()
    # sql_engine = create_engine("sqlite:///../orders.db")

    print(path)


seed_orders()