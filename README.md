<div align="center" markdown>
<img src="https://i.imgur.com/VsSAl4b.jpg" height="450px"/>



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

**OVIS** (short for **O**ccluded **V**ideo **I**nstance **S**egmentation) is a large scale benchmark dataset for video instance segmentation task. It is designed with the philosophy of perceiving object occlusions in videos, which could reveal the complexity and the diversity of real-world scenes.

**OVIS consist of:**

- 296k high-quality instance masks
- 25 commonly seen semantic categories
- 901 videos with severe object occlusions
- 5,223 unique instances

Given a video, all the objects belonging to the pre-defined category set are exhaustively annotated. All the videos are annotated per 5 frames.

The 25 semantic categories in OVIS are *Person, Bird, Cat, Dog, Horse, Sheep, Cow, Elephant, Bear, Zebra, Giraffe, Poultry, Giant panda, Lizard, Parrot, Monkey, Rabbit, Tiger, Fish, Turtle, Bicycle, Motorcycle, Airplane, Boat*, and *Vehicle*.

<img src="http://songbai.site/ovis/data/webp/2524877_0_170.webp"/>

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

Annotations file must contain `annotations` in its name. The images archive must have a name that matches the line in the annotation file name after the `_` and before the extension(like `annotations_train.json` and `train.zip`). If you do not comply with these conditions import will crash.

## How To Run 

**Step 1**: Add app to your team from [Ecosystem](https://ecosystem.supervise.ly/apps/import-ovis-format) if it is not there.

**Step 2**: Go to `Current Team`->`Files` page, right-click on your `.tar` archive or `folder`, containing `ovis` data and choose `Run App`->`Import Ovis`. You will be redirected to `Workspace`->`Tasks` page. 

<img src="https://i.imgur.com/dJr5sLz.png"/>



## How to use

Resulting project will be placed to your current `Workspace` with the same name as the `ovis` archive. Videos in datasets will have tags (`train`, `val`, `test`) corresponding to input data.

<img src="https://i.imgur.com/UC0ygAH.png"/>

You can also access your project by clicking on it's name from `Tasks` page.

<img src="https://i.imgur.com/h54uGur.png">