# Articles by Nir Rozen

Technical essays on systems, performance, and the engineering decisions behind reliable software.

| Article | Supporting material |
| --- | --- |
| [Generation VII: Autonomous Computational Engineering](https://mrquality.github.io/articles/generation-vii/) | [Markdown](generation-vii/article.md) · [Experiments and results](generation-vii/experiments/) |

GitHub Pages serves the generated static pages directly from the root of `main`. The shared layout, navigation, light/dark themes, article contents, RSS feed, and metadata are built from versioned sources.

## Edit and publish

Use Python 3.10 or later:

```sh
python -m pip install -r requirements.txt
python build.py
python build.py --check
python check_site.py
```

Edit `generation-vii/article.md` for article content (including its HTML figures), `site.json` for publication metadata, and `templates/`, `style.css`, or `site.js` for the shared design. Commit the generated HTML and XML with those changes. Pages needs no additional build service. The builder does not execute article code.

The established `/articles/generation-vii/` URL and all experiment and asset paths are retained. Do not rename the article directory when changing its title or moving it within the catalog. The renderer preserves the existing `#experiments` anchor.

## Add a publication

Create its directory and Markdown source, then add an entry to the `publications` array in `site.json`. Start the Markdown with an H1 title, a subtitle paragraph, and a byline paragraph. Subsequent H2 headings generate its table of contents. Use an explicit ISO publication date; reading time is computed from the rendered content. Rebuild the site to update the homepage, article, feed, and sitemap together.

## Optional integrations

Visitor tracking is disabled until `goatcounter_endpoint` contains the public counting endpoint from the owner's GoatCounter account. Do not store an API token in this public repository. Tracking starts after activation; it cannot recover historical visits.

GitHub Discussions can host article conversations without giving commenters permission to change repository files. An article's optional `discussion_url` links to its conversation. For embedded comments, install the giscus GitHub App for this repository only, then set `giscus` to an object with the `repo_id`, `category`, and `category_id` shown by [giscus configuration](https://giscus.app). An Announcements category lets the owner and giscus create discussions while readers can reply. The script is included only when configured.

## Future paid publications

The publication catalog can later link to public overviews of paid reference designs. Keep paid manuscripts, downloadable assets, credentials, and purchaser records outside this public repository. Access control and checkout belong to an authenticated delivery service; hiding a public static file is not access control. No payments or memberships are enabled today.
