"""Reusable UI fragments."""

from __future__ import annotations

import streamlit as st


def kpi_card(label: str, value: str | int, sub: str = "", accent: str = "#2563EB") -> None:
    st.markdown(
        f"""
        <div class="kpi-card" style="border-top: 4px solid {accent};">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def panel(title: str, subtitle: str = "") -> None:
    st.markdown(
        f'<div class="panel-head"><h3>{title}</h3><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def page_intro(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="hero-banner compact">
            <h2>{title}</h2>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def begin_panel(title: str, subtitle: str = "") -> None:
    st.markdown('<div class="content-panel">', unsafe_allow_html=True)
    panel(title, subtitle)


def end_panel() -> None:
    st.markdown("</div>", unsafe_allow_html=True)
