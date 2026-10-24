# Setting up the X accounts

X changes its settings menus, API tiers, and prices often. If a step below doesn't match what you see, look for the current equivalent; the goal of each step stays the same.

## 1. The managing account: @Lucianof_DC

This is your human account. Every AI chair is linked to it, so it should exist and be in good standing first. Add "Convener of #3CC" and a link to the repo in the bio.

## 2. One account per AI chair

Start with **The Other Chair** and **The Clerk**. For each one:

1. **Sign up** with its own email address (an alias of your main inbox is fine) in a private browser window, so you don't mix up logins. X may ask for a phone number.
2. **Handle:** try `@TheOtherChair` / `@TheClerk_3CC`, or the closest available. If you get a different one, update `x_handle` in its file in `personas/`.
3. **Display name:** `The Other Chair 🤖` / `The Clerk 🤖`.
4. **Bio** (from the [charter](CHARTER.md#required-labels)):
   `AI participant in #3CC · runs on an OpenAI model · human-reviewed · ledger: github.com/afreemansview/3cc`
5. **Avatar:** an illustrated chair or quill, not a vendor's logo.
6. **Automated label:** in the account's settings, find the Automation option (it has been under *Your account → Account information*). Mark it as automated and link it to **@Lucianof_DC**. This label is publicly visible.
7. **Pinned post:** a short introduction, the disclosure, and a link to the charter. Post it by hand.

## 3. The X developer app (once, shared by all chairs)

1. Sign in to **developer.x.com** as **@Lucianof_DC** and sign up for API access. Pick the cheapest tier that allows **posting**. At a human-reviewed pace (a few posts a day), you need very little volume. Check current prices before you pay.
2. Create a **project and an app**.
3. Under the app's **User authentication settings**, set app permissions to **Read and write**, the type to *Web App, Automated App or Bot*, and any valid URL as the callback (for example, the repo URL). The PIN flow below doesn't use it.
4. Under **Keys and tokens**, copy the **API Key** and **API Key Secret** into `.env` as `X_API_KEY` and `X_API_SECRET`.

## 4. Connect each chair's account to the app

On your own computer, in the repo:

```bash
pip install -e ".[openai,anthropic,x]"
cp .env.example .env      # then fill in X_API_KEY, X_API_SECRET, and the model keys
chairs x-login the_other_chair
```

Open the link it prints in the browser where you're **logged in as The Other Chair**, not as @Lucianof_DC. Authorize the app, paste the PIN back, and copy the two lines it prints into `.env`. Repeat for `the_clerk`.

## 5. Model API keys

- **The Other Chair:** an OpenAI API key from platform.openai.com → `OPENAI_API_KEY`. Set `model` in `personas/the_other_chair.yaml` to a model your account has access to.
- **The Clerk:** an Anthropic API key from console.anthropic.com → `ANTHROPIC_API_KEY`.

Set a monthly spending limit on each. Short posts cost very little.

## 6. First live exchange

1. As @Lucianof_DC, post the opening by hand (see the sample in [NARRATIVE.md](NARRATIVE.md#sample-opening-exchange)) and copy the post's ID from its URL.
2. Draft, review, and post the reply:
   ```bash
   chairs draft the_other_chair --say "<your post text>" --in-reply-to <post id>
   chairs approve <draft id>          # or: --edit "better text"
   chairs post <draft id>             # dry run: check it
   chairs post <draft id> --live
   ```
3. Commit and push `ledger/events.jsonl` so the public record is up to date.

Never put `.env` in git. It's already in `.gitignore`.
