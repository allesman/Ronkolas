#!/usr/bin/env bash
# ── Konfiguration ──────────────────────────────────────────────────────────
VENV_DIR=".venv"         # euer venv liegt direkt im Projektroot (Ronkolas/)
WRAPPER="src/wrapper.py"
# ───────────────────────────────────────────────────────────────────────────

set -euo pipefail

# Immer ins Projektverzeichnis (Ronkolas/) wechseln
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── venv anlegen falls nicht vorhanden ─────────────────────────────────────
if [[ ! -d "$VENV_DIR" ]]; then
    echo "[start.sh] venv nicht gefunden – erstelle $VENV_DIR …"
    python3 -m venv "$VENV_DIR"
fi

# ── venv aktivieren ────────────────────────────────────────────────────────
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
echo "[start.sh] venv aktiv: $(which python)"

# ── Abhängigkeiten installieren (falls requirements.txt vorhanden) ─────────
if [[ -f "requirements.txt" ]]; then
    echo "[start.sh] Installiere/aktualisiere Abhängigkeiten …"
    pip install -q -r requirements.txt
fi

# ── Wrapper starten ────────────────────────────────────────────────────────
echo "[start.sh] Starte $WRAPPER …"
exec python "$WRAPPER" "$@"
