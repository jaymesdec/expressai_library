# Sprint 1 Bonus — The Conversation Lab (Canvas assignment draft)

> **Teacher note:** Draft to paste into a Canvas **Assignment** for DES 125, Module 1, Week 3 — a bonus that
> sits between Sprint 1 and Sprint 2. Create it **unpublished**, wrap the body in the Franklin institutional
> page template if you use one, and attach/link the notebook `01b-sprint-1-bonus-conversation-lab.ipynb`.
> Suggested setup: **extra credit / optional, text entry, up to ~5 bonus pts.**

---

## 🎙️ Sprint 1 Bonus — The Conversation Lab

**Module 1 · Week 3 · Bonus · Skill: systems thinking**

You just built a persona bot in Sprint 1. Before we move on to Sprint 2, here's an optional bonus: make **two — or three, or four — bots talk to each other**. The twist is that you direct the entire conversation **without typing a single reply yourself.** You control it only through the pieces (each bot's `system_prompt`) and the starting conditions (the opening line).

### 🎯 The bonus challenge

> **Stage a conversation between two traded personas that stays in character for at least 6 turns — and you may only steer it by editing a `system_prompt` or the opening line. You may never type a bot's reply yourself.**

Writing what a bot "should" say is off-limits on purpose. The real skill is steering a system through its **inputs**: who each bot is, and how the conversation starts. Everything after that is the bots reacting to each other.

### What you'll do

1. **Reuse your Sprint 1 persona** and **trade** system prompts with a partner.
2. Stage a **duet**: your bot and your partner's bot, back and forth, seeded by one opening line.
3. **Scale up** to a group chat of 3–4 bots using the `group_chat` helper in the notebook.
4. **Steer without scripting** — change the opening line, add a goal to a persona, add a referee bot, or plant a secret. Observe what changes.
5. **Share it**: announce the personas + opening line, then run your best conversation.

Work in the notebook: **`01b-sprint-1-bonus-conversation-lab.ipynb`** (opens in Google Colab). No API key needed — you connect through the class proxy with the class password, exactly like Sprint 1.

### ⭐ What to submit for bonus credit (optional, text entry)

1. The **two (or more) system prompts** you used — pasted in full.
2. Your **opening line**.
3. A **transcript** of your best conversation (at least 6 turns).
4. **One sentence**: what were the bots trying to do or disagree about?
5. A **two-sentence reflection**: what *surprised* you in the conversation, and what did you change (a prompt or the opening line) to fix or improve it?

### 🏅 Bonus rubric (up to 5 pts)

| Score | What it looks like |
|-------|--------------------|
| **5 — Full bonus** | 6+ in-character turns; a clear tension or goal drives the exchange; the reflection names a *specific* change to a prompt or opening line and what it did. Bots produced a moment the student didn't script. |
| **3 — Partial** | A real back-and-forth of 6+ turns, both personas recognizable; transcript + both prompts + opening line submitted; reflection present but general. |
| **1 — Started** | Bots run but barely stay in character, drift off-topic, or the transcript is under 6 turns; parts of the submission missing. |
| **0** | Not attempted. |

### Transdisciplinary competency

**Systems Thinking** — designing components and initial conditions, then reasoning about the behavior that emerges from their interaction rather than controlling each output directly. (Secondary: **Adaptability** — tuning inputs in response to what the system does.)

### 🛠 Common issues (share with students)

- **Bots just agree politely?** Give them a reason to differ in the opening line and a goal in each `system_prompt`.
- **`[Slow down!]`** — the proxy allows ~15 messages/min and every bot turn counts; use fewer `rounds` or wait ~10s.
- **`NameError`** — run the earlier setup cells first.
- Full reference: the **expressai cheat sheet** (`expressai-cheatsheet.md`).
