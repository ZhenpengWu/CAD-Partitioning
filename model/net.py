from typing import List

from model.cell import Cell
from util.constants import NOT_SET


class Net:
    def __init__(self, nid, color) -> None:
        self.net_id = nid
        self.__cells: List[Cell] = []
        self.color = color

    def add_cell(self, cell: Cell) -> None:
        self.__cells.append(cell)

    def get_source(self) -> Cell:
        """
        :return: the source, which is the first cell in the cells
        """
        return self.__cells[0]

    def get_sinks(self) -> List[Cell]:
        """
        :return: the sinks, which are the cell except the first one
        """
        return self.__cells[1:]

    def calculate_label(self, assigned) -> int:
        if assigned[self.get_source().nid] == NOT_SET:
            return 0
        for sink in self.get_sinks():
            if (
                    assigned[sink.nid] != NOT_SET
                    and assigned[self.get_source().nid] != assigned[sink.nid]
            ):
                return 1
        return 0
