---
layout: post
title: 2016年の振り返りと2017年に向けて
description: 2016年の振り返りと2017年に向けて
category: null
tags: []
ogp: /assets/images/ogp/2016-12-31-2016retrospective_ogp.png
---

## 今年の振り返り

### 2016年 TL;DR;

上期(1-6月)には仕事に集中していた時期だった。特にインフラ系のコードを結構書いていて、HashiCorpツール類を色々と触っていた。また、インフラ上位のアプリ側のコードも書いていて、NodeJSをそれなりに書いた。イベント登壇もこの時期に多めにしていた。

下期(7-12月)は、プライベートを優先していた時期だった。諸事情で、フルタイムで仕事できなかった(昼休み前には終業してた)ので、開発をガッツリするというよりは、その周囲に落ちてる仕事をする感じだった。もちろん、夜以降に実施されることが多い、勉強会ものの登壇も0にした。その分、プライベートは充実していて、子供と遊んでいる時間が長かったのは最高だった。

#### 去年書いたことから

> コーディングする時間はある程度とれていたけど、全然足りないと考えている。 GitHub(GHE含む)の草の生えっぷりを見るとまだまだな感じ。 今年こそはJavaScriptを、と毎年思ってるけど、時間的＆優先度的＆役割的に仕事でやるのは辛そう。 コードは書くけど、JS以外のコードだろうなぁ。おそらく自動化系とか。 技術的には、クラウド系・自動化系を中心に手を動かしていく。

上期の時点で、上記引用部の内容はある程度達成できていた。インフラ系のコードも結構書けたし、JavaScriptも結構かけていた。

>  WebRTCで言えば、ものすごい書きかけの電子書籍も2016年は仕上げたい。

一生、WIPな感じがしてきた…。これは反省。内容減らして、出しちゃうのが良さそう。

#### 対外的なアウトプット

- 登壇したもの
  - 2016/2/19 [Developer Summmit 2016](http://event.shoeisha.jp/devsumi/20160218/)
  - 2016/5/17 [WebRTC Meetup Tokyo #10](https://atnd.org/events/76867)
  - 2016/6/2 [AWS Summit Tokyo](http://aws.amazon.com/jp/summit2016-report/)
  - 2016/8/8 [WebRTC Meetup Tokyo #11](https://atnd.org/events/79840)
  - その他、社内勉強会など

昨年よりも大幅に登壇数を意識的に減らしていた。登壇すると、準備にそれなりにリソースが取られるので、なるべく数を減らして、仕事とプライベートの時間優先にしていた。

- 書いた記事
  - [本Blogで11本](http://iwashi.co/)
  - [WebRTCHacks](https://webrtchacks.com/slack-webrtc-slacking/)
  - [社内ISUCON](http://qiita.com/iwashi86/items/97a7a97b59492cff181a)
  
WebRTC系の記事が多めで、特にSlackにおけるWebRTC利用を解説した記事がバズっていた。個人ブログで書いた記事2つをくっつけて、WebRTCHacksに記事を投稿できたのも良かった。

#### インプット

- 書籍数十冊 (主に会社Blogに書評を載せてる)
- PodCast
  - [Rebuild.fm](http://rebuild.fm/)
     - 週間少年ジャンプ的な感じでないとソワソワしちゃう
  - [omoiyari lean-agile podcast](http://lean-agile.fm/)
     - チーム開発についての悩みが非常に共感できる。Fearless Changeは名著。
  - [CloudInfra](https://cloudinfra.audio/)
     - クラウド、インフラ系のPodCastが生の声が聞けるのが非常に良い
  - [yatteiki.fm](https://yatteiki.fm/)
     - 特に、双剣問題のEPが共感できて最高だった

#### 2017年に向けて

上期は引き続き家族最優先でいこうと思う。1月は完全休業して、2月から徐々に再開していく。

自分のマネージャの受け売りだけど、「プライベートメインで、残った体力・気力で仕事をする」という感じでいきたい。といっても、仕事をすると体力・気力が回復することも多いので、個人的には仕事とプライベートは相互補完的なものがあると考えてる。

プライベートで残った時間で、以下のあたりに取り組みたい/使っていきたい。

- 技術的なこと
  - WebRTC: 技術的な知識、ノウハウをアウトプット
  - Golang/Swift(iOS)/Java(Android)
  - GCP/Azure
  - SaaS
     - Travis CI / Circle CI
     - ReadTheDocs
