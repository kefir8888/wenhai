# -*- coding: utf-8 -*-
from modalities.skeleton_modalities import  Skeleton_3D
from modalities.modality import GetPoints, Modality

from pose_estimation.draw import Plotter3d, draw_poses

import numpy as np
import common
import cv2

import sys
sys.path.append("../robotics_course/")

from modules.input_output import Source

class Video_source(Modality, Source):
    def __init__ (self, path_, type_ = "images_source", logger_ = 0):
        Modality.__init__ (self, logger_)
        Source.__init__ (self, path_, type_)

    def _read_data (self):
        self.read_data = self.get_frame ()

    def _process_data (self):
        self.processed_data = self.read_data

    def _interpret_data (self):
        self.interpreted_data = self.processed_data

    def get_read_data (self):
        return self.read_data

class Video (GetPoints):
    def __init__ (self, video_path_ = "", model_path_ = "", mode_ = "GPU", base_height_ = 512, logger_ = 0, focal_length = 3.67):
        GetPoints.__init__(self, logger_, model_path_, mode_, base_height_, focal_length)
        self.skel_3d = Skeleton_3D(logger_ = self.logger)
        self.poses_3d         = []
        self.canvas_3d = np.zeros((720, 1280, 3), dtype=np.uint8)
        self.plotter = Plotter3d(self.canvas_3d.shape[:2])
        self.canvas_3d_window_name = 'Video Skeleton 3D'
        self.video_path = video_path_

        if (self.video_path == ""):
            # self.all_data = cv2.VideoCapture("/home/kompaso/Desktop/sit.mp4")
            self.all_data = cv2.VideoCapture(0)#self.available_cameras[-1]) #/home/kompaso/Desktop/hand_high.mp4

        else:
            self.all_data = cv2.VideoCapture (self.video_path)

        self.read = False

    def name(self):
        return "video"

    def _read_data (self):
        if (self.read == False):
            _, img = self.all_data.read()
            self.img = img
        # edges = []
        self.read_data, self.poses_3d, edges = self._infer_net (self.img) #draww(self.img)
        self.plotter.plot(self.canvas_3d, self.poses_3d, edges)
        # print("VIDEO", self.poses_3d)
        # cv2.imshow(canvas_3d_window_name, canvas_3d)

    def _process_data(self):
        if sum (self.read_data) != -36 and self.read_data != []:
            self.skel_3d.read_data = self.poses_3d
            self.skel_3d._process_data()
            self.processed_data = self.skel_3d.processed_data
            # print("Video", self.processed_data)
            # self.processed_data = self.skel_3d.processed_data


    def _interpret_data(self):
        self.interpreted_data = self.processed_data

    def _get_command(self):
        commands = []

        if (self.timeout.timeout_passed ()):
            for key in self.processed_data.keys():
                commands.append(("/set_joint_angle", [key, str(self.processed_data[key])]))

            print ("app joints", commands)

        else:
            commands.append (("noaction", [""]))

        # print ("COMMANDS: ", commands)
        return commands

    def get_command(self, skip_reading_data=False):
        if (skip_reading_data == False):
            self._read_data()

        self._process_data()
        self._interpret_data()
        #print("МЯК", self._get_command())
        return self._get_command()

    def draw(self, img):
        return [self.canvas_3d, self.frame]
