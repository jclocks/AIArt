import time
import PIL.Image
import PIL.ImageTk
from tkinter import *
from typing import Optional, Tuple
from watchdog.observers import Observer
from datetime import datetime, timedelta
from watchdog.events import FileSystemEventHandler, FileModifiedEvent


class Kiosk:
    """
    Kiosk GUI class displaying art on full-screen.

    Parameters
    ----------
    active_artwork_path : str
        Path to active artwork to be displayed. If the active artwork image is updated, the new image will be rendered.

    frame_path : Optional[str], default=None
        Path to frame image (.jpg or .png)

    frame_inner_size : Optional[Tuple[int, int]], default=None
        Inner size of frame. Used to resize artwork to fit frame. Only used if `frame_path` is not None.
    """
    def __init__(self,
                 active_artwork_path: str,
                 frame_path: Optional[str] = None,
                 frame_inner_size: Optional[Tuple[int, int]] = None) -> None:
        self.tk = Tk()
        self.tk.attributes('-zoomed', True)
        self.frame = Frame(self.tk)
        self.frame.pack()
        self.label = None
        self.fullscreen_state = True
        self.tk.attributes("-fullscreen", self.fullscreen_state)
        self.tk.bind("<F11>", self._toggle_fullscreen)
        self.tk.bind("<Escape>", self._end_fullscreen)

        self.active_artwork_path = active_artwork_path
        self.frame_path = frame_path
        self.frame_inner_size = frame_inner_size
        self.image_last_modified = datetime.now()

        self._start_image_event_handler()

    def _start_image_event_handler(self) -> None:
        """Starts watchdog event handler looking for modificaitons to the active artwork image."""
        event_handler = FileSystemEventHandler()
        event_handler.on_modified = self._on_updated_image
        observer = Observer()
        observer.schedule(event_handler, path='.', recursive=False)
        observer.start() 

    def _toggle_fullscreen(self, event: Event = None) -> str:
        """Toggle Tkinter fullscreen state"""
        self.fullscreen_state = not self.fullscreen_state
        self.tk.attributes("-fullscreen", self.fullscreen_state)
        return "break"

    def _end_fullscreen(self, event: Event = None) -> str:
        """End Tkinter fullscreen state"""
        self.fullscreen_state = False
        self.tk.attributes("-fullscreen", False)
        return "break"

    def _image_too_recently_modified(self) -> bool:
        """
        Check if active artwork image file was too recently modified.

        Returns
        -------
        bool
            If active artwork image file was to recentrly modified.
        """
        if datetime.now() - self.image_last_modified < timedelta(seconds=1):
            return True
        else:
            return False

    def _on_updated_image(self,
                          event: FileModifiedEvent) -> None:
        """
        Re-read active artwork image file and display file.

        Parameters
        ----------
        event : FileModifiedEvent
            Event body from watchdog event handler/observer.

        Return
        ------
        None
        """
        if self._image_too_recently_modified():
            return
        time.sleep(0.1)
        img = self._read_image(
            img_path=self.active_artwork_path,
            frame_path=self.frame_path,
            frame_inner_size=self.frame_inner_size
        )
        self.panel.configure(image=img)
        self.panel.image = img
        self.image_last_modified = datetime.now()

    @staticmethod
    def _add_frame_to_image(img: PIL.Image,
                            frame_path: str,
                            frame_inner_size: Tuple[int, int]) -> PIL.Image:
        """
        Add a frame (.jpg/.png) around image.

        Parameters
        ----------
        img : PIL.Image
            Artwork to add frame around.

        frame_path : str
            Path to frame image.

        frame_inner_size : Tuple[int, int]
            Inner size of frame. Used to resize artwork to fit frame.

        Returns
        -------
        PIL.Image
            Image with frame around.
        """
        frame_image = PIL.Image.open(frame_path)
        img = img.resize(
            size=frame_inner_size
        )
        img_start_point = (
            (frame_image.size[0]-img.size[0])//2,
            (frame_image.size[1]-img.size[1])//2
        )
        img_end_point = (
            img_start_point[0]+img.size[0],
            img_start_point[1]+img.size[1]
        )
        frame_image.paste(img, (*img_start_point, *img_end_point))
        return frame_image

    def _read_image(self, 
                    img_path: str,
                    frame_path: Optional[str] = None,
                    frame_inner_size: Optional[Tuple[int, int]] = None) -> PIL.ImageTk.PhotoImage:
        """
        Reads image to PIL ImageTk PhotoImage.

        Parameters
        ----------
        img_path : str
            Path to image.
        
        frame_path : Optional[str], default=None
            Path to image of frame.

        frame_inner_size : Optional[Tuple[int, int]], default=None
            (width, height), in pixels, of the inner rectangle of frame. Only used if `frame_path` is not None.

        Returns
        -------
        PIL.ImageTk.PhotoImage
            PIL ImageTk PhotoImage.
        """
        img = PIL.Image.open(img_path)
        if frame_path:
            img = self._add_frame_to_image(
                img=img,
                frame_path=frame_path,
                frame_inner_size=frame_inner_size
            )
        img = PIL.ImageTk.PhotoImage(img)
        return img

    def _setup_image_on_start(self) -> None:
        """Initially setting up and displaying the active artwork image."""
        img = self._read_image(
            img_path=self.active_artwork_path,
            frame_path=self.frame_path,
            frame_inner_size=self.frame_inner_size
        )
        self.panel = Label(self.tk, image=img)
        self.panel.image = img
        self.panel.pack()

    def start(self) -> None:
        """Starts infinite loop with a repeated check against how long it's been since the last art change. When long enough, it changes the active artwork."""
        while True:
            if (datetime.datetime.now() - self.time_last_image_change).seconds > self.seconds_before_artwork_change:
                self._change_active_artwork()
                self.time_last_image_change = datetime.datetime.now()      
