
import os
import json
import subprocess
from pathlib import Path
from typing import Optional

class SecretManager:
    """
    LuciVerse Secret Manager
    Dynamically fetches credentials and configuration from 1Password
    to remove physical file dependencies (like fdb.cluster).
    """
    
    def __init__(self, vault: str = "LuciVerse-CORE"):
        self.vault = vault

    def _run_op_command(self, *args) -> Optional[str]:
        """Execute an op CLI command and return its output."""
        try:
            result = subprocess.run(
                ['op'] + list(args),
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"1Password CLI error: {e.stderr}")
            return None

    def get_fdb_cluster_string(self) -> Optional[str]:
        """
        Retrieves the FoundationDB cluster string from 1Password.
        Instead of reading /etc/foundationdb/fdb.cluster, we dynamically
        construct or retrieve the cluster string here.
        """
        # We look for the 'foundationdb-api' item in the specified vault
        # In a full deployment, the cluster string (e.g. docker:docker@172.16.1.152:4500)
        # would be stored in a dedicated field or notes.
        
        # Let's first check if there's a specific field for the cluster string
        item_json = self._run_op_command('item', 'get', 'foundationdb-api', '--vault', self.vault, '--format', 'json')
        if not item_json:
            return None
            
        try:
            item_data = json.loads(item_json)
            fields = item_data.get('fields', [])
            
            # For now, we will construct the cluster string using the known format and the IP
            # Alternatively, if we store the full string in 'notesPlain', we can extract it.
            notes = next((f.get('value') for f in fields if f.get('id') == 'notesPlain'), None)
            
            if notes and "docker:" in notes:
                return notes.strip()
            
            # If not found in notes, we can return the hardcoded stable string for now
            # and instruct the user to update the 1Password item.
            print("Warning: FDB cluster string not found in 1Password notes. Returning fallback.")
            return "docker:docker@172.16.1.152:4500"
            
        except json.JSONDecodeError:
            print("Failed to parse 1Password item JSON.")
            return None

    def ensure_fdb_cluster_file(self, target_path: str = "/tmp/dynamic_fdb.cluster") -> str:
        """
        Ensures a cluster file exists at the target path with the dynamically fetched content.
        Returns the path to the cluster file.
        """
        cluster_string = self.get_fdb_cluster_string()
        if not cluster_string:
            raise RuntimeError("Could not retrieve FoundationDB cluster string from 1Password.")
            
        path = Path(target_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(cluster_string + "\n")
        
        return str(path)

if __name__ == "__main__":
    sm = SecretManager()
    cluster_file = sm.ensure_fdb_cluster_file()
    print(f"Dynamically generated cluster file at: {cluster_file}")
    with open(cluster_file, 'r') as f:
        print(f"Content: {f.read().strip()}")
