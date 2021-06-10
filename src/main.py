import os, random
import zipfile, json, tarfile
import supervisely_lib as sly
import glob
from supervisely_lib.io.fs import get_file_name, get_file_name_with_ext
from pathlib import Path
import shutil
import cv2
import pycocotools._mask as _mask
from collections import defaultdict
from supervisely_lib.video_annotation.video_tag import VideoTag
from supervisely_lib.video_annotation.video_tag_collection import VideoTagCollection


my_app = sly.AppService()
TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])
INPUT_DIR = os.environ.get("modal.state.slyFolder")
INPUT_FILE = os.environ.get("modal.state.slyFile")
samplePercent = int(os.environ['modal.state.samplePercent']) / 100
PROJECT_NAME = 'OVIS'
logger = sly.logger
archive_ext = '.zip'
frame_rate = 5
video_ext = '.mp4'
train_tag = 'train'
val_tag = 'val'


def decode(rleObjs):
    if type(rleObjs) == list:
        return _mask.decode(rleObjs)
    else:
        return _mask.decode([rleObjs])[:,:,0]


@my_app.callback("import_ovis")
@sly.timeit
def import_ovis(api: sly.Api, task_id, context, state, app_logger):

    storage_dir = my_app.data_dir

    if INPUT_DIR:
        cur_files_path = INPUT_DIR
        extract_dir = os.path.join(storage_dir, str(Path(cur_files_path).parent).lstrip("/"))
        input_dir = os.path.join(extract_dir, Path(cur_files_path).name)
        archive_path = os.path.join(storage_dir, cur_files_path.split("/")[-2] + ".tar")
        project_name = Path(cur_files_path).name
    else:
        cur_files_path = INPUT_FILE
        extract_dir = os.path.join(storage_dir, get_file_name(cur_files_path))
        archive_path = os.path.join(storage_dir, get_file_name_with_ext(cur_files_path))
        project_name = get_file_name(INPUT_FILE)
        input_dir = extract_dir

    api.file.download(TEAM_ID, cur_files_path, archive_path)

    if tarfile.is_tarfile(archive_path):
        with tarfile.open(archive_path) as archive:
            archive.extractall(extract_dir)
    else:
        raise Exception("No such file".format(INPUT_FILE))

    search_anns = os.path.join(input_dir, "annotations_*.json")
    anns_fine_paths = glob.glob(search_anns)
    if len(anns_fine_paths) == 0:
        logger.warn('There is no annotations in input data. Check your input format')
    anns_fine_paths.sort()

    ovis_classes = {}
    id_to_obj_classes = {}

    new_project = api.project.create(WORKSPACE_ID, project_name, type=sly.ProjectType.VIDEOS,
                                     change_name_if_conflict=True)

    tag_meta_train = sly.TagMeta(train_tag, sly.TagValueType.NONE)
    tag_meta_val = sly.TagMeta(val_tag, sly.TagValueType.NONE)
    tag_collection = sly.TagMetaCollection([tag_meta_train, tag_meta_val])
    meta = sly.ProjectMeta(tag_metas=tag_collection)
    api.project.update_meta(new_project.id, meta.to_json())

    for ann_path in anns_fine_paths:
        ann_name = str(Path(ann_path).name)
        arch_name = sly.fs.get_file_name(ann_name).split('_')[1] + archive_ext
        arch_path = os.path.join(input_dir, arch_name)
        if not sly.fs.file_exists(arch_path):
            logger.warn('There is no archive {} in the input data, but it must be'.format(arch_name))
            continue

        #shutil.unpack_archive(arch_path, input_dir)
        if zipfile.is_zipfile(archive_path):
            with zipfile.ZipFile(archive_path, 'r') as archive:
                archive.extractall(input_dir)
        else:
            raise Exception("No such file".format(INPUT_FILE))

        imgs_dir_path = os.path.join(input_dir, sly.fs.get_file_name(arch_name))
        ann_json = sly.json.load_json_file(ann_path)

        videos = ann_json['videos']
        ovis_anns = ann_json['annotations']
        if not ovis_anns:
            logger.warn('There is no annotations data in {}'.format(ann_name))
            continue

        for category in ann_json['categories']:
            if category['id'] not in ovis_classes.keys():
                ovis_classes[category['id']] = category['name']
                id_to_obj_classes[category['id']] = sly.ObjClass(category['name'], sly.Bitmap)
            else:
                if ovis_classes[category['id']] != category['name']:
                    logger.warn(
                        'Category with id {} corresponds to the value {}, not {}. Check your input annotations'.format(
                            category['id'], ovis_classes[category['id']], category['name']))

        new_dataset = api.dataset.create(new_project.id, sly.fs.get_file_name(ann_name), change_name_if_conflict=True)
        new_meta = sly.ProjectMeta(sly.ObjClassCollection(list(id_to_obj_classes.values())))
        meta = meta.merge(new_meta)
        api.project.update_meta(new_project.id, meta.to_json())

        anns = defaultdict(list)
        for ovis_ann in ovis_anns:
            anns[ovis_ann['video_id']].append([ovis_ann['category_id'], ovis_ann['id'], ovis_ann['segmentations']])

        for video_data in videos:
            no_image = False
            curr_anns = anns[video_data['id']]
            video_objects = {}
            for curr_ann in curr_anns:
                video_objects[curr_ann[1]] = sly.VideoObject(id_to_obj_classes[curr_ann[0]])

            #=============================create video===============================================================
            img_size = (video_data['width'], video_data['height'])
            video_folder = video_data['file_names'][0].split('/')[0]
            video_name = video_folder + video_ext
            images_path = os.path.join(imgs_dir_path, video_folder)
            if not sly.fs.dir_exists(images_path):
                #logger.warn('There is no folder {} in the input data, but it is in annotation'.format(images_path))
                continue
            images = os.listdir(images_path)
            progress = sly.Progress('Create video', len(videos), app_logger)
            video_path = os.path.join(extract_dir, video_name)
            video = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'MP4V'), frame_rate, img_size)
            for curr_ovis_im_path in video_data['file_names']:
                curr_im_path = os.path.join(imgs_dir_path, curr_ovis_im_path)
                if not sly.fs.file_exists(curr_im_path):
                    logger.warn('There is no image {} in {} folder, but it must be. Video will be skipped.'.format(
                        curr_ovis_im_path.split('/')[1], video_name))
                    no_image = True
                    break
                video.write(cv2.imread(curr_im_path))
            if no_image:
                continue
            progress.iter_done_report()
            video.release()
            # =======================================================================================================
            frames = []
            for idx in range(len(images)):
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

            file_info = api.video.upload_paths(new_dataset.id, [video_name], [video_path])
            new_frames_collection = sly.FrameCollection(frames)
            new_objects = sly.VideoObjectCollection(list(video_objects.values()))
            if random.random() < samplePercent:
                tag = VideoTag(tag_meta_val)
            else:
                tag = VideoTag(tag_meta_train)
            tag_collection = VideoTagCollection([tag])
            ann = sly.VideoAnnotation((img_size[1], img_size[0]), len(frames), objects=new_objects,
                                      frames=new_frames_collection, tags=tag_collection)
            logger.info('Create annotation for video {}'.format(video_name))
            api.video.annotation.append(file_info[0].id, ann)

    my_app.stop()


def main():
    sly.logger.info("Script arguments", extra={
        "TEAM_ID": TEAM_ID,
        "WORKSPACE_ID": WORKSPACE_ID
    })
    my_app.run(initial_events=[{"command": "import_ovis"}])


if __name__ == '__main__':
    sly.main_wrapper("main", main)

