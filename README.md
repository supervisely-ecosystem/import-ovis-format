<div align="center" markdown>
<img src="https://i.imgur.com/fO42F3p.jpg"/>




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

**[OVIS](http://songbai.site/ovis/)** (short for **O**ccluded **V**ideo **I**nstance **S**egmentation) is a large scale benchmark dataset for video instance segmentation task. It is designed with the philosophy of perceiving object occlusions in videos, which could reveal the complexity and the diversity of real-world scenes.

**OVIS public date consist of:**

- 296k high-quality instance masks
- 25 commonly seen semantic categories
- 901 videos with severe object occlusions
- 5,223 unique instances

Given a video, all the objects belonging to the pre-defined category set are exhaustively annotated. All the videos are annotated per 5 frames.

The 25 semantic categories in OVIS are *Person, Bird, Cat, Dog, Horse, Sheep, Cow, Elephant, Bear, Zebra, Giraffe, Poultry, Giant panda, Lizard, Parrot, Monkey, Rabbit, Tiger, Fish, Turtle, Bicycle, Motorcycle, Airplane, Boat*, and *Vehicle*.

<img src="http://songbai.site/ovis/data/webp/2524877_0_170.webp"/><img src="http://songbai.site/ovis/data/webp/2932104.webp"/><img src="http://songbai.site/ovis/data/webp/3383476.webp"/><img src="http://songbai.site/ovis/data/webp/3021160.webp"/>



## Get access to data

Click `Dataset Download` in [OVIS](http://songbai.site/ovis/)  main page. 

<img src="https://i.imgur.com/kM6yQMv.png" width="600"/>

Register in opened form.

Click `participate` tab and choose `Google Drive` link. 

<img src="https://i.imgur.com/3rxQhpX.png" width="900"/>

You will be redirected to Google Drive with data in OVIS format. Load data you need to use in your work.

<img src="https://i.imgur.com/OVSVyZS.png" width="900"/>

Now, you can import loaded data to [Supervisely](https://supervise.ly/).

## Preparation

Upload your data in `OVIS` format to `Team Files` (for example you can create `import_ovis` folder). You can also upload data from `.tar` archive.

<img src="https://i.imgur.com/45uOaK0.png"/>

#### Structure of archive or directory have to be the following:   
```
 .                                   .                             
 └── ovis_data                       └── ovis_data.zip
     ├── train.zip                           |   
     │   ├── 0b4b662c                        ├── train.zip             
     |   |	├── img_0000001.jpg              │   ├── 0b4b662c          
     |   |	├── img_0000002.jpg              |   |	├── img_0000001.jpg
     |   |	├── ...                          |   |	├── img_0000002.jpg
     │   ├── 2f477d05                        |   |	├── ...            
     |   |	├── img_0000001.jpg              │   ├── 2f477d05          
     |   |	├── img_0000002.jpg              |   |	├── img_0000001.jpg
     |   |	├── ...                          |   |	├── img_0000002.jpg
     │   └── ...                             |   |	├── ...            
     │                                       │   └── ...               
     └── annotations_train.json              │                         
                                             └── annotations_train.json

```

#### Note:

Annotations file must contain `annotations` in its name. The images archive must have a name that matches the line in the annotation file name after the `_` and before the extension(like `annotations_train.json` and `train.zip`). If you do not comply with these conditions import will crash.

## How To Run 

**Step 1**: Add app to your team from [Ecosystem](https://ecosystem.supervise.ly/apps/import-ovis-format) if it is not there.

**Step 2**: Go to `Current Team`->`Files` page, right-click on your `.tar` archive or `folder`, containing `ovis` data and choose `Run App`->`Import Ovis`. You will be redirected to `Workspace`->`Tasks` page. 

<img src="https://i.imgur.com/dJr5sLz.png"/>



## How to use

Resulting project will be placed to your current `Workspace` with the same name as the `ovis` data directory or archive. Videos in datasets will have tags (`train`, `val`, `test`) corresponding to input data.

<img src="https://i.imgur.com/UC0ygAH.png"/>

You can also access your project by clicking on it's name from `Tasks` page.

<img src="https://i.imgur.com/v3aEGAE.png">