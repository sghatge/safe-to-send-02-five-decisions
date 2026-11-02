"""Five decisions for AI agent tool calls: allow, allow_masked, dry_run, needs_approval, block.

Allow/block is too coarse for CRM work. This engine shows the three decisions in the middle,
where an agent can still help without acting alone. Standard library only, synthetic data.
"""
import json
import re
import sys

EMAIL = re.compile(r"[^@\s]+@[^@\s]+")
PII_FIELDS = {"email", "first_name", "last_name", "phone", "address"}
WRITE_SQL = re.compile(r"\b(insert|update|delete|drop|truncate|alter|merge)\b", re.I)


def mask_value(field, value):
    if value is None:
        return value
    if field == "email":
        return EMAIL.sub(lambda m: m.group(0)[0] + "***@***", str(value))
    return str(value)[:1] + "***"


def mask_rows(rows):
    return [{k: (mask_value(k, v) if k in PII_FIELDS else v) for k, v in r.items()} for r in rows]


def decide(call):
    """Return (decision, reason, safe_alternative) for one agent call."""
    tool = call["tool"]
    if tool in {"schema_browse", "audience_count", "delivery_qa"}:
        return "allow", "read-only metadata or aggregate", None
    if tool == "query_run":
        if WRITE_SQL.search(call.get("sql", "")):
            return "block", "query looks like a write", "describe the change; a human runs it"
        if call.get("returns_rows") and PII_FIELDS & set(call.get("fields", [])):
            return "allow_masked", "row-level personal data", None
        return "allow", "read-only query", None
    if tool == "js_execute":
        return "dry_run", "server-side script is explained, never executed", None
    if tool == "data_export":
        return "block", "data leaves the platform", "export aggregate counts only"
    if tool in {"delivery_send", "workflow_start"}:
        if call.get("qa_passed") is False:
            return "block", "pre-send QA failed", "fix the failing checks first"
        approvers = 2 if call.get("volume", 0) > 100_000 else 1
        return "needs_approval", f"{approvers} human approver(s) required", None
    return "block", "tool not named in policy (fail closed)", "ask a human to add it to the policy"


def run_session(calls):
    out = []
    for c in calls:
        decision, reason, alt = decide(c)
        row = {"call": c["id"], "tool": c["tool"], "decision": decision, "reason": reason}
        if alt:
            row["instead"] = alt
        if decision == "allow_masked":
            row["preview"] = mask_rows(c.get("sample", []))[:2]
        out.append(row)
    return out


def main(path):
    with open(path, encoding="utf-8") as fh:
        calls = json.load(fh)
    results = run_session(calls)
    counts = {}
    for r in results:
        counts[r["decision"]] = counts.get(r["decision"], 0) + 1
        line = f"{r['call']:>3}  {r['tool']:<15} {r['decision']:<15} {r['reason']}"
        if "instead" in r:
            line += f"  -> instead: {r['instead']}"
        print(line)
        if "preview" in r:
            print(f"     masked preview: {r['preview']}")
    print("\n" + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "examples/session.json")
