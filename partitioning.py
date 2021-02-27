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
        self.result, self.best = self.__random_partition(circuit)
        self.pruned = 0

        logging.info("random partition result = {}".format(self.best))

        n: int = circuit.get_cells_size()
        left_remain, right_remain = int(n / 2), n - int(n / 2)
        self.__partition(circuit, [NOT_SET] * n, 0, left_remain, right_remain)

        write_result(circuit.benchmark, self.best, self.result)

        return self.best, self.result

    @staticmethod
    def __random_partition(circuit: Circuit):
        best = -1
        result = []
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

        return result, best

    def __partition(self, circuit: Circuit, assigned, nid, left_reamin, right_remain):
        label = circuit.calculate_label(assigned)

        if left_reamin == 0 and right_remain == 0:  # no node to assign
            if self.best < 0 or label < self.best:
                self.result = assigned.copy()
                self.best = label
            logging.info(
                "LEAF | pruned: {:.6%} | label = {}, best = {}".format(
                    self.__pruned_rate(circuit), label, self.best
                )
            )
        else:
            if self.best < 0 or label < self.best:
                if left_reamin > 0:
                    assigned[nid] = LEFT  # add current cell into LEFT
                    self.__partition(
                        circuit, assigned, nid + 1, left_reamin - 1, right_remain
                    )
                    assigned[nid] = NOT_SET
                else:
                    self.pruned += 1 << (right_remain - 1)

                if right_remain > 0:
                    assigned[nid] = RIGHT  # add current cell into RIGHT
                    self.__partition(
                        circuit, assigned, nid + 1, left_reamin, right_remain - 1
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
        return self.pruned / (1 << circuit.get_cells_size())
