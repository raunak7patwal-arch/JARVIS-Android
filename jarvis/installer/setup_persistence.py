from __future__ import annotations

import getpass
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT.parent) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT.parent),
    )

from jarvis.central.security.persistent_vault import (
    PersistentVault,
)
from jarvis.central.security.persistence import (
    JARVISPersistence,
)


def main():
    print()
    print("======================================")
    print("       JARVIS PERMANENT SETUP")
    print("======================================")
    print()
    print("This creates your local master password.")
    print("JARVIS will NOT display or print it.")
    print()

    vault = PersistentVault()

    if vault.configured:
        print(
            "Master password is already configured."
        )
        print(
            "No existing password will be replaced."
        )
        return

    password1 = getpass.getpass(
        "Create master password: "
    )

    password2 = getpass.getpass(
        "Confirm master password: "
    )

    if password1 != password2:
        print()
        print("ERROR: Passwords do not match.")
        return

    if len(password1) < 8:
        print()
        print(
            "ERROR: Minimum 8 characters required."
        )
        return

    vault.setup_master_password(
        password1
    )

    persistence = JARVISPersistence()
    persistence.create_lineage()

    print()
    print("======================================")
    print("JARVIS PERMANENT SETUP : COMPLETE")
    print("======================================")
    print("Master password : CONFIGURED")
    print("Encrypted vault : READY")
    print("Persistent data : READY")
    print("Lineage         : READY")
    print("Password output : DISABLED")
    print("======================================")
    print("SUCCESS")


if __name__ == "__main__":
    main()
