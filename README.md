<div align="center" markdown>
<img src="https://i.imgur.com/48JFbtt.png" width="1900px"/>


# Import OVIS

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#Preparation">Preparation</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#How-To-Use">How To Use</a>
</p>


[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/import-ovis-format)
[![views](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-ovis-format&counter=views&label=views)](https://supervise.ly)
[![used by teams](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-ovis-format&counter=downloads&label=used%20by%20teams)](https://supervise.ly)
[![runs](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-ovis-format&counter=runs&label=runs&123)](https://supervise.ly)

</div>

## Overview

Import data in [OVIS](http://songbai.site/ovis/) format to [Supervisely](https://supervise.ly/) from folder or `tar` archive.

## Preparation

Upload your data in `OVIS` format to `Team Files` (for example you can create `import_ovis` folder). You can also upload data from `.tar` archive.

<img src="https://i.imgur.com/45uOaK0.png"/>

#### Structure of directory or archive have to be the following:   
```
.
├── train.zip
│   ├── 0b4b662c
|   |	├── img_0000001.jpg
|   |	├── img_0000002.jpg
|   |	├── ...
│   ├── 2f477d05
|   |	├── img_0000001.jpg
|   |	├── img_0000002.jpg
|   |	├── ...
│   └── ...
│    
└── annotations_train.json
```

#### Note:

If you will drag and drop archive with parent directory instead of its content, import will crash.

Annotations file must contain `annotations` in its name. The images archive must have a name that matches the line in the annotation file name after the `_` and before the extension. If you do not comply with these conditions import will crash.

## How To Run 

**Step 1**: Add app to your team from [Ecosystem](https://ecosystem.supervise.ly/apps/import-cityscapes) if it is not there.

**Step 2**: Go to `Current Team`->`Files` page, right-click on your `.tar` archive or `folder`, containing `ovis` data and choose `Run App`->`Import Ovis`. You will be redirected to `Workspace`->`Tasks` page. 

<img src="https://i.imgur.com/dJr5sLz.png"/>

**Step 3**: Select slider value to split images in `train` folders with `train` and `val` tags.

<img src="https://i.imgur.com/vXWYwhR.png" width="600px"/>



## How to use

Resulting project will be placed to your current `Workspace` with the same name as the `ovis` archive. Videos in datasets will have tags (`train`, `val`) corresponding to the ratio, exposed in the slider.

<img src="https://i.imgur.com/UC0ygAH.png"/>

You can also access your project by clicking on it's name from `Tasks` page.

<img src="https://i.imgur.com/h54uGur.png">