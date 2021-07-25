# 音频合成、识别、切割

## 目录结构

- audio_subtitle // 剪映接口获取字幕核心逻辑代码
- edit // 音频编辑逻辑代码
- config.yaml // 配置文件
- audio_factory.py // 执行文件

## 使用说明

```
cd ..../module
python audio_factory.py -i ./example_audio -w ./example_workspace
```

## 输出目录说明

- workspace
    - cut //音频简介
    - jointed //合成的音频文件，包含json，切分之后的文本
    - 

## 剪映音频字幕获取脚本（经测试，请求头参数可以重复使用）

建议使用脚本前，先运行一次剪映识别字幕功能，抓取每个URL的请求头参数并配置在config.json文件中

## URL抓包工具

Proxifier + Fiddler

### 需要获取签名的URL：

- https://lv-pc-api.ulikecam.com/lv/v1/upload_sign
- https://lv-pc-api.ulikecam.com/lv/v1/audio_subtitle/submit
- https://lv-pc-api.ulikecam.com/lv/v1/audio_subtitle/query

### 需要获取请求头参数

- device-time
- tdid
- sign