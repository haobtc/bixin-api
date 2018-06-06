bixin-api django-app
--------------------

# 安装配置

## 创建Vendor 

去 https://bixin.im/openplatform/ 创建Vendor并获取币信
的 `vendor_name` 和 `secret`以及 `aes_key`

回调的URL可以稍后再填写

## 配置django-app

添加币信config到 `settings.py` 或者 `local_settings.py`

```
BIXIN_CONFIG = {
    'client': {
        'server_url': None,     # None is valid here
        'vendor_name': '',
        'secret': '',
        'aes_key': '',
    },
    'graphql_client': {
        'server_url': None,     # None is valid here
    }
}
```

然后在 `settings.py` 内启用币信应用

```
INSTALLED_APPS += [
    'bixin_api.contrib.django_app',
]
```

配置回调地址， 打开 `urls.py` , 在urlpatterns内添加

```
path('bixin/', include('bixin_api.contrib.django_app.urls'))
```

# 测试

```
make check
```

测试服务器和开放平台配置


callback 地址填 `http://your-hostname.com/bixin/events_callback/` 即可


# 开发约定

## 更新数据模型后

上线后需要一直track变更，每次数据更新的都需要生成migrations文件，
以便能使用django migration来维护线上数据结构的更新升级。

```
make make-migrations
```

将生成的文件提交到代码库内，并不要手工修改这些文件：）
