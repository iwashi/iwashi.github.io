---
layout: post
title: インストール jdk 1.7 and maven 3.0.5
description: インストール jdk 1.7 and maven 3.0.5
category: null
tags: []
ogp: /assets/images/ogp/2014-06-08-install-jdk-17-and-maven-305_ogp.png
---

CentOS6に、Java 1.7とMaven 3.0.5をインストールするときの手順メモ。
Chefへのレシピ化は別のポストで。

### Javaのインストール

```
// Javaのダウンロード
wget --no-check-certificate --no-cookies --header "Cookie: oraclelicense=accept-securebackup-cookie"  http://download.oracle.com/otn-pub/java/jdk/7u60-b19/jdk-7u60-linux-x64.rpm

// インストール
sudo rpm -ivh jdk-7u60-linux-x64.rpm\?AuthParam\=1402159184_93de8c9ec59bb33e6645d7796b140656

// 1.7が入っているのを確認
java -version

// JAVA_HOMEを設定
vi .bash_profile

//// 以下を追記
export JAVA_HOME=/usr/java/default

// 反映
source ~/.bash_profile

// 設定されているのを確認
echo $JAVA_HOME
```

### Mavenのインストール　

```
// ダウンロード
wget http://mirror.cc.columbia.edu/pub/software/apache/maven/maven-3/3.0.5/binaries/apache-maven-3.0.5-bin.tar.gz

// /usr/localに展開
sudo tar xzf apache-maven-3.0.5-bin.tar.gz  -C /usr/local

// シンボリックリンクを貼る	
cd /usr/local/
sudo ln -s apache-maven-3.0.5 maven

// MavenのPATHを設定
sudo vi /etc/profile.d/maven.sh

//// 以下を追記
export M2_HOME=/usr/local/maven
export PATH=${M2_HOME}/bin:${PATH}

// PATHが反映されているのを確認するために
// ログアウト＆ログオフをする。（例：sshの繋ぎ直しと）

// インストールを確認する
mvn -version
```

おしまい。