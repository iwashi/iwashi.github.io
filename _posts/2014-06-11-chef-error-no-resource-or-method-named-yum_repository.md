---
layout: post
title: 'Chef ERROR: No resource or method named yum_repository の対処'
description: 'Chef ERROR: No resource or method named yum_repositoryの対処'
category: null
tags: []
ogp: /assets/images/ogp/2014-06-11-chef-error-no-resource-or-method-named-yum_repository_ogp.png
---

## Chefのyum_repositoryにて
以下のエラーが出ちゃった場合

```
ERROR: No resource or method named `yum_repository' for `Chef::Recipe "default"'
```

yum_repositoryというリソースが定義されていないので、
独自にyum向けのcookbookを入れる必要がある。

http://community.opscode.com/cookbooks/yum

またはberkshelfで入れてもOK。

yum_repositoryがてっきり、Chefのデフォルトリソースだと
勘違いした結果、2-3時間ハマってしまった。
ちゃんとドキュメント読みましょう。

### 参考
OpsCodeコミュニティのチャットログに助けられました。

http://community.opscode.com/chat/chef/2013-05-19