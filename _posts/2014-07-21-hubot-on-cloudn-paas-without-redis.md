---
layout: post
title: HubotをCloudn PaaS v2で動かす (CloudFoundryも対応)
description: HubotをCloudn PaaS v2で動かす (CloudFoundryも対応)　なお、PaaSの仕様上でRedis抜きになる。
category: null
tags: []
ogp: /assets/images/ogp/2014-07-21-hubot-on-cloudn-paas-without-redis_ogp.png
---

HipChatやSlack等のチャットサービスにHubotを参加させて、
様々な作業を代行すると非常に便利。

Hubotを自前サーバを建ててやる手段もあるが、ちょっと面倒なので、
PaaSに載せちゃおう。有名どころだと海外のherokuだけど、国産のCloudnでもやりたい、ってことでやってみた。

今回はSlackを対象としてやるけど、HipChatもやり方は一緒。
あと、Cloudn PaaSはCloudFoundryベースなので、他のCloudFoundryにも使い回しが効くはず。

## 全体の流れ
まず全体の流れを紹介する。

1. 前提、注意点
2. Hubotの準備
3. デプロイ
4. Cloudnへ環境変数を登録
5. Slackの設定変更

-----

## 1. 前提、注意点
- 今回の対象チャットサービスはSlack向けであり、Slack側のインテグレーションは事前に作っておくこと。特にTOKENとTEAM名は忘れずにとっておくこと。

```
HUBOT_SLACK_TOKEN=AAAAAAAAAAAAAAAAAAAAAAAAAAA
HUBOT_SLACK_TEAM=your team name
```

- またSlack側にHubot URLを設定する必要があるが、これはこの時点では空でOK。
- Cloudn PaaS v2はRedisをサポートしてないので、Hubot(Redis無し)にする
- gudコマンドラインツールを先に入れておくこと。（前回の記事を参照）

## 2. Hubotの準備
まずhubotをgithubから落として、インストール。
すでにhubotが入っている人はかっ飛ばしてOK。

```
$ git clone git://github.com/github/hubot.git
$ cd hubot
$ npm install
```

hubotが入ったらhubotコマンドでひな形作成。
以下の -c の後は、好きな名前でOK。
slackのアダプタも入れる。

```
$ hubot -c ibot
$ cd ibot
$ npm install hubot-slack save
```

次に設定を変える。

```
$ vim Procfile  で、以下に変更する
web: bin/hubot -a slack
```
これで、hubot起動時(デプロイ時)にslackアダプタを使うようになる。

最後に、hubotはデフォルトでRedisを使うのでRedisを使う部分を削除する。
具体的にはhubot-scripts.jsonを以下のとおり編集すればOK。

```
$ vim hubot-scripts.json
["shipit.coffee"]
```

なお、これによりRedisを使わないのでHubotは起動する毎に、
すべてを忘れるようになる。もしCloudnで使いたければ
Redistogoのような別のSaaS型Redisを使うか、自前のIaaSで準備する必要がある。

## 3. デプロイ
ここまで出来たので、Cloudn PaaSへデプロイする。

```
$ gud push sample 
```

いろいろとデプロイで出力があるが、変なエラーがなきゃOK。

## 4. Cloudnへ環境変数を登録
今回デプロイしたアプリが使う環境変数を設定する。
これは、Slackのインテグレーションページで設定したものを参考に。

```
$ gud se sample HUBOT_SLACK_TOKEN AAAAAAAAAAAAAAAAAAAAAAAAA // 適宜変えてください
$ gud se sample HUBOT_SLACK_TEAM teamname  // 適宜変えてください
$ gud se sample HUBOT_SLACK_BOTNAME ibot   // 適宜変えてください
```

## 5. Slackの設定変更
だれかが発言したときに、SlackからCloudn PaaS上のHubotに発言が飛ぶので、
この飛び先URIを、Slackに設定しておかないといけない。

ウェブページからも探せるけど、コマンドのが早いので以下を実行。

```
$ gud app sample

/// 略
urls: sample.paas.jp-e1.cloudn-service.com
/// 略

```

このurlをSlackのインテグレーションのページで、Hubot URLに設定してあげる。
あとは、Slack上で

```
ibot ping
> ibot PONG
```

と、返事がある。あとはご自由に！（おしまい）
