import os
import sys
import time
import random

class ArtCronJob:
    """

    Parameters
    ----------

    active_artwork_file_path : str
        Path to the active artwork file. This is the image that will be displayed in the Kiosk.

    image_directory : str
        Path to the image directory from where the images will be randomly sampled.

    loop_sleep_sec : float, default=1.0
        Seconds to sleep after registered button click. Risk of multiple unexpected simultaneous clicks
        if set to low.
    """
    def __init__(self,
                 active_artwork_file_path: str,
                 image_directory: str,
                 loop_sleep_sec: float = 1.0) -> None:
        try:

        except Exception as e:
            print(e.message)
            sys.exit(1)

        if ('.jpg' in active_artwork_file_path) and (os.path.isfile(active_artwork_file_path)):
            self.active_artwork_file_path = active_artwork_file_path
        else:
            raise ValueError('Active arwork file is not a .jpg or does not exist.')
        if os.path.isdir(image_directory):
            self.image_directory = image_directory

        self.loop_sleep_sec = loop_sleep_sec

    def _get_random_image_path(self) -> str:
        """
        Randomly samples a path to an image in the image directory.

        Returns
        -------
        str
            Randomly sampled path to an image.
        """
        image_names = [image_name for image_name in os.listdir(self.image_directory) if '.jpg' in image_name]
        image_name = random.choice(image_names)

        image_path = os.path.join(self.image_directory, image_name)
        return image_path

    def _change_active_artwork(self) -> None:
        """Replaces the currently active artwork image file with a randomly sampled image file from the image directory"""
        image_path = self._get_random_image_path()
        os.rename(
            src=image_path,
            dst=self.active_artwork_file_path
        )

    def start(self) -> None:
       """Starts infinite loop that monitors how long it's been since the last change, changes image if exceeds time setting."""
        self.seconds_before_artwork_change = 3600
        while True:
            if (datetime.datetime.now() - self.time_last_image_change).seconds > self.seconds_before_artwork_change:
                self._change_active_artwork()
                self.time_last_image_change = datetime.datetime.now()
