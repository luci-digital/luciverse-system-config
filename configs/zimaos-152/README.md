# ZimaOS 192.168.1.152 Snapshot

This directory mirrors selected runtime config files captured from `zimacube`.

Included:
- CasaOS compose files modified during image pinning and service recreation.

Intentionally excluded (sensitive/runtime-local):
- `/DATA/mosquitto/config/password_file`
- `/DATA/.bashrc`
- `/DATA/.bash_profile`

Operational notes:
- MQTT broker currently includes temporary smoke credential user created during validation.
- 1Password item created for smoke test: `vgfz5zyn2zcqim2afsmi56yjem`.
