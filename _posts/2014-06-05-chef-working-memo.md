---
layout: post
title: Vagrant & Chef を連携する際のメモ
description: VagrantとChef周りでコケたときのメモ。
tags: [開発環境, 自動化, トラブルシューティング]
ogp: /assets/images/ogp/2014-06-05-chef-working-memo_ogp.png
---

## VagrantのマルチVM
マルチVMをたてるときに、
　config.vm.network
のconfigを各サーバの値にするの忘れて、アドレス競合で30分ハマった。。。ちゃんと
　xxserver.vm.network
のように書く。

たとえばこんな感じ：

``` 
config.vm.define :dbserver do |dbserver|
    dbserver.vm.network "private_network", ip: "192.168.100.20"
end
```


## berkshelf周り

### berkshelfのインストールは

　berks install --path cookbooks
は今やNGで、
 berks vendor cookbooks
が正解。

### Berksfileの一行目
あとBerksfileは
　site :opscode source
じゃなくて 
　"https://api.berkshelf.com "
が正解。

## Chef周り

### Chefのテンプレート

chefのtemplateを作るときは、
なるべくゲスト側でデフォルトで用意されているやつから、作るべき。
コピペ等で作ると、変なスペースとかが入って詰まる。(特にipatbles)
こんなエラー。 no command specified　みたいな。

### Chef x Vagrantのワークフロー

1. まず ``vagrant sandbox on`` か、すでに作業中であれば ``vagrant sandbox commit``
2. ``vagrant ssh`` でログインして、任意の作業をする。例えば、パッケージのインストールとか。
3. 上手くいったら、手順をrecipeに起こす。
4. ``vagrant sandbox rollback``して、recipeを試す。おそらくrecipeで相当コケるので、頑張って何度も試す。頑張るときは、ひとまずrollbackしなくても良いと思う。時間かかるので。
5. 上手くrecipeで、ノードの状態が収束したら、``vagrant sandbox commit`` と ``git commit``しておく。





### Chefでrpmforgeのリポジトリを追加する
こんなレシピ。 

```
bash 'add_rpmforge' do
	user 'root'
	code <<-EOC
		rpm --import http://apt.sw.be/RPM-GPG-KEY.dag.txt
		rpm -i 'http://packages.sw.be/rpmforge-release/rpmforge-release-0.5.2-2.el6.rf.x86_64.rpm'
	EOC
	creates "/etc/yum.repos.d/rpmforge.repo"
end
```

### 



