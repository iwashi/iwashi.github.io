---
layout: page
title: タグ別の記事
permalink: /tags/
nav_exclude: true
---

<div class="tag-page">
  {% assign sorted_tags = site.tags | sort %}

  {% if sorted_tags.size > 0 %}
  {% for tag in sorted_tags %}
  <section class="tag-section" id="tag-{{ tag[0] | slugify }}">
    <h2>{{ tag[0] }} <span class="tag-count">({{ tag[1] | size }})</span></h2>
    <ul class="post-list">
      {% assign posts = tag[1] | sort: "date" | reverse %}
      {% for post in posts %}
      <li>
        <span class="post-meta">{{ post.date | date: "%Y/%m/%d" }}</span>
        <a class="post-link" href="{{ post.url | prepend: site.baseurl }}">{{ post.title }}</a>
      </li>
      {% endfor %}
    </ul>
  </section>
  {% endfor %}
  {% else %}
  <p>まだタグが設定された記事はありません。</p>
  {% endif %}
</div>
