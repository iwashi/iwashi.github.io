---
layout: post
title: "Cloudn OpenNW(VPC)にて複数NICするときの挙動"
description: "Cloudn OpenNW(VPC)にて複数NICするときの挙動"
category: 
tags: []
---

CloudnのVPCタイプは、任意のプライベートIPを使えたりして、サービス構築に便利。
より便利に使うには、Template(VMイメージみたいなもの)を使うと良いのだが、
複数NICを使った場合※で気が付きにくい動作差分が生じる。
※公開向けのNICと、メンテナンス向けのNICを分ける場合とか

----

## CentOSとUbuntuで違う？

### CentOSの話 

複数NICを追加する場合に、CentOSだと

- ``/etc/sysconfig/network-scripts/ifcfg-eth0``
- ``/etc/sysconfig/network-scripts/ifcfg-eth1``

を2つ用意したテンプレートがあれば、
VMを作成して、NICを追加すれば、良い感じに動く！と思われるが、実際は上手くいかない。

何が起きるかというと、VM作成時のNIC名がeth2やeth3とズレてしまうのだ。
そのため、ifcfg-ethXを上手く読み込めず、NICが正常に起動しない。

### Ubuntuの話

対してubuntuは``/etc/network/interfaces``に、

```
auto eth0
iface eth0 inet dhcp

auto eth1
iface eth1 inet dhcp
```

と書いてテンプレートを作っておけば、良い感じにNICを読み込んでくれる。
言い換えると、CentOSと異なり、eth2やeth3とずれることが無い。

-----

## まとめ
CentOSとUbuntuを利用して独自テンプレートを使い、複数NICを作るときは注意しよう！

(誰か、CentOSの回避方法を知っていたら教えてください。。。)
