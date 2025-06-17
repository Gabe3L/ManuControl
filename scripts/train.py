import os
import json
import shutil
import logging

import roboflow
from ultralytics import YOLO

################################################################


class ModelTrainer:
    def __init__(self):
        roboflow.login()
        self.config = self.get_config()
        self.workspace = self.get_roboflow_workspace(self.config)

    def get_config(self):
        logging.info("Loading Config.")

        with open("admin/roboflow_creds.json", "r") as f:
            config = json.load(f)

        return config

    def get_roboflow_workspace(self, config):
        logging.info("Accessing Roboflow")
        rf = roboflow.Roboflow()
        return rf.workspace(config["workspace"]).project(config["project"]).version(config["version"])

    def get_dataset(self):
        logging.info("Downloading Dataset")

        return self.workspace.project.download(
            self.config["model_type"],
            location="video_ai/datasets"
        )

    def delete_dataset(self, dataset):
        dataset_path = dataset.location
        if os.path.exists(dataset_path):
            shutil.rmtree(dataset_path)
            logging.info(f"Dataset at '{dataset_path}' deleted.")
        else:
            logging.warning(f"Dataset path '{dataset_path}' not found.")

    def train(self, dataset):
        try:
            logging.info("Beginning Training.")
            model = YOLO("video_ai/yolo11n.pt").to("cuda")
            model.train(
                data=os.path.join(dataset.location, "data.yaml"),
                project="video_ai",
                device="cuda",
                batch=60,
                imgsz=640,
                epochs=100,
                workers=8,
                nms=True,
                iou=0.6,
                amp=True,
                half=True
            )

            logging.info("Exporting model...")
            model.export(format="onnx", half=True, device="cuda")
            model.export(format="engine", half=True, device="cuda")
        except Exception as e:
            logging.error(e)

################################################################


def main():
    trainer = ModelTrainer()
    dataset = trainer.get_dataset()
    trainer.train(dataset)
    trainer.delete_dataset(dataset)


#################################################################################################

if __name__ == "__main__":
    main()
