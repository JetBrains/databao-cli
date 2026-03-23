import pandas as pd
from prettytable import PrettyTable

DEFAULT_MAX_DISPLAY_ROWS = 10


def dataframe_to_prettytable(df: pd.DataFrame, max_rows: int = DEFAULT_MAX_DISPLAY_ROWS) -> str:
    """Convert a pandas DataFrame to a prettytable string."""
    table = PrettyTable()
    table.field_names = list(df.columns)
    for _, row in df.head(max_rows).iterrows():
        table.add_row([str(v) for v in row])
    return str(table)
