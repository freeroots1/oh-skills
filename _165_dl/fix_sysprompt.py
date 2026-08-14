
import yaml, sys

paths = ["/root/.hermes/config.yaml", "/opt/hermes-gateway/config.yaml"]
for p in paths:
    try:
        with open(p, encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        if "agent" not in cfg:
            cfg["agent"] = {}
        old = cfg["agent"].get("system_prompt", "<none>")
        cfg["agent"]["system_prompt"] = ""
        if p == "/root/.hermes/config.yaml":
            cfg["agent"]["prefill_messages_file"] = "prefill.json"
        else:
            cfg["agent"]["prefill_messages_file"] = "/root/.hermes/prefill.json"
        with open(p, "w", encoding="utf-8") as f:
            yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True, width=120, sort_keys=False)
        print(f"OK {p}: system_prompt cleared (was {str(old)[:40]}...)")
    except Exception as e:
        print(f"FAIL {p}: {e}")
