---
layout: post
title: AnsibleとJenkinsを組み合わせた際にバッファなしで出力する方法
description: AnsibleとJenkinsを組み合わせた際にバッファなしで出力する方法
category: null
tags: []
ogp: /assets/images/ogp/2015-01-19-ansible-and-jenkins-with-no-buffer-output_ogp.png
---

JenkinsからAnsibleを叩いて、自動的にConfigurationする際に、
Jenkins側のコンソール（アウトプット）で、途中経過が表示されず
全てのタスクが終わった後にまとめて結果が表示されることがある。
これは、途中経過を見たいときには不便。

なんで表示されないかというと、Python側で標準出力のバッファが効いているため。
なので、バッファを無効にすればいいので、Ansibleの実行前に

```
export PYTHONUNBUFFERED=1
```

と、環境変数を定義してから実行すればOK。
