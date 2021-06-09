import os, random
import zipfile, json, tarfile
import supervisely_lib as sly
import glob
from supervisely_lib.io.fs import download, file_exists, get_file_name, get_file_name_with_ext
from supervisely_lib.imaging.color import generate_rgb
from pathlib import Path
import shutil
from supervisely_lib.geometry.bitmap import Bitmap
import numpy as np
import cv2
import pycocotools._mask as _mask
from collections import defaultdict
from supervisely_lib.video_annotation.key_id_map import KeyIdMap


my_app = sly.AppService()
TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])
INPUT_DIR = os.environ.get("modal.state.slyFolder")
PROJECT_NAME = 'OVIS'
IMAGE_EXT = '.png'
logger = sly.logger
train_tag = 'train'
val_tag = 'val'
archive_ext = '.zip'
frame_rate = 10
video_ext = '.mp4'


def decode(rleObjs):
    if type(rleObjs) == list:
        return _mask.decode(rleObjs)
    else:
        return _mask.decode([rleObjs])[:,:,0]


@my_app.callback("import_ovis")
@sly.timeit
def import_ovis(api: sly.Api, task_id, context, state, app_logger):

    storage_dir = my_app.data_dir

    cur_files_path = INPUT_DIR
    extract_dir = os.path.join(storage_dir, str(Path(cur_files_path).parent).lstrip("/"))
    input_dir = os.path.join(extract_dir, Path(cur_files_path).name)
    archive_path = os.path.join(storage_dir, cur_files_path.split("/")[-2] + ".tar")
    project_name = Path(cur_files_path).name

    #api.file.download(TEAM_ID, cur_files_path, archive_path)

    #if tarfile.is_tarfile(archive_path):
    #    with tarfile.open(archive_path) as archive:
    #        archive.extractall(extract_dir)
    #else:
    #    raise Exception("No such file".format(INPUT_FILE))

    ovis_data = os.listdir(input_dir)

    search_anns = os.path.join(input_dir, "annotations_*.json")
    anns_fine_paths = glob.glob(search_anns)
    anns_fine_paths.sort()

    ovis_classes = {}
    id_to_obj_classes = {}

    for ann_path in anns_fine_paths:
        ann_name = str(Path(ann_path).name)
        arch_name = sly.fs.get_file_name(ann_name).split('_')[1] + archive_ext
        arch_path = os.path.join(input_dir, arch_name)
        if not sly.fs.file_exists(arch_path):
            logger.warn('There is no archive {} in the input data, but it must be'.format(arch_name))
            continue

        # try:
        #    shutil.unpack_archive(arch_path, input_dir)
        # except Exception('Unknown archive format {}'.format(arch_name)):
        #    my_app.stop()

        imgs_dir_path = os.path.join(input_dir, sly.fs.get_file_name(arch_name))
        images_dirs = os.listdir(imgs_dir_path)
        ann_json = sly.json.load_json_file(ann_path)

        videos = ann_json['videos']
        ovis_anns = ann_json['annotations']


        for category in ann_json['categories']:
            if category['id'] not in ovis_classes.keys():
                ovis_classes[category['id']] = category['name']
                id_to_obj_classes[category['id']] = sly.ObjClass(category['name'], sly.Bitmap)
            else:
                if ovis_classes[category['id']] != category['name']:  #TODO test it!!!
                    logger.warn('Category with id {} corresponds to the value {}, not {}. Check your input annotations'.format(category['id'], ovis_classes[category['id']], category['name']))


        anns = defaultdict(list)
        for ovis_ann in ovis_anns:
            anns[ovis_ann['video_id']].append([ovis_ann['category_id'], ovis_ann['id'], ovis_ann['segmentations']])

        for video_data in videos:

            curr_anns = anns[video_data['id']]
            video_objects = {}
            for curr_ann in curr_anns:
                video_objects[curr_ann[1]] = sly.VideoObject(id_to_obj_classes[curr_ann[0]])

            frames = []
            for idx in range(500):
                figures = []
                for curr_ann in curr_anns:
                    ovis_geom = curr_ann[2][idx]
                    if ovis_geom:
                        mask = decode(ovis_geom).astype(bool)
                        geom = sly.Bitmap(mask)
                        figure = sly.VideoFigure(video_objects[curr_ann[1]], geom, idx)
                        figures.append(figure)
                new_frame = sly.Frame(idx, figures)
                frames.append(new_frame)



            a=0


            #=============================create video===============================================================
            img_size = (video_data['width'], video_data['height'])
            video_folder = video_data['file_names'][0].split('/')[0]
            video_name = video_folder + video_ext
            images_path = os.path.join(imgs_dir_path, video_folder)
            if not sly.fs.dir_exists(images_path):
                logger.warn('There is no folder {} in the input data, but it is in annotation'.format(images_path))
                continue
            images = os.listdir(images_path)
            progress = sly.Progress('Create video and figures for frame', len(images), app_logger)
            video_path = os.path.join(extract_dir, video_name)
            video = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'MP4V'), frame_rate, img_size)
            for curr_ovis_im_path in video_data['file_names']:
                curr_im_path = os.path.join(imgs_dir_path, curr_ovis_im_path)
                if not sly.fs.file_exists(curr_im_path):
                    logger.warn('There is no image {} in {} folder, but it must be. Video will be skipped.'.format(
                        curr_ovis_im_path.split('/')[1], video_name))
                    break  #TODO no image how to continue
                video.write(cv2.imread(curr_im_path))
                progress.iter_done_report()
            video.release()
            # =======================================================================================================





        rle = ovis_anns[0]['segmentations'][0]
        mask = decode(rle)


    #try:
    #    shutil.unpack_archive(archive_path, storage_dir)
    #except Exception('Unknown archive format {}'.format(project_name)):
    #    my_app.stop()

    new_project = api.project.create(WORKSPACE_ID, project_name, change_name_if_conflict=True)

    tags_template = os.path.join(input_dir, "gtFine", "*")
    tags_paths = glob.glob(tags_template)
    tags = [os.path.basename(tag_path) for tag_path in tags_paths]

    if train_tag in tags and val_tag not in tags:
        split_train = True
    else:
        split_train = False

    search_fine = os.path.join(input_dir, "gtFine", "*", "*", "*_gt*_polygons.json")
    files_fine = glob.glob(search_fine)
    files_fine.sort()

    search_imgs = os.path.join(input_dir, "leftImg8bit", "*", "*", "*_leftImg8bit" + IMAGE_EXT)
    files_imgs = glob.glob(search_imgs)
    files_imgs.sort()

    if len(files_fine) == 0 or len(files_imgs) == 0:
        raise Exception('Input cityscapes format not correct')

    samples_count = len(files_fine)
    progress = sly.Progress(('Importing images'), samples_count)

    images_pathes_for_compare = []
    images_pathes = {}
    images_names = {}
    anns_data = {}
    ds_name_to_id = {}
    for orig_ann_path in files_fine:
        parent_dir, json_filename = os.path.split(os.path.abspath(orig_ann_path))

        dataset_name = os.path.basename(parent_dir)
        if dataset_name not in dataset_names:
            dataset_names.append(dataset_name)
            ds = api.dataset.create(new_project.id, dataset_name, change_name_if_conflict=True)
            ds_name_to_id[dataset_name] = ds.id
            images_pathes[dataset_name] = []
            images_names[dataset_name] = []
            anns_data[dataset_name] = []

        orig_img_path = json_path_to_image_path(orig_ann_path)
        images_pathes_for_compare.append(orig_img_path)
        if not file_exists(orig_img_path):
            logger.warn('Image for annotation {} not found is dataset {}'.format(orig_ann_path.split('/')[-1], dataset_name))
            continue
        images_pathes[dataset_name].append(orig_img_path)
        images_names[dataset_name].append(sly.io.fs.get_file_name_with_ext(orig_img_path))

        tag_path = os.path.split(parent_dir)[0]
        train_val_tag = os.path.basename(tag_path)

        if train_val_tag == train_tag and split_train is True:
            if random.random() < samplePercent:
                train_val_tag = val_tag
            else:
                train_val_tag = train_tag

        tag_meta = sly.TagMeta(train_val_tag, sly.TagValueType.NONE)
        if not tag_metas.has_key(tag_meta.name):
            tag_metas = tag_metas.add(tag_meta)
        tag = sly.Tag(tag_meta)

        json_data = json.load(open(orig_ann_path))
        ann = sly.Annotation.from_img_path(orig_img_path)

        for obj in json_data['objects']:
            class_name = obj['label']
            if class_name == 'out of roi':
                polygon = obj['polygon'][:5]
                interiors = [obj['polygon'][5:]]
            else:
                polygon = obj['polygon']
                if len(polygon) < 3:
                    logger.warn('Polygon must contain at least 3 points in ann {}, obj_class {}'.format(orig_ann_path, class_name))
                    continue
                interiors = []

            interiors = [convert_points(interior) for interior in interiors]
            polygon = sly.Polygon(convert_points(polygon), interiors)
            if city_classes_to_colors.get(class_name, None):
                obj_class = sly.ObjClass(name=class_name, geometry_type=sly.Polygon, color=city_classes_to_colors[class_name])
            else:
                new_color = generate_rgb(city_colors)
                city_colors.append(new_color)
                obj_class = sly.ObjClass(name=class_name, geometry_type=sly.Polygon, color=new_color)
            ann = ann.add_label(sly.Label(polygon, obj_class))
            if not obj_classes.has_key(class_name):
                obj_classes = obj_classes.add(obj_class)

        ann = ann.add_tag(tag)
        anns_data[dataset_name].append(ann)

        progress.iter_done_report()

    out_meta = sly.ProjectMeta(obj_classes=obj_classes, tag_metas=tag_metas)
    api.project.update_meta(new_project.id, out_meta.to_json())

    for ds_name, ds_id in ds_name_to_id.items():
        dst_image_infos = api.image.upload_paths(ds_id, images_names[ds_name], images_pathes[ds_name])
        dst_image_ids = [img_info.id for img_info in dst_image_infos]
        api.annotation.upload_anns(dst_image_ids, anns_data[ds_name])

    stat_dct = {'samples': samples_count, 'src_ann_cnt': len(files_fine), 'src_img_cnt': len(files_imgs)}

    logger.info('Found img/ann pairs.', extra=stat_dct)

    images_without_anns = set(files_imgs) - set(images_pathes_for_compare)
    if len(images_without_anns) > 0:
        logger.warn('Found source images without corresponding annotations:')
        for im_path in images_without_anns:
            logger.warn('Annotation not found {}'.format(im_path))

    logger.info('Found classes.', extra={'cnt': len(obj_classes),
                                             'classes': sorted([obj_class.name for obj_class in obj_classes])})
    logger.info('Created tags.', extra={'cnt': len(out_meta.tag_metas),
                                            'tags': sorted([tag_meta.name for tag_meta in out_meta.tag_metas])})

    my_app.stop()


def main():
    sly.logger.info("Script arguments", extra={
        "TEAM_ID": TEAM_ID,
        "WORKSPACE_ID": WORKSPACE_ID
    })
    my_app.run(initial_events=[{"command": "import_ovis"}])

if __name__ == '__main__':
    sly.main_wrapper("main", main)

