# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Jekyll-based personal technical blog (iwashi.co) focused on engineering topics, particularly WebRTC, cloud infrastructure, and engineering management. The blog is written primarily in Japanese.

## Development Commands

```bash
# Install dependencies
bundle install

# Run development server (auto-rebuilds on changes)
bundle exec jekyll serve

# Build the static site for production
bundle exec jekyll build

# Build with production environment
JEKYLL_ENV=production bundle exec jekyll build
```

## Architecture & Structure

### Jekyll Configuration
- **Jekyll version**: 4.3.2
- **Markdown processor**: Kramdown
- **Permalink structure**: `/:categories/:year/:month/:day/:title`
- **Plugins**: jekyll-mentions, jekyll-redirect-from, jekyll-sitemap, jekyll-feed

### Content Organization
- **Blog posts**: `_posts/` directory with `YYYY-MM-DD-title.md` format
- **Static pages**: Root directory (about.md, contact.md, index.html)
- **Assets**: 
  - Images: `assets/images/` and `assets/imgs/`
  - Legacy Bootstrap theme: `assets/themes/twitter/`

### Layout System
- `default.html`: Base layout with header/footer includes
- `post.html`: Blog post layout (includes Google AdSense integration)
- `page.html`: Static page layout

### Key Technical Details
- **Domain**: Configured via CNAME file for iwashi.co
- **Social Integration**: Twitter (@iwashi86) and GitHub (iwashi) configured
- **Google AdSense**: Integrated in post layout for monetization
- **Future posts**: Enabled in config (`future: true`)
- **Excluded files**: `vendor` directory is excluded from builds

## Important Notes

- Blog content is primarily in Japanese
- When creating new posts, follow the existing naming convention and front matter structure
- The site uses Google AdSense - be careful not to modify the ad integration code
- The `ads.txt` file is present for ad verification
- Images should be placed in `assets/images/` directory