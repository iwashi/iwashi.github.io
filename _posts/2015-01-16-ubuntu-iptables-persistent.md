---
layout: post
title: "Ubuntuでiptablesの設定をiptables-persistentで永続化する"
description: "Ubuntuでiptablesの設定をiptables-persistentで永続化する"
category: 
tags: []
---

Ubuntuではiptablesを永続保持（再起動しても動くように）するにはちょっと工夫が必要。
色々な方法があるみたいだが、サクッとできる方法として ``iptables-persistent``を使う方法がある。
本記事ではそれの簡単な紹介。

### 進め方

全体の流れとしては、

1. iptablesにルール追加
2. iptables-persistentのインストール

となる。

#### 1. iptablesにルール追加

まず先にiptablesに必要なルールを入れておく。
簡単な例だと、特定のIPからだけSSHを許可したければ

```
$ sudo iptables -A INPUT -p tcp -s 好きなIP --dport 22 -j ACCEPT
```

と追加しておく。


#### 2. iptables-persistentのインストール	

iptables-persistentをインストールすると、それまでに登録されているiptablesの情報が永続化される。
具体的には、 ``/etc/iptables/rules.v4`` と ``/etc/iptables/rules.v6``が吐出されて、これが起動時に読み込まれる（はず）。
インストールは簡単：

```
// 必要に応じてapt-get updateもしてください
$ sudo apt-get install iptables-persistent
```

これで再起動しても残るようになった。（試しにsudo rebootなんかでやってみるといい）

#### おまけ

保存やリロードは・・・

```
$ sudo /etc/init.d/iptables-persistent save 
$ sudo /etc/init.d/iptables-persistent reload

// または直で叩いてもいい

$ sudo iptables-restore < /etc/iptables/rules.v4
``` 

