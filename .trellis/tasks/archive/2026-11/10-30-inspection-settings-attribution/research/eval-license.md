# Evaluation license findings

## Decision after the user's correction

Use `LGPL-3.0-or-later` for the Sub2API evaluation adaptation.
Keep the original CPA plugin MIT license in `licenses/CPA-Codex-Candy-Eval-MIT.txt`.
Keep its `Copyright (c) 2026 Hao Wang` line and all permission and warranty text.
Keep existing dependency notices under their original licenses.
Use `LGPL-3.0-or-later` for quota and the plugin template too.
Quota changes Sub2API's existing services, routes, repository, and Vue components directly.
Its standalone-MIT treatment in the earlier plan was incomplete for those upstream modifications.
Keep the parent build/installer code under MIT with its separate scope statement.

The plugin changes are modifications to Sub2API source, not only independent programs using an API.
Use the upstream LGPL modification terms for those changes and the same project license for the template.
Do not describe inherited MIT code as code originally licensed under LGPL.

## Verified sources

- [Sub2API v0.2.19 README](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/README.md#license)
  explicitly states GNU LGPL v3.0 "or later".
- [Sub2API v0.2.19 LICENSE](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/LICENSE)
  contains the LGPLv3 text.
- [GNU LGPLv3](https://www.gnu.org/licenses/lgpl-3.0.html), sections 0, 2, 4, and 6,
  defines applications, combined works, modified versions, distribution conditions, and later versions.
- Eval commit `a096211b7e015edbd0af784b6bdf883c1d349618` introduced the root MIT license.
  Git records Hao Wang as the author. The notice belongs to inherited CPA plugin code.

The local v0.2.19 source is `/tmp/sub2api-v0219-upgrade.TcfHlc/source`.
Its upstream commit is `dece26153621959ccd7635814f4b2d08304e681a`.
The English README states the license at line 941. The Chinese and Japanese READMEs agree.

## Code and package evidence

- `patches/0007-sub2api-integration.patch` modifies the upstream server, routes, account service, and frontend navigation.
  It imports `internal/codexeval` into the same program.
- Both build paths use `CGO_ENABLED=0` and build `./cmd/server` with the evaluation code.
  This is not a separate service that only calls the Sub2API HTTP API.
- `patches/0006-evaluation-ui.patch` contains the footer at line 2664.
  Its current license link says MIT and points to the original CPA repository.
- Eval `scripts/build.py:71` copies root `LICENSE` and `licenses/` into the installer.
- Parent `scripts/build.py:59` collects each plugin's root `LICENSE` and `licenses/` recursively.
- Both installers embed the collected `licenses` directory.
  Current license collections include LGPLv3, but omit the accompanying GPLv3 text.

## Planned correction

1. Put the unmodified LGPLv3 text in eval root `LICENSE`.
   Add a separate project scope statement for `LGPL-3.0-or-later` and the inherited MIT code.
   Do not alter the Free Software Foundation copyright in the license text.
2. Preserve the original root MIT text as `licenses/CPA-Codex-Candy-Eval-MIT.txt`.
3. Add the official [GPLv3 text](https://www.gnu.org/licenses/gpl-3.0.txt) as `licenses/GPL-3.0.txt`.
4. Update the existing footer license label to `LGPL-3.0-or-later` and link to this repository's root `LICENSE`.
   Preserve CPA credit. Add Sub2API credit and references to the GPL and LGPL copies in the same footer.
5. Reuse recursive license collection and adapt root/plugin namespaces for direct standalone builds.
   Inspect the required license inputs in each complete build kit and combined package.

Keep the approved README restoration exact. It has no project-wide MIT license declaration.
Replace quota's staged MIT-only correction with a root LGPLv3 text and `or-later` scope statement.
Preserve `2026 Nanboom233` for its own attribution without changing the license text's FSF attribution.
Give quota and the template their own upstream LGPL and GPL texts for independent packaging.
Do not add `THIRD_PARTY_NOTICES.txt`, another manifest, a licensing guide, or a license test suite.

## Review correction: embedded Lucide icons

The evaluation UI patch embeds Lucide SVG paths and identifies them as ISC-licensed.
Its license collection lacked the original Lucide license.
Add the official [Lucide LICENSE](https://github.com/lucide-icons/lucide/blob/81875c8c42d2320fa5123b37fee3554f4ca2bddc/LICENSE) as eval `licenses/Lucide-LICENSE.txt`.
The source revision is `81875c8c42d2320fa5123b37fee3554f4ca2bddc`, dated 2026-10-29.
Eval commit `6cac3a27` introduced the embedded sprite without a package version pin.
Keep the complete ISC text and its included Feather-derived icon MIT notice with their original copyright holders.
The existing recursive collector includes this file in standalone and combined installers. No separate notices file is needed.

## Parent Sub2API-Plugins license

The parent owns the independent build script, installer source, and tests.
It has no root patch directory. Its build discovers plugin patches and downloads Sub2API separately.
The installer module imports Go standard-library packages and embeds the separate Sub2API executable as compressed data.
It does not import or link Sub2API packages into the installer code.
Keep MIT for this independent build and installer code, with `2026 Nanboom233` attribution.
The LGPL obligations still apply to the contained Sub2API executable.
Embedding the executable does not change its license to MIT.

Add a short scope statement to parent root `LICENSE`, separate from its MIT permission text.
Identify parent-owned code as MIT. Identify Sub2API and plugins as components under their respective licenses.
Add parent `licenses/GPL-3.0.txt` alongside the existing `licenses/Sub2API-LGPL-3.0.txt`.
This makes the parent package's upstream license collection independent of the eval plugin.
Use existing `collect_licenses` behavior. Do not add a second packaging mechanism or license test suite.

Eval and quota both modify upstream LGPL source. Their patch adaptations use `LGPL-3.0-or-later`.
The template uses the same project license for future plugin work and its complete build kit.
Inherited MIT and third-party portions retain their original notices in each license collection.
Aligned build-kit copies retain applicable original MIT permission and attribution where that code is reused.
This does not require a separate notices document.

## Distribution condition

LGPLv3 section 4(b) requires both GPLv3 and LGPLv3 copies with a combined work.
Section 4(c) covers displayed copyright notices and references to those copies.
Section 4(d)(0) requires suitable corresponding source and application material for a statically combined distribution.
The public repositories and upstream tag provide source inputs. License copies alone do not establish compliance for a binary release.
Before later binary publication, provide the exact corresponding source and build material through that release's distribution channel.
CI artifact publication follows this task's explicit GitHub authorization boundary.
Use the exact public source revisions and build material for those artifacts. Do not add a new source-release platform.
