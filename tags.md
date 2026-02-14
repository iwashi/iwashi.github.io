---
layout: page
title: タグ
permalink: /tags/
---

<div class="tag-page">
  {% assign sorted_tags = site.tags | sort %}

  {% if sorted_tags.size > 0 %}
  <h2>タグ一覧</h2>
  <ul class="tag-cloud">
    {% for tag in sorted_tags %}
    <li>
      <a href="#tag-{{ tag[0] | slugify }}">{{ tag[0] }} <span class="tag-count">({{ tag[1] | size }})</span></a>
    </li>
    {% endfor %}
  </ul>

  <h2>タグ別の記事</h2>
  {% for tag in sorted_tags %}
  <section class="tag-section" id="tag-{{ tag[0] | slugify }}">
    <h3>{{ tag[0] }} <span class="tag-count">({{ tag[1] | size }})</span></h3>
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
  <p>まだタグが設定された記事はありません。記事の front matter に <code>tags</code> を追加するとここに表示されます。</p>
  {% endif %}
</div>
