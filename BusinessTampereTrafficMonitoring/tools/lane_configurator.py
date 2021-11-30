import argparse
import json
import tkinter as tk

import geometry
from PIL import Image
from PIL import ImageTk

PTSIZE = 8
LINEWIDTH = 2
COLORS = ["#FF0000", "#FFFF00", "#FF00FF", "#00FFFF", "#00FF00"]


def read_args():
    parser = argparse.ArgumentParser(description="Tool to pick areas of interest (defined as polygons) from an image",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="Example usage:\n $ python lane_configurator.py image.jpg -L A -L B")

    parser.add_argument("image_file")

    parser.add_argument("-L", "--lane",
                        action="append",
                        help="Lanes to pick")

    parser.add_argument("--intersection-id",
                        default="UNKNOWN",
                        help="Intersection id (to be printed in JSON)")

    parser.add_argument("--camera-id",
                        default="UNKNOWN",
                        help="Camera id (to be printed in JSON)")

    parser.add_argument("--scale",
                        type=float,
                        default=1,
                        help="Factor to scale the image (coordinates will be translated to the original image size)")

    parser.add_argument("--round", action="store_true", help="Round the final coordinates to nearest integer")

    return vars(parser.parse_args())


def print_json(args, lanes, polygons):
    """
    prints the result of intersection, camera_id, lane, vertices as a json
    #Required arguments:
      args: Dictionary of arguments(Dict)
      lanes : List of lanes (List)
      polygons: List of polygons(List)
    """
    arr = []
    for i, lane in enumerate(lanes):
        obj = {}
        obj["intersection_id"] = args["intersection_id"]
        obj["camera_id"] = args["camera_id"]
        obj["lane"] = lane
        obj["vertices"] = polygons[i]
        arr.append(obj)
    print(json.dumps(arr))


def main():
    """
    Main function to work with the input image
    """
    args = read_args()
    lanes = args["lane"] or []
    scale = args["scale"] or 1
    lanes_given = len(lanes) > 0
    points = []
    polygons = []
    polygon_index = 0

    window = tk.Tk()
    window.title("Configurator 9001")

    img = Image.open(args["image_file"])
    imgw, imgh = img.size
    if args["scale"] != 1:
        img = img.resize((round(imgw * scale), round(imgh * scale)))
        imgw, imgh = img.size

    infotxt = tk.StringVar()

    def update_infotxt():
        """
        called from main method. Helps in selecting points in the input image
        """
        if lanes_given and polygon_index >= len(lanes):
            infotxt.set("All required lanes have been configured, you can close the window!")
        elif lanes_given:
            point_number = len(points) + 1
            lane = lanes[polygon_index]
            infotxt.set(f'Pick point #{point_number} for lane "{lane}", or right click to finish current polygon')
        else:
            infotxt.set("Pick points by left clicking the image, right click to finish a shape")

    update_infotxt()

    tk.Label(window, textvariable=infotxt).pack()

    tkimg = ImageTk.PhotoImage(img)

    canvas = tk.Canvas(window, width=imgw, height=imgh)
    canvas.create_image(0, 0, anchor=tk.NW, image=tkimg)
    canvas.pack()

    def onclick(event):
        """
        Onclick event triggered upon clicking on the image
        #Required arguments:
          event : event that triggers the onclick
        """
        x = event.x
        y = event.y
        points.append((x, y))
        color = COLORS[polygon_index % len(COLORS)]
        kwargs = {"fill": color}
        d = PTSIZE // 2
        canvas.create_oval(x - d, y - d, x + d, y + d, **kwargs)
        update_infotxt()

    def finish_polygon(event):
        """
        Method for creating a polygon on the input image to get the region of interest.
        #Required arguments:
          event : Event of button click
        """
        nonlocal polygon_index, points
        hull = geometry.convex_hull(points)
        kwargs = {"width": LINEWIDTH, "fill": COLORS[polygon_index % len(COLORS)]}
        for (x0, y0), (x1, y1) in zip(hull, hull[1:] + hull[0:1]):
            canvas.create_line(x0, y0, x1, y1, **kwargs)
        polygon_index += 1
        if args["round"]:
            polygons.append([(round(x / scale), round(y / scale)) for x, y in hull])
        else:
            polygons.append([(x / scale, y / scale) for x, y in hull])
        points = []
        update_infotxt()

    canvas.bind("<Button-1>", onclick)
    canvas.bind("<Button-3>", finish_polygon)

    window.mainloop()

    if lanes_given:
        print_json(args, lanes, polygons)
    else:
        for points in polygons:
            print(points)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
