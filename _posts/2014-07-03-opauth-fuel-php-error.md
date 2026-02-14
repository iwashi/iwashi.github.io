---
layout: post
title: FuelPHPのOPAuthでハマったこと
description: FuelPHPのOPAuthでハマったこと
tags: [プログラミング, セキュリティ, トラブルシューティング]
ogp: /assets/images/ogp/2014-07-03-opauth-fuel-php-error_ogp.png
---

FuelPHPにてFacebook向けのOPAuthを試していたら半日ハマったので備忘メモ。fuelPHPのログに出るエラー内容は以下のとおり。

```
ERROR - 2014-07-03 15:05:09 --> Warning - session_start(): open(/var/lib/php/session/sess_bbbbbbbbbbbbbbbbbb, O_RDWR) failed: Permission denied (13) in /vagrant/XXXXX/fuel/packages/opauth/classes/OpauthStrategy.php on line 178
ERROR - 2014-07-03 15:05:37 --> Warning - file_get_contents(https://graph.facebook.com/oauth/access_token?client_id=XXXXXXXXXXXXXX&amp;client_secret=YYYYYYYYYYYY): failed to open stream: HTTP request failed! HTTP/1.1 400 Bad Request
in /vagrant/XXXXX/fuel/packages/opauth/classes/OpauthStrategy.php on line 417
ERROR - 2014-07-03 16:40:04 --> Warning - session_start(): open(/var/lib/php/session/sess_aaaaaaaaaaaaaaaaaaa, O_RDWR) failed: Permission denied (13) in /vagrant/XXXXX/fuel/packages/opauth/classes/OpauthStrategy.php on line 178
```

あとnginxにはこんなメッセージも出る。
ぱっと見、タイムアウトが原因っぽく見えるけど、それは不正解。

```
upstream timed out (110: Connection timed out) while reading response header from upstream fastcgi
```

ホント何が厄介だったって、ブラウザからデバッグしていたときに、最初に見える画面がnginxの504エラーなこと。
するとphp-fpmがタイムアウトしているように見えるのだが、実際のエラーはfuelphpのログが正解で、こっちを直せばいい。

解決方法は超簡単で

```
$ sudo chgrp -R nginx session/
```

でおしまい。

### 環境
Vagrant(CentOS)上に Nginx + php-fpm + fuelphpで動かしている。

### おまけ
外部から落としてきたVagrantパッケージを使っていたので、httpdがプリインストールされていた。
そのせいで、`/var/lib/php/session` のグループがapacheになっていて、nginxから書き込めないのでドハマり。

VMのイメージはやっぱり自分の手で作ったほうがいいかも。高い学習コストだったが、良い教訓になった。
