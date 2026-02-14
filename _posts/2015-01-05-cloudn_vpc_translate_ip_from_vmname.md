---
layout: post
title: Cloudn VPCにて、VM名からIPを翻訳するワンライナー
description: Cloudn VPCにて、VM名からIPを翻訳するワンライナー
tags: [クラウド, ネットワーク, 自動化]
ogp: /assets/images/ogp/2015-01-05-cloudn_vpc_translate_ip_from_vmname_ogp.png
---

CloudnのようなIaaS基盤を使うと、サーバに振られるPublicIPは動的に決定される。
CI等で自動化する場合は、このIPを取得するケースが増えてくるのだけど、
これをサクッと取得したいケースがある。そういうときのためのワンライナーの紹介。

### ``cloudnmonkey``と``jq``を使ってサクッと取得する

```
cloudmonkey list vpcs name=VPCのお名前 | jq '.vpc[0].id' | tr -d '"' | xargs -Ivviidd cloudmonkey list virtualmachines vpcid=vviidd name=VMのお名前 | jq '.virtualmachine[0].publicip' | tr -d '"'
```

当たり前だけど、cloudmonkeyのconfigは設定済じゃないと動きません。
