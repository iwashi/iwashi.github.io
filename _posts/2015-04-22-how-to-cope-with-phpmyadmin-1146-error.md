---
layout: post
title: 'phpMyAdminで #1146 Error が出ている場合の対応方法'
description: how to cope with phpMyAdmin 1146 error
category: null
tags: []
ogp: /assets/images/ogp/2015-04-22-how-to-cope-with-phpmyadmin-1146-error_ogp.png
---

phpMyAdminで

```
#1146 – Table ‘phpmyadmin.pma_recent’ doesn’t exist
```

がエラーが出てしまって、正常に確認したDBが見れないことがある。
これは、phpMyAdmin管理用のDBへ接続できてないケースで出る。
ちなみに、エラーに書いてあるpmaってPhpMyAdminのacronymだ。

具体的には、phpMyAdminから覗いたDBの履歴とかを保存しているみたいなだけど、
今回の自身のユースケースでは、そもそもphpMyAdmin用にデータベースはいらず、
外部のDBの内容を確認したいだけだったので、該当機能を外す。

```
$ vim /etc/phpmyadmin/config.inc.php

/**
    $cfg['Servers'][$i]['pmadb'] = $dbname;
    $cfg['Servers'][$i]['bookmarktable'] = 'pma_bookmark';
    $cfg['Servers'][$i]['relation'] = 'pma_relation';
    $cfg['Servers'][$i]['table_info'] = 'pma_table_info';
    $cfg['Servers'][$i]['table_coords'] = 'pma_table_coords';
    $cfg['Servers'][$i]['pdf_pages'] = 'pma_pdf_pages';
    $cfg['Servers'][$i]['column_info'] = 'pma_column_info';
    $cfg['Servers'][$i]['history'] = 'pma_history';
    $cfg['Servers'][$i]['table_uiprefs'] = 'pma_table_uiprefs';
    $cfg['Servers'][$i]['designer_coords'] = 'pma_designer_coords';
    $cfg['Servers'][$i]['tracking'] = 'pma_tracking';
    $cfg['Servers'][$i]['userconfig'] = 'pma_userconfig';
    $cfg['Servers'][$i]['recent'] = 'pma_recent';
*/
```

な感じで、コメントアウトしちゃえばOK。
