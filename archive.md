---
layout: page
title: すべての記事
permalink: /archive/
---

<div class="archive">
  {% assign postsByYear = site.posts | group_by_exp: "post", "post.date | date: '%Y'" %}
  {% for year in postsByYear %}
  <h2>{{ year.name }}</h2>
  <ul class="post-list">
    {% for post in year.items %}
    <li>
      <span class="post-meta">{{ post.date | date: "%m/%d" }}</span>
      <a class="post-link" href="{{ post.url | prepend: site.baseurl }}">{{ post.title }}</a>
    </li>
    {% endfor %}
  </ul>
  {% endfor %}
</div>