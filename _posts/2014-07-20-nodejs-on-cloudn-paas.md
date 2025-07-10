---
layout: post
title: Node.jsのサーバサイドアプリをCloudn PaaSで10分で動かす
description: Node.jsのサーバサイドアプリをCloudn PaaSで10分で動かす
category: null
tags: []
ogp: /assets/images/ogp/2014-07-20-nodejs-on-cloudn-paas_ogp.png
---

本ポス卜では、Cloudn PaaS(v2) でNode.jsのサーバサイドアプリを動かす手順について記載する。
公式マニュアルにも書いてないので、参考になるかも。

あとCloudn PaaSは、CloudFoundryベースなので、
どこかで詰まったらCloudFoundryの情報を探すと、解決できそう。

## 全体の流れ
全体の流れはざっくり以下のとおり。

1. アクセスキーIDと秘密鍵の準備 (2min)
2. クライアントツールをインストール (3min)
3. アプリを作成 (3min)
4. デプロイ、確認 (2min)

## 1. アクセスキーIDと秘密鍵の準備
APIキーをCloudnのポータルサイトにログインして取得する。
ここから見れるはず。(まだ作ってないhとは作成すること)

https://portal.cloudn-service.com/comgi/listKey

## 2. クライアントツールをインストール
PaaSのコンソールへアクセスすると、「Cloudn PaaS GUD (コマンドラインツール)」なるものが
トップにあるので、環境にあわせてダウンロードする。今回はOSX 64bit。

## 3. アプリを作成

### 3.1 app.js
**app.js**というファイル名で以下をコピペして保存。
やってることは、ただWebサーバを立てているだけ。

```
var http = require('http'),
	host = process.env.VCAP_APP_HOST || 'localhost',
	port = process.env.VCAP_APP_PORT || 3000,
	server = http.createServer(function(req, res){
  res.end("Hello World");
});
server.listen(port, function(){
  console.log("Server started at port %s", server.address().port);
})
```

ポイントは ``process.env.VCAP_APP_HOST`` と ``process.env.VCAP_APP_HOST`` を
設定してあげること。これがないと、PaaSへデプロイしたときに、間違ったhostとportで動作しようとしてコケる。

ちなみにこの時点で ``node app.js`` すれば、http://localhost:3000　で確認できる。

### 3.2 Procfile
**Procfile**というファイル名で以下をコピペして保存。
やってることは、動かす種別(node)とソースファイル(app.js)を指定していること。
(Cloudn PaaSは、Node以外にも色々と動くので、nodeであることをCloudn側に伝えてあげている)

```
web: node app.js
```

### 3.3 package.json
**package.json**というファイル名で以下をコピペして保存。
package.jsonはアプリの情報を色々と書いておくファイル。
今回はサンプルなので、ちょっとだけ書いておこう。

```
{
      "name": "application-name"
    , "version": "0.0.1"
}

```

## 4. デプロイ、確認
最後にアプリをデプロイしよう。

```
// APIのend pointを設定。end pointはデプロイとかで叩くURIのこと。
$ gud api api.paas.jp-e1.cloudn-service.com
```

で、

```
// end pointログインする
$ gud login
```

この後Emailと聞かれるが、そこに1.で準備したアクセスキーIDを入れる。
次にPasswordを聞かれるので、秘密鍵を入れる。(めちゃめちゃわかりにくい...)
これで認証もOK。

最後にデプロイする。

```
$ gud push sample
```

最後のsampleは自由に変えてOK。
上手く行けば色々と表示が出て、最後にこんな感じで出る。

```
requested state: started
instances: 1/1
usage: 256M x 1 instances
urls: sample.paas.jp-e1.cloudn-service.com
zone:

     state     since                    cpu    memory          disk
#0   running   2014-07-20 01:34:48 AM   0.0%   25.1M of 256M   19.7M of 1G
```

で、上のurlに書かれているところにアクセスすれば、hello worldが見えるはず。（おしまい）


## 参考：ハマった点
最初にやったときに、デプロイ時に以下が出て詰まった。

```
0 of 1 instances running, 1 down
0 of 1 instances running, 1 down
0 of 1 instances running, 1 down
0 of 1 instances running, 1 down
0 of 1 instances running, 1 down
が繰り返し表示され、最後は
0 of 1 instances running, 1 failing
で落ちる。

ログを見ると
index"=>0, "reason"=>"CRASHED", "exit_status"=>-1,
となっている。
```

これは、ポイントと述べた
``process.env.VCAP_APP_HOST`` と ``process.env.VCAP_APP_HOST`` を
上手いこと設定できてなかったのが原因だった。(誤ってCloudFoundry v1の名前を使っていた)

## 参考：参考にしたリンク

- http://docs.cloudfoundry.org/buildpacks/node/node-tips.html
- http://docs.cloudfoundry.org/devguide/deploy-apps/troubleshoot-app-health.html
