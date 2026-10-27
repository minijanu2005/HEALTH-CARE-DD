import streamlit as st

from auth import require_login
from config import get_settings
from database import get_shared_database
from models.constants import Collection, SyncStatus
from services.sync_service import get_sync_dashboard, push_pending_to_peers
from ui.components import begin_panel, end_panel, kpi_card, page_intro


def render() -> None:
    user = require_login()
    if user["role"] != "Administrator":
        st.error("Administrators only.")
        return

    settings = get_settings()
    db = get_shared_database()

    page_intro(
        "Facilities & distributed sync",
        "Local multi-node demo with authenticated sync — not production cloud hosting.",
    )

    stats = get_sync_dashboard(db)
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Pending outbox", stats["pending"], "Awaiting push", "#F59E0B")
    with c2:
        kpi_card("Conflicts", stats["conflicts"], "Version mismatches", "#EF4444")
    with c3:
        kpi_card("Processed", stats["processed"], "Idempotent messages", "#10B981")

    begin_panel("Node configuration", "Current facility and peer URLs from `.env`")
    st.markdown(
        f"**This node:** `{settings.facility_id}` — {settings.facility_name}  \n\n"
        f"**Peers:** {', '.join(settings.sync_peer_urls) or '*(none — add SYNC_PEER_URLS)*'}"
    )
    if st.button("Push pending sync messages to peers", type="primary", use_container_width=True):
        result = push_pending_to_peers(db)
        st.success(f"Sync push finished: sent={result['sent']} failed={result['failed']}")
    end_panel()

    begin_panel("Recent sync log", "Outbound and inbound attempts")
    logs = list(db[Collection.SYNC_LOG].find().sort("timestamp", -1).limit(20))
    st.dataframe(
        [
            {
                "Time": l.get("timestamp"),
                "Direction": l.get("direction"),
                "Status": l.get("status"),
                "Entity": f"{l.get('entity_type')}:{l.get('entity_id')}",
                "Peer": l.get("peer"),
                "Detail": l.get("detail"),
            }
            for l in logs
        ],
        use_container_width=True,
        hide_index=True,
    )
    end_panel()

    begin_panel("Sync conflicts", "Records kept local when version is newer")
    conflicts = list(db[Collection.SYNC_CONFLICTS].find().sort("timestamp", -1).limit(20))
    if conflicts:
        st.dataframe(conflicts, use_container_width=True, hide_index=True)
    else:
        st.caption("No conflicts recorded.")
    pending = list(db[Collection.SYNC_OUTBOX].find({"status": SyncStatus.PENDING}).limit(10))
    if pending:
        st.warning(f"{len(pending)} message(s) still pending in outbox.")
    end_panel()
