import logging
import os.path
import tkinter.font as tk_font
from math import sqrt, ceil
from tkinter import ALL, Canvas, StringVar, Tk, E, N, S, W, filedialog, DISABLED, NORMAL
from tkinter.ttk import Button, Frame, Label

from model.circuit import Circuit
from model.constants import LEFT, RIGHT, LEFT_COLOR, RIGHT_COLOR
from partitioning import Partitioner
from util.logging import init_logging
from util.output import read


def count(assigned):
    left, right = 0, 0
    for num in assigned:
        if num == LEFT:
            left += 1
        elif num == RIGHT:
            right += 1
    return left, right


class App:
    def __init__(self, args=None) -> None:
        init_logging(args.verbose)

        self.circuit = Circuit()
        self.partitioner = Partitioner()

        # if no_gui and infile are set, test benchmark directly without gui
        if args.no_gui and args.infile:
            self.__test_benchmark(args.infile)
        elif args.all:  # if all is set, test all benchmarks without gui
            for file in os.scandir("benchmarks"):
                self.__test_benchmark(file)
        else:  # otherwise, display GUI
            self.root = Tk()
            self.__init_gui()
            if args.infile:
                self.__load_benchmark(args.infile)
            if args.infile and args.render:
                self.__render_result(args.render)
            self.root.mainloop()

    def __render_result(self, file):
        cost, assignment = read(file)
        self.__update_canvas(assignment)
        self.__update_cost(cost)

    def __test_benchmark(self, file):
        logging.info("opened benchmark: {}".format(file))
        self.circuit.parse_file(file)

        self.partitioner.partition(self.circuit)

    def __open_benchmark(self):
        """
        called when "open" button is pressed, a dialog is opened for the user
        if a file is selected, load the file and initialize the canvas
        """
        filename = filedialog.askopenfilename(
            initialdir="benchmarks",
            title="Select file",
            filetypes=[("Text files", "*.txt"), ("all files", "*.*")],
        )

        if not filename:
            return

        self.__load_benchmark(filename)

        self.root.nametowidget("btm.partition")["state"] = NORMAL

    def __load_benchmark(self, filename):
        """
        load the input file, initialize the canvas, update related info in the info frame
        :param filename: the input file
        """

        logging.info("opened benchmark: {}".format(filename))
        self.circuit.parse_file(filename)

        self.__update_info("info.benchmark", self.circuit.benchmark)
        self.__update_info("info.cells", self.circuit.get_cells_size())
        self.__update_info("info.nets", self.circuit.get_nets_size())

    def __partitioning(self):
        cost, assignment = self.partitioner.partition(self.circuit)
        self.__update_canvas(assignment)
        self.__update_cost(cost)

        self.root.nametowidget("btm.partition")["state"] = DISABLED

    def __init_gui(self):
        """
        initialize the GUI
        """
        self.root.title("partitioning")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(4, weight=1)

        # set up the canvas / top frame
        top_frame = Frame(self.root, name="top")
        top_frame.grid(column=1, row=0, sticky=E + W + N + S)

        # add canvas to the top frame
        canvas = Canvas(top_frame, width=500, height=400, bg="gray66", name="canvas")
        canvas.grid(column=0, row=0, sticky=E + W + N + S)

        # set up the bottom / button frame
        btm_frame = Frame(self.root, name="btm")
        btm_frame.grid(column=1, row=1)

        # add open button to the bottom frame
        open_button = Button(
            btm_frame, text="open", command=self.__open_benchmark, name="open"
        )
        open_button.grid(column=0, row=0, padx=5, pady=5)

        # add partition button to the bottom frame
        partition_button = Button(
            btm_frame,
            text="partition",
            command=self.__partitioning,
            name="partition",
        )
        partition_button.grid(column=2, row=0, padx=5, pady=5)
        partition_button["state"] = DISABLED

        # set up the info frame
        info_frame = Frame(self.root, name="info")
        info_frame.grid(column=2, row=0, rowspan=2, sticky=E + W)

        # add informations to the info frame
        font = tk_font.Font(family="Helvetica", size=13)
        for i, v in enumerate(["benchmark", "cells", "nets", "cost"]):
            fg = "red" if v == "cost" else "black"
            label = Label(info_frame, font=font, foreground=fg, text=v + ":")
            label.grid(column=0, row=i, padx=5, pady=5, sticky=W)
            val = StringVar(info_frame, value="-")
            val_label = Label(
                info_frame, font=font, foreground=fg, textvariable=val, name=v
            )
            val_label.grid(column=1, row=i, padx=5, pady=5)

    def __update_canvas(self, assignment):
        """
        initialize the canvas, with the given circuit
        """
        canvas = self.root.nametowidget("top.canvas")

        # clear the canvas
        canvas.delete(ALL)

        left, right = count(assignment)

        left_cols, right_cols = ceil(sqrt(left)), ceil(sqrt(right))
        left_rows, right_rows = ceil(left / left_cols), ceil(right / right_cols)
        rows, cols = max(left_rows, right_rows), left_cols + right_cols

        w_size = self.root.winfo_screenwidth() * 0.8 / (cols + 3)
        h_size = self.root.winfo_screenheight() * 0.8 / rows
        # calculate the size of cells in the canvas, depends on the number of rows and cols
        size = int(min(w_size, h_size))

        offset_x, offset_y = size // 2, size // 2

        canvas_width = (cols + 1) * size + 2 * offset_x
        canvas_height = rows * size + (rows - 1) * 0.5 * size + 2 * offset_y
        canvas.config(width=canvas_width, height=canvas_height)

        left_offset_x, right_offset_x = size // 2, size // 2 + (left_cols + 1) * size,

        left_index, rihgt_index = 0, 0
        for i, val in enumerate(assignment):
            if val == LEFT:  # left
                self.__update_cell(i, left_index, left_cols, size, left_offset_x, offset_y, LEFT_COLOR)
                left_index += 1
            else:  # right
                self.__update_cell(i, rihgt_index, right_cols, size, right_offset_x, offset_y, RIGHT_COLOR)
                rihgt_index += 1

        self.__update_nets()

    def __update_cell(self, sid, i, cols, size, offset_x, offset_y, color):
        canvas = self.root.nametowidget("top.canvas")

        cell = self.circuit.get_cell(sid)
        cell.x, cell.y = i % cols, int(i / cols)
        x1, y1 = offset_x + cell.x * size, cell.y * size * 1.5 + offset_y
        x2, y2 = x1 + size, y1 + size
        cell.rect_id = canvas.create_rectangle(x1, y1, x2, y2, fill=color)
        cell.set_text(canvas)

    def __update_nets(self):
        canvas = self.root.nametowidget("top.canvas")

        canvas.delete("netlist")

        for i in range(self.circuit.get_nets_size()):
            net = self.circuit.get_net(i)
            source = net.get_source()
            x1, y1 = source.center_coords(canvas)
            for sink in net.get_sinks():
                x2, y2 = sink.center_coords(canvas)
                canvas.create_line(x1, y1, x2, y2, fill=net.color, tags="netlist", width=1.5)

    def __update_cost(self, cost):
        self.__update_info("info.cost", cost)

    def __update_info(self, name: str, val):
        num_cells = self.root.nametowidget(name)
        varname = num_cells.cget("textvariable")
        num_cells.setvar(varname, val)
