---
layout: post
title: "Upstart/Systemdがあるにも関わらずなぜmonitが必要なのか"
description: "Upstart/Systemdがあるにも関わらずなぜmonitが必要なのか"
category: 
tags: []
---

## はじめに

Linuxの各種ディストリビューションには、UpstartやSystemdがデフォルトでインストールされていることが多い。
たとえば、Ubuntuでは14系ではUpstartが標準装備されているし、15系以降ではSystemdが標準装備になる。

UpstartもSystemdのどちらも、管理するプロセスが死んだときに、死んだプロセスを再起動する仕組みを備えている。
たとえば、Upstartであれば**respawn**というキーワードを仕込んでおけば、再起動する動作をしてくれる。
具体的な設定なこんな感じ：

```
description "サービスの説明とか"
author  "名前と連絡先"

start on runlevel [2345]
stop on runlevel [016]

chdir /hogehoge/
exec foorbar
respawn
```

## 本題：なぜmonitが必要なのか？

予期せぬ理由でプロセスが死んだときに、適切な処置を施すようにプロセス監視は必須だ。
Upstartのrespawnは1つのその仕組として使える。
この記事の本題は、なぜupstartがあるにも関わらず、monitやdaemontoolsが必要なのか？という点だ。
（本記事では特にmonitについてフォーカスして紹介する）

## 回答：monitはより高度な状態確認を提供するからだ

たとえばWebサービスのアプリケーションロジックを提供するプロセスを監視したい場合、
単にプロセスの生存監視をするだけでは十分ではない。
すなわち、プロセスとしては一見、生きているように見えるが、
HTTPに対するレスポンスが返ってこないなど、
ビジネスロジックとして考えれば死んでいるも同然の場合がある。
このようなケースは、Upstartでは拾うことができない。

そこで、monitのようなより高度なプロセス監視ツールが必要になる。
monitでHTTPレベルの死活監視を行うなら以下のような設定を仕込めば良い。

```
if failed port 80 protocol http
  request "/index.html"
  with timeout 10 seconds
  (..以下略..)
```

## おまけ

個人的には、以下の2つ目の回答にもあるように、Upstart/Systemd と monit を併用するのが良いと思う。
なぜかというと、それぞれの目的が異なるから。基本的なところはUpstart/Systemdにまかせて、
粒度の細かい監視はMonitなどの別の監視を利用するのが良いと思う。

- [Is there benefit to using Monit instead of a basic Upstart setup?](http://stackoverflow.com/questions/4722675/is-there-benefit-to-using-monit-instead-of-a-basic-upstart-setup)

## 参考

- [Upstart Stanzas](http://upstart.ubuntu.com/wiki/Stanzas#respawn)
- [Upstart を使ってお手軽 daemon 化](http://heartbeats.jp/hbblog/2013/02/upstart-daemon.html)
