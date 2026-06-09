#!/usr/bin/env python3
"""
Wrapper für main.py
- Fängt alle Exceptions ab und loggt sie
- Startet das Programm bei Absturz automatisch neu
"""

import subprocess
import sys
import time
import logging
from datetime import datetime
from pathlib import Path

# ── Konfiguration ─────────────────────────────────────────────────────────────
# Pfad zu main.py relativ zu diesem wrapper.py
PROGRAM         = Path(__file__).parent / "src" / "start" / "main.py"
RESTART_DELAY   = 5          # Sekunden Pause zwischen Neustarts
MAX_RESTARTS    = 10         # 0 = unbegrenzt
LOG_FILE        = Path(__file__).parent / "wrapper.log"
# ──────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("wrapper")


def run() -> None:
    restarts = 0

    while True:
        log.info(f"Starte {PROGRAM.name} (Versuch #{restarts + 1})")
        start = datetime.now()

        try:
            result = subprocess.run(
                [sys.executable, str(PROGRAM), *sys.argv[1:]],
                check=False,
            )
            exit_code = result.returncode

        except Exception as exc:
            log.exception(f"Unerwarteter Wrapper-Fehler: {exc}")
            exit_code = -1

        uptime = (datetime.now() - start).total_seconds()
        log.warning(
            f"{PROGRAM.name} beendet – Exit-Code {exit_code}, "
            f"Laufzeit {uptime:.1f}s"
        )

        restarts += 1
        if MAX_RESTARTS and restarts >= MAX_RESTARTS:
            log.error(f"Maximale Neustarts ({MAX_RESTARTS}) erreicht. Wrapper beendet.")
            sys.exit(1)

        log.info(f"Neustart in {RESTART_DELAY}s …")
        time.sleep(RESTART_DELAY)


if __name__ == "__main__":
    run()