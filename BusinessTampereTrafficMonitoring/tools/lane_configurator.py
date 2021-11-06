import argparse
import json
import tkinter as tk

from PIL import Image
from PIL import ImageTk


PTSIZE = 8
LINEWIDTH = 2
COLORS = ["#FF0000", "#FFFF00", "#FF00FF", "#00FFFF", "#00FF00"]


def read_args():
    parser = argparse.ArgumentParser(description="Tool to pick areas of interest (defined by 4 points) from an image",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="Example usage:\n $ python lane_picker.py image.jpg -s A -s B -s C")

    parser.add_argument("image_file")

    parser.add_argument("-s", "--signal-group",
                        action="append",
                        help="Signal groups to pick")

    return vars(parser.parse_args())


def print_json(sgroups, points):
    arr = []
    for i, sgroup in enumerate(sgroups):
        obj = {}
        obj["intersection_id"] = "UNKNOWN"
        obj["camera_id"] = "UNKNOWN"
        obj["signal_group"] = sgroup
        obj["vertices"] = points[4*i:4*i+4]
        arr.append(obj)
    print(json.dumps(arr))


def main():
    args = read_args()
    sgroups = args["signal_group"]
    sgroups_given = len(sgroups) > 0
    points = []

    img = Image.open(args["image_file"])
    imgw, imgh = img.size

    window = tk.Tk()
    window.title("Configurator 9001")

    infotxt = tk.StringVar()

    def update_infotxt():
        if sgroups_given and len(points) >= 4 * len(sgroups):
            infotxt.set("All required points have been picked, you can close the window!")
        elif sgroups_given:
            point_number = len(points) % 4 + 1
            sg = sgroups[len(points) // 4]
            infotxt.set(f'Picking point {point_number}/4 for signal group "{sg}"...')
        else:
            infotxt.set("Pick points by clicking the image")

    update_infotxt()

    label = tk.Label(window, textvariable=infotxt)
    label.pack()

    tkimg = ImageTk.PhotoImage(img)

    canvas = tk.Canvas(window, width=imgw, height=imgh)
    canvas.create_image(0, 0, anchor=tk.NW, image=tkimg)
    canvas.pack()

    def onclick(event):
        points.append((event.x, event.y))
        d = PTSIZE // 2
        color_index = (len(points) - 1) // 4
        color = COLORS[color_index % len(COLORS)]
        kwargs = {"fill": color}
        canvas.create_oval(event.x - d, event.y - d, event.x + d, event.y + d, **kwargs)
        if len(points) % 4 == 0:
            kwargs = {"width": LINEWIDTH, "fill": color}
            canvas.create_line(*points[-1], *points[-2], **kwargs)
            canvas.create_line(*points[-1], *points[-3], **kwargs)
            canvas.create_line(*points[-1], *points[-4], **kwargs)
            canvas.create_line(*points[-2], *points[-3], **kwargs)
            canvas.create_line(*points[-2], *points[-4], **kwargs)
            canvas.create_line(*points[-3], *points[-4], **kwargs)
        update_infotxt()

    canvas.bind("<Button-1>", onclick)

    window.mainloop()

    if sgroups_given:
        print_json(sgroups, points)
    else:
        print(points)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
