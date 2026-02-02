import logging
import plotly.graph_objects as go
from flask import Blueprint, render_template, current_app

from .odoo_jsonrpc import OdooJsonRpcClient, OdooConfig, OdooAuthError, OdooJsonRpcError
from .metrics import partners_to_df, compute_cards, agg_month, agg_active, agg_country

logger = logging.getLogger(__name__)
bp = Blueprint("web", __name__)


@bp.get("/")
def index():
    settings = current_app.config["SETTINGS"]

    try:
        cfg = OdooConfig(
            url=settings.odoo_url,
            db=settings.odoo_db,
            username=settings.odoo_user,
            password=settings.odoo_password,
        )

        client = OdooJsonRpcClient(cfg)
        uid = client.odoo_login()

        partners = client.search_read([["active", "=", True]])
        df = partners_to_df(partners)

        if df.empty:
            return render_template("index.html", error="No data found.", charts=None)

        # Aggregations
        top_n = 10
        s_active = agg_active(df)
        s_country = agg_country(df, top_n=top_n)
        s_month = agg_month(df)
        cards = compute_cards(df)

        # --- Plotly: Pizza (x_cliente_ativo)
        fig_active = go.Figure(
            data=[go.Pie(
                labels=s_active.index.tolist(),
                values=s_active.values.tolist(),
                hole=0.3,
                textinfo="percent+label",
                hovertemplate="<b>%{label}</b><br>Contatos: %{value}<br>Percentual: %{percent}<extra></extra>",
            )]
        )
        fig_active.update_layout(
            title="Cliente ativo (x_cliente_ativo)",
            legend_title_text="Status",
            margin=dict(t=60, b=20, l=20, r=20),
        )

        # --- Plotly: Bars (Top countries)
        fig_country = go.Figure(
            data=[go.Bar(
                x=s_country.index.tolist(),
                y=s_country.values.tolist(),
                hovertemplate="<b>%{x}</b><br>Contatos: %{y}<extra></extra>",
            )]
        )
        fig_country.update_layout(
            title=f"Contatos por país (Top {top_n})",
            xaxis_title="País",
            yaxis_title="Quantidade de contatos",
            margin=dict(l=40, r=20, t=60, b=60),
        )

        # --- Plotly: Line (creation by month)
        fig_month = go.Figure(
            data=[go.Scatter(
                x=s_month.index.astype(str).tolist(),
                y=s_month.values.tolist(),
                mode="lines+markers",
                hovertemplate="<b>%{x|%Y-%m}</b><br>Contatos criados: %{y}<extra></extra>",
            )]
        )

        fig_month.update_layout(
            title="Criação de contatos por mês (create_date)",
            xaxis_title="Mês",
            yaxis_title="Qtd. contatos",
        )

        fig_month.update_xaxes(
            type="category",
            dtick="M1",
            tickformat="%Y-%m",
            categoryorder="category ascending",
        )

        charts = {
            "active": fig_active.to_json(),
            "country": fig_country.to_json(),
            "month": fig_month.to_json(),
        }

        return render_template(
            "index.html",
            error=None,
            cards=cards,
            charts=charts
        )

    except OdooAuthError:
        logger.exception("Authentication error")
        return render_template("index.html", error="Invalid credentials for Odoo(.env).", charts=None)
    except OdooJsonRpcError as e:
        logger.exception("Odoo JSON-RPC error")
        return render_template("index.html", error=f"Error to call Odoo JSONRPC: {e}", charts=None)
    except Exception as e:
        logger.exception("Unexpected error")
        return render_template("index.html", error=f"Unexpected error: {e}", charts=None)
