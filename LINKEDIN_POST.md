Safe to Send · Ep 02 — Allow or block is not enough

Most AI guardrails have two settings: allow or block. Real CRM work needs five.

✅ Allow: schema browse, an audience count
🟦 Allow masked: 50 recipient rows, with names and emails hidden before the agent sees them
🧪 Dry run: server-side JavaScript is explained, never executed
⏸️ Needs approval: a send waits for one human, or two above 100,000 recipients
⛔ Block: SQL writes, data exports, failed QA, and any tool nobody named

I ran an 11-call synthetic session through it. 5 calls got an answer straight away, 2 waited for a human, 4 were stopped with a safer alternative. Personal data never reached the agent's context once.

The middle three are where the value is. They let an agent help without letting it act alone. And every block names a safer alternative, so the agent gets redirected, not just stopped.

This repo is ~100 lines of plain Python. Fork it and change the rules to match your platform.

Which decision would you use most?

Repo: https://github.com/sghatge/safe-to-send-02-five-decisions

#SafeToSend #AIAgents #AdobeCampaign #DataPrivacy
