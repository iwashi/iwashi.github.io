---
layout: post
title: Nginxでオレオレ証明書作成するときの手順メモ
description: ''
tags: [セキュリティ, インフラ, 解説]
ogp: /assets/images/ogp/2014-05-28-make_ssl_certificate_ogp.png
---

## Nginxのインストール -> オレオレSSL証明書を作成するときのメモ
nginxのインストールからSSL作成まで。	

今回はVagrant上のCentOS6.3に対して実行。
Vagrantfileにてipaddressを192.168.33.10を設定。


### 下準備でsslとnginxをインストール

```
// opensslとnginxを入れる
$ sudo yum -y install mod_ssl
$ sudo yum -y install nginx
```

### nginxを動作させる

```
// nginxを立ち上げる＆次回起動時からON
$ sudo chkconfig nginx on
$ sudo service nginx start

// FWをカット（今回は、一時的にフラッシュしているだけ）
$ sudo iptables -F
```

この時点で、ローカルブラウザからhttp://192.168.33.10へアクセスできるのを確認。
また、https://192.168.33.10　へはアクセスNGなのも確認。

### 証明書の準備

```
// SSL保存用のフォルダを作る
$ sudo mkdir /usr/local/etc/ssl
$ cd /usr/local/etc/ssl

// 秘密鍵を作る
$ sudo openssl genrsa -out VAGRANT.key 2048

// 公開鍵を作る
$ sudo openssl req -new -key VAGRANT.key -out VAGRANT.csr

// パスフレーズを省略できるようにする
$ sudo openssl rsa -in VAGRANT.key -out VAGRANT.key

// 証明書を作る。
$ sudo openssl x509 -req -days 3650 -in VAGRANT.csr -signkey VAGRANT.key -out VAGRANT.crt
```

#### nginxに証明書を使うように設定

```
$ sudo vi /etc/nginx/conf.d/default.conf

// 以下を追記
#
# The default server
#
server {
#     listen       80;
    listen       443 ssl;
    ssl on;
    ssl_certificate /usr/local/etc/ssl/VAGRANT.crt;
    ssl_certificate_key /usr/local/etc/ssl/VAGRANT.key;

# あとは省略
}

$ sudo service nginx reload
```

この後に、 ローカルブラウザからhttp://192.168.33.10へ引き続きアクセスできるのを確認。
また、https://192.168.33.10　へはアクセスできるのも確認。
ただし、オレオレ証明書なのでアクセス時はWarningは出る。今回は、当たり前なのでそのまま続行。


