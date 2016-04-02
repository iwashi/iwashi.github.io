---
layout: post
title: "CloudnとVagrantを組み合わせて使う方法"
description: "CloudnでVagrantを利用する方法"
category: 
tags: []
---

[Cloudn](http://www.ntt.com/cloudn/)とVagrantを組み合わせて使えると非常に便利なのだけど、
ググったところ、既存事例が見つからなかった。なのでやってみた。

Cloudnは[CloudStack](http://cloudstack.apache.org/)ベースであり、
[vagrant-cloudstack](https://github.com/klarna/vagrant-cloudstack) みたいなVagrant Pluginもあり、
やればできるはず。で、結果的にvagrantからインスタンス作成・削除出来たので、
この記事では方法について解説する。

本記事に沿うと、以下のvagrantコマンドをCloudnを対象として実行できるようになる。

```
$ vagrant up --provider=cloudstack
$ vagrant ssh
$ vagrant destroy
```

こんな感じ。(cloudnって文字は出てきてないけど、cloudnに対して実行してる)

![cloudnとvagrantの実行イメージ](/assets/images/20140624sc.jpg)

<script async src="//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
<!-- iwashico_middle -->
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-4737755123993145"
     data-ad-slot="6593095118"
     data-ad-format="auto"></ins>
<script>
(adsbygoogle = window.adsbygoogle || []).push({});
</script>

## 全体の流れ
いくつか下準備等もあるので、はじめに全体の流れを書いて、後から詳説する。

1. 前提
2. Vagrant用のテンプレートの作成
3. Vagrantfileの作成
4. Vagrantからインスタンス起動・プロビジョニング・削除

-----

## 1. 前提
今回はMac OS(10.9.3)上で実施しており、Vagrant周りのバージョンは以下のとおり：

```
$ vagrant -v
Vagrant 1.5.4

$ vagrant plugin install vagrant-cloudstack

# vagrant plugin list
vagrant-cloudstack (0.7.0)
```

------

## 2. Vagrant用のテンプレートの作成
Cloudnでは、Vagrant用のオフィシャルテンプレートを用意していない。
そのため、自分で作成する必要がある。

今回は、Cloudnのオフィシャルテンプレートである CentOS 6.3 64-bit を利用して、
Vagrant用のオリジナルテンプレートを作成する。

Vagrantのオフィシャルテンプレートは以下の点を満たす必要がある:

- vagrantというログインユーザがいること
- vagrantユーザは、パスワード無しでsudoできること、
- sshのrequirettyが無効になっていること
- 公開鍵認証でsshログインできること(vagrantユーザの.sshにauthorized_keyを設定)

以下でそのテンプレートを作成する。

### 2-1. Cloudnでインスタンスを作成
CloudnのDashboard上からインスタンスを作成する。
今回は、Compute FLATを選択しており、最小限のスペックで作成している。

作成時には、セキュリティグループも設定しておく。
このセキュリティグループは、作業環境からつながるように設定しておくこと。
例えば、自身のグローバルIPが1.2.3.4なら、1.2.3.4/32を送信元として許可するような設定にする。

### 2-2. ssh接続して準備
作成したインスタンスへ接続する。
初回接続時は、Cloudnの画面上で、インスタンス作成時に出るパスワードを使う。
以下は、ssh接続した後のコマンド。

```
// rootユーザのパスワードを変更
# passwd
// rootのpasswordはvagrantにする

// vagrantユーザの作成
# useradd vagrant
# passwd vagrant
// passwordはvagrantでOK

// selinuxの無効化（任意。必要ないことが多いのでやっておく）
# vi /etc/sysconfig/selinux
# setenforce 0

// 元のmacアドレスを記憶しないように設定
# cd /etc/udev/rules.d/
# mv 70-persistent-net.rules .70-persistent-net.rules
# ln -s /dev/null /etc/udev/rules.d/70-persistent-net.rules

// sudoをPW無しで出来るように
# visudo
// 以下を追記
vagrant         ALL=(ALL)       NOPASSWD: ALL
// requirettyを無効化するために、以下のようにrequirettyをコメントアウト
#Defaults    requiretty

// IPからの逆引きを無効化(接続が早くなるように)
# vi /etc/ssh/sshd_config
// 以下を追記
UseDNS no

// sshの設定を反映
# service sshd reload

// vagrantユーザへ
# su vagrant

// 鍵の準備
$ mkdir .ssh
$ cd .ssh/

// vagrant用の公開鍵をダウンロード。自分で作った公開鍵でもOKだが、サボった。
$ wget http://github.com/mitchellh/vagrant/raw/master/keys/vagrant.pub --no-check-certificate

// 落とした公開鍵をssh用へリネーム
$ mv vagrant.pub authorized_keys

// パーミッションの修正
$ chmod 600 authorized_keys
$ chmod 700 .ssh/
```

これから、テンプレートを作成する作業になるので、
その他で入れたいパッケージがあれば入れておくと良い。

### 2-3. Cloudnでオリジナルテンプレートの作成
上記でカスタマイズしたインスタンスをテンプレート化する。
テンプレート化するには、インスタンスを止めるかスナップショットが必要。
今回はインスタンスを停止してから行った。

作業手順自体はマニュアル通りで、マウスでポチポチしてくだけなので省略。
ちなみに今回は、 CentOS6.3_vagrant というテンプレート名で作成した。

-----

## 3. Vagrantfileの作成
VagrantのキモであるVagrantfileを作成したいが、
そこにはCloudnの情報を色々と埋め込む必要がある。
Cloudnの情報は、Web上のコンソールからも色々と確認できるが、Webだと必要な情報がすべて確認できない？ようなので、
[Cloudmonkey](https://pypi.python.org/pypi/cloudmonkey/)を入れてCUIから見る。

ちなみに、同様のことが出来る公式ツールとして、[cloudn-cli](http://info.cloudn-service.com/document/cli/)もあるので、
こっちを使ってもいいと思う。

### 3-1. Cloudmonkeyのインストールと設定
インストールは`pip install cloudmonkey`だけ。
その後configファイルを編集する。

以下で埋め込んでいるsecretkeyとAPIキーは、Cloudnのポータル画面から確認できる。
また、hostとpathは http://info.cloudn-service.com/document/cli/ のページ中央にあるものを利用した。なので今回は東日本リージョン。

```
$ cat ~/.cloudmonkey/config

[user]
secretkey = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
apikey = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

[server]
protocol = https
expires = 600
host = comp-api.jp-e1.cloudn-service.com
timeout = 3600
path = /client/api
port = 443
```

### 3-2. 必要な情報を見る
Vagrantfileに必要な情報をガシガシ抽出していく。
cloudmonkeyはtabで補完が聞くので、とりあえずlistの後にtabを押して
以下の本家マニュアルのパラメータを参考にしながらコマンド打てばOK。

cloudn本家のAPIマニュアルは [ココ](http://info.cloudn-service.com/wordpress/wp-content/uploads/documents/JP/ejp/compute_ejp_api_manual.pdf)を参照。

```
$ cloudmonkey

// 1-3で作成したテンプレートIDを確認する
> list templates templatefilter=self

// securitygroupidを確認する。keywordは手順1-1でインスタンス作成した際に設定したsecuritygroupを使う。
> list securitygroups keyword=vagrant

// zone idの確認
> list zones

// Serviceofferingid(microとかのインスタンスのプラン)を確認
> list serviceofferings
```

~~あとnetworkidも知りたいのだが、これはコマンドライン上から確認する方法を見つけられなかったので、Web上のコンソールから実施した。~~
(2014/7/4追記：Twitterで指摘いただきましたが、network_idは不要でした）

具体的には、コンソール画面の「ネットワーク - ゲスト ネットワーク - defaultGuestNetwork」から確認した。
デフォルトだと3つ見えるので、ゾーン名等を見ながら選ぶとnetworkidが見える。

### 3-3. Vagrantfileを作る
以下のVagrantファイルのXXXXやYYYYの項目を埋める。

```
# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "dummy"
  config.ssh.private_key_path = "~/.vagrant.d/insecure_private_key"

  config.vm.provider :cloudstack do |cloudstack, override|
    cloudstack.host = "comp-api.jp-e1.cloudn-service.com"
    cloudstack.path = "/client/api"
    cloudstack.port = "443"
    cloudstack.scheme = "https"
    cloudstack.api_key = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    cloudstack.secret_key = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

#    cloudstack.network_id = "YYYYYYYYYYYYYYYYYYYYYYYYYYYYY" ### 不要でした
    cloudstack.template_id = "YYYYYYYYYYYYYYYYYYYYYYYYYYYYY"
    cloudstack.service_offering_id = "YYYYYYYYYYYYYYYYYYYYYYYYYYY"
    cloudstack.zone_id = "YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY"
    cloudstack.security_group_ids = ['YYYYYYYYYYYYYYYYYYYYYYYYYYYY'] # 複数設定してもOK
    cloudstack.network_type = "Basic"
  end

  # Provisionまで出来るか確認
  config.vm.provision :shell do |s|
    s.inline = <<-EOS
    touch provision.txt
    EOS
  end

end
```

-----

## 4. Vagrantからインスタンス起動・プロビジョニング・削除
長かったけど最後の仕上げ。

以下のコマンドでインスタンスを立ち上げ、ssh接続、破棄を試す。
それぞれ、それなりに時間がかかるので気長に待つ。

```
$ vagrant up --provider=cloudstack
$ vagrant ssh
$ vagrant destroy
```

おしまい。

-----

### おまけ
将来的にCompute VPC (OpenNW)もやってみたけど、
これは、vagrant-cloudstackが対応してない？いつやるかわからないけど、要調査。

### 参考
色々と参考にさせていただいたサイト：

- https://github.com/klarna/vagrant-cloudstack
- http://www.slideshare.net/star76/20130627-9cloudn-23600250
- http://buta9999.hatenablog.jp/entry/2014/01/21/160539
- http://blog.udcp.net/2012/12/02/cloudmonkey/
- http://nushu123.blogspot.jp/2013/12/vagrant-cloudstack.html
- http://www.idcf.jp/blog/etc/vagrant-cloudstack/
