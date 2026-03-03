import pandas as pd
import io


def append_to_dataframe(df: pd.DataFrame, data: dict) -> pd.DataFrame:
    """
    Append a telemetry row to a DataFrame.
    """
    new_row = pd.DataFrame([data])
    return pd.concat([df, new_row], ignore_index=True)


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """
    Convert DataFrame to CSV bytes for Streamlit download.
    """
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")