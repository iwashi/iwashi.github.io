---
layout: post
title: "Vagrant rbenv chef jekyll メモ集"
description: ""
category: 
tags: []
---

## ポスト全体像

- Vagrant設定メモ
- rbenvのアップグレードメモ
- chefインストールメモ 

### Vagrant boxの追加
今回は Centos 6.5 の追加。

```
$ vagrant box add centos6.5 https://github.com/2creatives/vagrant-centos/releases/download/v6.5.1/centos65-x86_64-20131205.box
```

### sshを楽に
hogehogeは好きなホストネームで。

```
$ vagrant ssh-config --host hogehoge >> ~/.ssh/config
$ ssh hogehoge
```

### プロビジョニング
１点だけ注意で vagrant up によるプロビジョニングは初回のup時のみとなる。
ちゃんとマニュアルは読まないとダメ。

> Provisioners are run in three cases: the initial vagrant up, vagrant provision, and vagrant reload --provision.


### rbenvで入れるrubyバージョンの更新
```
// インストールできる一覧を確認して、
$ rbenv install -list

// 欲しいバージョンがなければ、ruby-buildを更新
$ brew upgrade ruby-build

// 新しいのが出るのを確認して
$ rbenv install -list

// 欲しいバージョンをインストール
$ rbenv install 2.1.1

// インストールしたバージョンがある本当にあるか確認
$ rbenv versions

// システムで使うバージョンを設定
$ rbenv global 2.1.1

// 仮にバージョンが変わっていなければ、 .zshrc　あたりを見なおす
$ vi ~/.zshrc

eval "$(rbenv init -)"      // 左記を追加
```

### Chef, knife-solo インストール

```
$ knife configure
ERROR: Ohai::Exceptions::DependencyNotFound: Can not find a plugin for dependency os
```

となったら、今のバージョンはNGなので、古いバージョンに落とす。

```
$ gem uninstall knife-solo
$ gem uninstall chef
で一旦消して、
$ curl -L https://www.opscode.com/chef/install.sh | sudo bash -s -- -v 11.10.4-1
$ gem install knife-solo
```

すればOK。

### JekyllのPost作成
Postを作るときは、新規にファイルを作ってもいいけど、rakeコマンドを使ったほうが楽。

```
rake post title="タイトルをここに
```

### jekyll serve時のエラー対応
```
$ jekyll serve
YAML Exception reading example.md: invalid byte sequence in US-ASCII
```
となってしまったら、システムエンコーディングを変えればOK。
具体的には.zshrcに以下を追加。

```
export LANG=ja_JP.UTF-8
```

あと、自動リロードしたいときは``--watch``を付与すること。

#### git落ち葉ひろい
Github上のリモートブランチを消すときは、Pull Requestがマージされた後に

```
// masterブランチにいる前提で
$ git fetch origin
$ git merge origin/master
$ git br -d hogebranch
$ git push origin :hogebranch
```

ポイントは最後のコマンドで、実は記載が省略されていて本来は、
```
$ git push origin localbranch:remotebranch
```
という意味なので、今回は空のブランチをリモートのブランチにPushすることで、
結果的に削除するという流れになる。