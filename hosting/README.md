# Website hosting and handoff

## Shared source

The repository's root `index.html` is the self-contained club catalogue and October 9 fair page. Everyone can propose edits through a PR; the existing main-branch review policy remains unchanged. Club descriptions/organizers/logos are edited directly in that file. Missing data is intentionally marked N/A.

Keep inline images, alphabetic Latin-then-Cyrillic ordering, separate organizer sections, descriptions up to 70 words, and the student council separate from clubs. Never add private Discord exports, email lists or credentials.

## Temporary backend

Anton owns Cloudflare Pages project `tues-clubs-bridge`, serving:

- `https://clubs.toni.foo/`: temporary hosting/preview on his domain.
- `https://info.elsys.club/`: public club address once this repo's DNS change is merged/applied and its certificate activates.

The advanced-mode Pages adapter reads only `main/index.html` from this public repository. Approved merges become visible after GitHub/Cloudflare cache refresh, typically within a few minutes; source changes in unmerged branches are never fetched. The bundled initial snapshot keeps the site available before the first merge and during GitHub failures. An outage can therefore show the initial version rather than the newest merged edit. `X-Clubs-Source: repository|bootstrap` identifies which is served.

Only GET/HEAD at `/` and `/index.html` are served. Request paths, query strings and headers cannot select other source files or upstreams. This temporary backend is independent of Anton's main website runtime, private services and the earlier 30-day random preview. No hosting credentials are stored in this repository.

`clubs/info.yaml` is DNS-only and targets the Pages project directly. Both custom domains have been registered with that project; changing DNS alone without registration would not configure HTTPS/hostname routing. The existing `elsys.club` HTTP 302 redirect to `https://info.elsys.club/` is already configured outside this repo; no new apex record is included.

Owner-only adapter deployment, with an authenticated Wrangler session:

```bash
python3 hosting/build.py "$HOME/tmp/clubs-pages/dist"
# Copy hosting/wrangler.jsonc to $HOME/tmp/clubs-pages/wrangler.jsonc first.
cd "$HOME/tmp/clubs-pages"
wrangler pages deploy dist --project-name tues-clubs-bridge --branch main --force
```

Build output contains only the approved HTML and `_worker.js`. Wrangler 4.142.0's Pages delegation required `--force` for the existing Pages backend; project creation through that CLI failed, while the Pages API created the project successfully. Do not create another project to work around a transient failure. Adapter tests: `node --test hosting/worker.test.mjs`.

## Kiril's GitHub Pages handoff

1. Enable GitHub Pages on this repository, deploying **main / root**. Root `.nojekyll` and `CNAME` are already included.
2. Configure the custom domain as **info.elsys.club** in Pages settings. The CNAME file alone does not configure the service.
3. Verify the domain as GitHub recommends. Use the verification record/token supplied by GitHub, not a guessed value.
4. Change `clubs/info.yaml` to `value: rangelovkiril.github.io.` through a reviewed PR. Keep it DNS-only while GitHub provisions HTTPS.
5. Once GitHub has issued the certificate, enable Enforce HTTPS and verify `https://info.elsys.club/`, the root redirect, exact page content, logos and mobile layout.
6. Only then ask Anton to retire his Pages custom-domain attachment and temporary project. Leave the root redirect in place until a replacement apex site is verified.

Publishing-source settings require admin/maintainer access; configuring GitHub Pages' custom domain requires admin access. Anton currently has write access, so this one-time setup belongs to Kiril. No extra page-build workflow or Cloudflare credential is needed for branch-based GitHub Pages.

The root redirect is done. The temporary `preserve-manual-apex` OctoDNS processor leaves all apex DNS records outside reconciliation, preserving the manually created proxied A record that supports it. The original PR plan would otherwise have deleted that record; CI tests now protect this boundary.

Hosting directly at `elsys.club` is optional future work, not a prerequisite for the email link. It needs coordinated GitHub custom-domain/DNS changes, and this repository's current zone builder does not consume a separate apex configuration file. When Kiril deliberately brings root DNS into this repo, he must provide a managed apex source and then remove the temporary processor together.
