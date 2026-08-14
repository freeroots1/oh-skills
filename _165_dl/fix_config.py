import yaml, hashlib, base64, os

with open("/root/.hermes/config.yaml", "r") as f:
    cfg = yaml.safe_load(f)

# Remove the old password_hash field
if "basic_auth" in cfg.get("dashboard", {}):
    cfg["dashboard"]["basic_auth"].pop("password_hash", None)
    cfg["dashboard"]["basic_auth"]["password"] = "hermes123"

with open("/root/.hermes/config.yaml", "w") as f:
    yaml.dump(cfg, f, default_flow_style=False)

print("Done")
