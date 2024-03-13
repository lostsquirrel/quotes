# quotes
以YAML格式整理名言名句，经典语录等，通过 CI 自动构建为 `json` 格式发布

## 使用

1. 直接使用发布的 `json` 文件
2. 以 api 形式提供数据访问

## 数据模板

```yaml
- author:
    name:
      zh:
      en:
  quotes:
    - tags: []
      zh:
      en:
    - tags: []
      zh:
      en:
```

## 功能计划

- [x] 名言警句通过 [api](https://tool.shangao.tech/api/v1/quotes) 随机返回
- [ ] 名言警句通过 api 标签返回
- [ ] 名言警句通过 api 标签加关键字固定对应关系返回
- [ ] 名言警句根据请求语言国际化