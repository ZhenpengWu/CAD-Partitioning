import logging
import random

from model.circuit import Circuit
from util.constants import LEFT, RIGHT, NOT_SET
from util.result import write_result


class Partitioner:
    def __init__(self):
        self.best = -1
        self.result = []
        self.pruned = 0

    def partition(self, circuit: Circuit):
        """
        execute the branch and bound partitioning
        :param circuit:
        :return:
        """
        self.best, self.result = self.__random_partition(circuit)
        self.pruned = 0

        logging.info("random partition result = {}".format(self.best))

        n: int = circuit.get_cells_size()
        left_remain, right_remain = int(n / 2), n - int(n / 2)
        self.__partition(circuit, [NOT_SET] * n, 0, 0, left_remain, right_remain)

        write_result(circuit.benchmark, self.best, self.result)

        return self.best, self.result

    def __partition(
            self, circuit: Circuit, assigned, nid, label, left_reamin, right_remain
    ):
        """
        execute the recursive branch and bound partitioning
        :param circuit:
        :param assigned: the current assignment
        :param nid: the next cell
        :param label: the label of the current assignment
        :param left_reamin: the number of empty spaces remaining in the left
        :param right_remain: the number of empty space remaining in the right
        """
        if left_reamin == 0 and right_remain == 0:  # no node to assign
            if self.best < 0 or label < self.best:
                self.result = assigned.copy()
                self.best = label
            logging.info(
                "pruned: {:.6%} | label = {}, best = {} | LEAF".format(
                    self.__pruned_rate(circuit), label, self.best
                )
            )
        else:
            if self.best < 0 or label < self.best:
                if left_reamin > 0:  # add current cell into LEFT
                    new_label = label + self.__calculate_delta_label(
                        circuit, nid, assigned, LEFT
                    )
                    self.__partition(
                        circuit,
                        assigned,
                        nid + 1,
                        new_label,
                        left_reamin - 1,
                        right_remain,
                    )
                    assigned[nid] = NOT_SET
                else:
                    self.pruned += 1 << (right_remain - 1)

                if right_remain > 0:  # add current cell into RIGHT
                    new_label = label + self.__calculate_delta_label(
                        circuit, nid, assigned, RIGHT
                    )
                    self.__partition(
                        circuit,
                        assigned,
                        nid + 1,
                        new_label,
                        left_reamin,
                        right_remain - 1,
                    )
                    assigned[nid] = NOT_SET
                else:
                    self.pruned += 1 << (left_reamin - 1)
            else:
                self.pruned += 1 << (left_reamin + right_remain)

            logging.debug(
                "pruned: {:.6%} | label = {}, best = {}".format(
                    self.__pruned_rate(circuit), label, self.best
                )
            )

    def __pruned_rate(self, circuit):
        """
        :param circuit:
        :return: the pruned rate
        """
        return self.pruned / (1 << circuit.get_cells_size())

    @staticmethod
    def __calculate_delta_label(circuit: Circuit, nid, assigned, value):
        """
        :param circuit:
        :param nid: the cell id
        :param assigned: the current assignment
        :param value: LEFT / RIGHT
        :return: the label changes before and after assigning the cell into LEFT / RIGHT
        """
        cell = circuit.get_cell(nid)
        pre_label = cell.calculate_label(assigned)
        assigned[nid] = value  # add current cell into value
        post_label = cell.calculate_label(assigned)
        return post_label - pre_label

    @staticmethod
    def __random_partition(circuit: Circuit):
        """
        perfrom random partitioning on the given circuit
        :param circuit:
        :return: the best laebl and assignment
        """
        result = []
        best = -1
        n: int = circuit.get_cells_size()

        for _ in range(n):
            cids = random.sample(range(n), n)

            assigned = [NOT_SET] * n
            for i, v in enumerate(cids):
                assigned[v] = LEFT if i < int(n / 2) else RIGHT

            label = circuit.calculate_label(assigned)
            if best < 0 or label < best:
                best = label
                result = assigned

        return best, result
