from dataclasses import dataclass
import pandas as pd
import logging

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Cards:
    total_contacts: int
    active_percent: float
    companies_percent: float
    countries: int


def many2one_to_name(field: str) -> str:
    """Odoo search_read return fields many2one as [id, 'name']
    this method return the field formatted as name string
    """
    if isinstance(field, list) and len(field) >= 2:
        return str(field[1])
    return "N/A"


def partners_to_df(partners: list[dict]) -> pd.DataFrame:
    """Convert partner list to pandas dataframe"""
    df = pd.DataFrame(partners)
    if df.empty:
        return df

    # convert country and state to name
    df["country_name"] = df.get("country_id").apply(many2one_to_name)
    df["state_name"] = df.get("state_id").apply(many2one_to_name)

    df["create_date"] = pd.to_datetime(df["create_date"], errors="coerce", utc=True)
    df["create_month"] = df["create_date"].dt.strftime("%Y-%m")

    if "x_cliente_ativo" not in df.columns:
        df["x_cliente_ativo"] = False
    df["x_cliente_ativo"] = df["x_cliente_ativo"].fillna(False).astype(bool)

    if "is_company" not in df.columns:
        df["is_company"] = False
    df["is_company"] = df["is_company"].fillna(False).astype(bool)

    return df


def compute_cards(df: pd.DataFrame) -> Cards:
    total = int(len(df))
    if total == 0:
        return Cards(total_contacts=0, active_percent=0.0, countries=0, companies_percent=0.0)

    active_pct = float(df["x_cliente_ativo"].mean() * 100.0)
    num_countries = int(df["country_name"].replace("N/A", pd.NA).dropna().nunique())
    companies_pct = float(df["is_company"].mean() * 100.0)

    return Cards(
        total_contacts=total,
        active_percent=active_pct,
        countries=num_countries,
        companies_percent=companies_pct,
    )


def agg_active(df: pd.DataFrame) -> pd.Series:
    """Return aggregate active clients data"""
    return df["x_cliente_ativo"].map({True: "Sim", False: "Não"}).value_counts()


def agg_country(df: pd.DataFrame, top_n: int = 10) -> pd.Series:
    """Return aggregate countries data"""
    return df["country_name"].value_counts().head(top_n)


def agg_month(df: pd.DataFrame) -> pd.Series:
    """Return aggregate month date data by order"""
    return df["create_month"].value_counts().sort_index()