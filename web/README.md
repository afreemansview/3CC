# First website design

A static, responsive visual prototype. No model calls, account system, or publishing backend is connected. Quotes retain their supplied provenance; fictional conversations are not presented as real exchanges.

From the repository root, run:

```sh
python3 -m http.server 8000 --directory web
```

Open the local server in your browser. The website is a self-contained `index.html`, with its CSS and JavaScript embedded so previews do not lose their styling through separate asset paths. There is no build step. Google Fonts are optional; local fallback fonts work without network access. Stop the server with Ctrl+C.

Profiles open as accessible dialogs. The side-door button selects a different background fragment. Animation can be paused and honors the system's reduced-motion preference. Hosting and domain configuration are not yet connected.

The visual palette uses violet gradients and purple code rain. The reader-comment form is a design preview only: it validates required fields locally but does not transmit or retain input. Real comments require a backend, private verified email sign-in, storage, and moderation controls. Phone verification is a possible later addition.

## Public hosting on GitHub Pages

The repository's `Publish website` GitHub Actions workflow deploys only `web/` on updates to `main`. In repository Settings → Pages, select **GitHub Actions** as the build and deployment source. Then run **Publish website** from the Actions tab if the initial push happened before Pages was enabled. The expected project URL is `https://afreemansview.github.io/3CC/`; confirm a successful deployment before sharing it. No API keys, private ledgers, or backend code are included in this deployment. This publishes the visual prototype only; email verification and live comments remain unconnected.
