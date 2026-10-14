from __future__ import annotations

from typing import Callable

TRANSLATIONS: dict[str, dict[str, str]] = {
    "EN": {
        # HUD
        "hud.tag": "AUTONOMOUS ACCOUNTS PAYABLE · DACH",
        "hud.status": "LIVE",
        "hud.sector": "SECTOR",
        # Header
        "app.caption": "Turn every invoice exception into a permanent rule.",
        # Metrics
        "metric.automation_rate": "Automation Rate",
        "metric.automation_rate_help": "Share of invoices processed without human intervention.",
        "metric.open_exceptions": "Open Exceptions",
        "metric.open_exceptions_help": "Exceptions still needing a human decision.",
        "metric.resolved": "Resolved by Rules",
        "metric.resolved_help": "Exceptions auto-resolved because a matching rule exists.",
        "metric.rules": "Rules Learned",
        "metric.rules_help": "Permanent rules learned from answered questions.",
        "metric.invoices": "Invoices Processed",
        "metric.invoices_help": "Total invoices in the current dataset.",
        "metric.vs_baseline": "vs baseline",
        # Tabs
        "tab.dashboard": "Dashboard",
        "tab.queue": "Exception Queue",
        "tab.rules": "Rules Learned",
        "tab.insights": "Supplier Insights",
        "tab.report": "Sprint Report",
        # Dashboard
        "dash.progression": "Automation Rate Progression",
        "dash.mix": "Exception Mix · Open",
        "dash.no_open": "All exceptions resolved. System fully autonomous.",
        "dash.rule_impact": "Rule Impact",
        "dash.rule_impact_empty": "No rules yet. Open the Exception Queue to answer a question.",
        # Queue
        "queue.title": "Open Exceptions",
        "queue.empty": "Every exception is resolved. Automation rate is 100%.",
        "queue.invoice": "Invoice",
        "queue.message": "Message",
        "queue.question": "Question",
        # Rules
        "rules.title": "Rules Learned",
        "rules.empty": "No rules yet. Answer a question in the Exception Queue.",
        "rules.col_id": "Rule ID",
        "rules.col_type": "Type",
        "rules.col_target": "Target",
        "rules.col_rationale": "Rationale",
        "rules.col_created": "Created",
        "rules.remove_title": "Remove a rule",
        "rules.remove_btn": "Delete rule",
        "rules.reset_btn": "Reset all rules",
        # Insights
        "insights.title": "Where automation is leaking",
        "insights.empty": "No open exceptions to analyze.",
        "insights.chart_title": "Top suppliers by open exceptions",
        "insights.caption": "Suppliers at the top are where one rule or one master-data fix unlocks the most automation.",
        # Report
        "report.title": "Automation Sprint Report",
        "report.caption": "The deliverable handed to the customer after each sprint: what changed, what was learned, what is left, and where to aim next.",
        "report.baseline": "Baseline",
        "report.current": "Current",
        "report.rules_learned": "Rules Learned",
        "report.resolved": "Resolved by Rules",
        "report.generate": "Generate & download report",
        "report.download": "Download Markdown",
        # Toasts
        "toast.rule_learned": "Rule learned",
        "toast.rule_removed": "Rule removed",
        "toast.rules_reset": "All rules reset",
    },
    "DE": {
        "hud.tag": "AUTONOME KREDITORENBUCHHALTUNG · DACH",
        "hud.status": "AKTIV",
        "hud.sector": "SEKTOR",
        "app.caption": "Verwandeln Sie jede Rechnungsausnahme in eine dauerhafte Regel.",
        "metric.automation_rate": "Automatisierungsquote",
        "metric.automation_rate_help": "Anteil der Rechnungen, die ohne menschliches Eingreifen verarbeitet werden.",
        "metric.open_exceptions": "Offene Ausnahmen",
        "metric.open_exceptions_help": "Ausnahmen, die noch eine menschliche Entscheidung benötigen.",
        "metric.resolved": "Durch Regeln gelöst",
        "metric.resolved_help": "Ausnahmen, die automatisch durch eine passende Regel gelöst wurden.",
        "metric.rules": "Gelernte Regeln",
        "metric.rules_help": "Dauerhafte Regeln aus beantworteten Fragen.",
        "metric.invoices": "Verarbeitete Rechnungen",
        "metric.invoices_help": "Gesamtzahl der Rechnungen im aktuellen Datensatz.",
        "metric.vs_baseline": "vs. Basiswert",
        "tab.dashboard": "Übersicht",
        "tab.queue": "Ausnahmen",
        "tab.rules": "Regeln",
        "tab.insights": "Lieferanten",
        "tab.report": "Sprint-Bericht",
        "dash.progression": "Verlauf der Automatisierungsquote",
        "dash.mix": "Ausnahmen-Mix · Offen",
        "dash.no_open": "Alle Ausnahmen gelöst. System vollständig autonom.",
        "dash.rule_impact": "Regelwirkung",
        "dash.rule_impact_empty": "Noch keine Regeln. Beantworten Sie eine Frage in den Ausnahmen.",
        "queue.title": "Offene Ausnahmen",
        "queue.empty": "Alle Ausnahmen gelöst. Automatisierungsquote 100%.",
        "queue.invoice": "Rechnung",
        "queue.message": "Meldung",
        "queue.question": "Frage",
        "rules.title": "Gelernte Regeln",
        "rules.empty": "Noch keine Regeln. Beantworten Sie eine Frage in den Ausnahmen.",
        "rules.col_id": "Regel-ID",
        "rules.col_type": "Typ",
        "rules.col_target": "Ziel",
        "rules.col_rationale": "Begründung",
        "rules.col_created": "Erstellt",
        "rules.remove_title": "Regel entfernen",
        "rules.remove_btn": "Regel löschen",
        "rules.reset_btn": "Alle Regeln zurücksetzen",
        "insights.title": "Wo Automatisierung verloren geht",
        "insights.empty": "Keine offenen Ausnahmen zur Analyse.",
        "insights.chart_title": "Top-Lieferanten nach offenen Ausnahmen",
        "insights.caption": "Lieferanten oben auf der Liste sind dort, wo eine Regel oder eine Stammdatenkorrektur am meisten Automatisierung freisetzt.",
        "report.title": "Automatisierungs-Sprint-Bericht",
        "report.caption": "Das Dokument, das dem Kunden nach jedem Sprint übergeben wird: was sich geändert hat, was gelernt wurde, was offen ist und worauf als Nächstes zu zielen ist.",
        "report.baseline": "Basiswert",
        "report.current": "Aktuell",
        "report.rules_learned": "Gelernte Regeln",
        "report.resolved": "Durch Regeln gelöst",
        "report.generate": "Bericht erzeugen & herunterladen",
        "report.download": "Markdown herunterladen",
        "toast.rule_learned": "Regel gelernt",
        "toast.rule_removed": "Regel entfernt",
        "toast.rules_reset": "Alle Regeln zurückgesetzt",
    },
}


def get_translator(lang: str) -> Callable[[str], str]:
    """Return a function t(key) that looks up the current language."""
    table = TRANSLATIONS.get(lang, TRANSLATIONS["EN"])

    def t(key: str) -> str:
        return table.get(key, TRANSLATIONS["EN"].get(key, key))

    return t
