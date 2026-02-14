---
layout: page
title: すべての記事
permalink: /archive/
---

<div class="archive-page tag-page">
  <div class="archive-layout">
    <div class="archive-main">
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

    {% assign sorted_tags = site.tags | sort %}
    {% if sorted_tags.size > 0 %}
    <aside class="archive-sidebar">
      <h2>タグ</h2>
      <ul class="tag-cloud">
        {% for tag in sorted_tags %}
        <li>
          <a class="tag-link" href="{{ "/tags/#tag-" | prepend: site.baseurl }}{{ tag[0] | slugify }}">{{ tag[0] }} <span class="tag-count">({{ tag[1] | size }})</span></a>
        </li>
        {% endfor %}
      </ul>
    </aside>
    {% endif %}
  </div>
</div>
