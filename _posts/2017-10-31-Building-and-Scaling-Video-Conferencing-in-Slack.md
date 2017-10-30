---
layout: post
title: "Building and Scaling Video Conferencing in Slack 講演から取ったメモ"
description: "Building and Scaling Video Conferencing in Slack 講演から取ったメモ"
category: 
tags: []
---

本記事は、[Building and Scaling Video Conferencing in Slack](https://www.youtube.com/watch?v=VJj4ddWDTbs)から取ったメモです。かなり意訳気味にとってるので、何か間違いなどあれば [@iwashi86](https://twitter.com/iwashi86) までお願いします。

- Slackの良いところ
  - スクリーン共有越しに相手のユーザの画面をコントロールできる
  - Screenhero時代からのゴールだった
- Slackの開発チームは6人、だいたいどの時代でも
- クライアントアーキテクチャ
  - 最初は、自前カスタムのWebRTCのライブラリを使ってた
  - ただメンテがつらすぎて、Electron/Chromium に自然に含まれるほうに移行した
     - Electronのが自分でメンテするアップデートより早いし
- トポロジとしてはSFUを100%通る
  - だけど、1:1callが約90%あるので、考え直し中
- インフラ
  - AWSとGCP使ってる
  - SFUの配置場所を探すために、各リージョンにRegion serversというのを置いていて、そこでユーザをディスパッチしている
     - その際は、もっともLoad Averageが低いところを選んでる
  - この問題は、会議開始時点でどのSFUが適切かわからないという点
     - あとから15人入るかもしれない
     - 新アプリ・サーバのデプロイで台数が2倍必要になることもある
         - というのも、アップデートするときに会議が終わるのを待つのにだいたい24時間かかる（いわゆるdrain問題）
     - 選んだサーバがUSなのに会議参加者の大半がオーストラリアかもしれない
- なので未来の構成を考え中
  - 具体的にはSFUをカスケードする（マルチホストする）
     - これでユーザはSFUを選ばずに、どの最寄りのSFUに入っても良くなる
     - GCP/AWSのPrivateFiberを経由するから、UXめっちゃあがるかもね
- Enterpriseな顧客対応
  - UDPが通らない問題
  - だからTCPを通した。がそれでも通らない人がいる
  - なので、HA Proxy/443 を作った。これでTURN TLSを通した
- Janus対応
  - SFUは数年前からForkしたJanusを使ってる
  - Janusはプラグインモデルだがおかげで、PlanBやSimulcastを入れ込むのが難しい
  - 結果的に開発を続け、デバッグするのが大変になった
- 将来
  - elixirで書き直している
  - elrangの恩恵をうけられて、障害耐性がある。Processが死んでも、Supervisorが助けてくれる
  - ついでにhot codeリロードができる。インフラコストが安くなりそう
  - 重い処理（暗号化とか、アクティブ話者発見）はC++で書くつもり
