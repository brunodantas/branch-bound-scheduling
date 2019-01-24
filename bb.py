import re
import random
from collections import namedtuple
from subprocess import call

# adjacency list contains successors & predecessors
Vertex = namedtuple("Vertex", "id cost successors predecessors")
Edge = namedtuple("Edge", "vertex cost")
Solution = namedtuple("Solution", "sequence processors makespan")


class BB:
    def __init__(self, file_graph, processor_qty):
        # graph filename & # of processors
        self.file_graph = file_graph
        self.processor_qty = processor_qty
        self.get_graph()
        self.best_makespan = sum(self.graph[i].cost for i in range(self.task_qty))  # serial heuristic
        self.best_solution = None
        self.total_evaluations = 0

    def get_graph(self):
        # makes graph representation from file
        self.task_qty = int(re.search("\d+", self.file_graph).group(0))
        with open(self.file_graph) as f:
            lines = f.readlines()

        self.graph = [Vertex(v, int(lines[v]), [], [])
                      for v in range(self.task_qty)]

        for l in lines[self.task_qty + 1:]:
            a, b, cost = [int(x) for x in l.split()]
            e1 = Edge(self.graph[b], cost)
            e2 = Edge(self.graph[a], cost)
            self.graph[a].successors.append(e1)
            self.graph[b].predecessors.append(e2)

    def search(self):
        # generates optimal solution

        # solution with "root" vertex only
        procs = [0] * self.task_qty
        s = Solution([0], procs, self.graph[0].cost)
        available_tasks = []
        remaining_tasks = list(range(1,self.task_qty))
        predecessors_left = [len(v.predecessors) for v in self.graph]
        task = self.graph[0]
        for e in task.successors:
            t = e.vertex
            predecessors_left[t.id] -= 1
            if predecessors_left[t.id] == 0:
                available_tasks.append(t.id)
        self.branch(s, available_tasks[:], remaining_tasks[:], predecessors_left)

    def branch(self, partial_sol, available_tasks, remaining_tasks, predecessors_left):
        if remaining_tasks == []:
            self.total_evaluations += 1
            if partial_sol.makespan < self.best_makespan:
                self.best_makespan = partial_sol.makespan
                self.best_solution = partial_sol

        # print(partial_sol, available_tasks, remaining_tasks, predecessors_left)
        branches = []
        for t in available_tasks:
            seq = partial_sol.sequence + [t]
            task = self.graph[t]
            available_tasks2 = available_tasks[:]
            available_tasks2.remove(t)
            remaining_tasks2 = remaining_tasks[:]
            remaining_tasks2.remove(t)
            predecessors_left2 = predecessors_left[:]
            for e in task.successors:
                child = e.vertex
                predecessors_left2[child.id] -= 1
                if predecessors_left2[child.id] == 0:
                    available_tasks2.append(child.id)

            h = sum(self.graph[t].cost for t in remaining_tasks2) // self.processor_qty
            for p in range(self.processor_qty):
                procs = partial_sol.processors[:]
                procs[t] = p
                sol = self.evaluate(Solution(seq, procs, 0))
                g = sol.makespan + h
                # print(g)
                branches.append((g, sol, available_tasks2, remaining_tasks2, predecessors_left2))

        branches.sort(key = lambda x: x[0])
            # print(branches)
        for b in branches:
            if b[0] < self.best_makespan:
                _, sol, av, rem, pre = b
                self.branch(sol, av, rem, pre)


    def evaluate(self, ind):
        # assigns fitness (makespan)
        self.total_evaluations += 1
        timestamps = [0] * self.task_qty
        total_time = [0] * self.processor_qty

        for t in ind.sequence:
            task = self.graph[t]
            processor = ind.processors[t]
            start_time = total_time[processor]

            for e in task.predecessors:
                parent = e.vertex
                parent_proc = ind.processors[parent.id]
                if processor != parent_proc:
                    tim = timestamps[parent.id] + parent.cost + e.cost
                    start_time = max(tim, start_time)

            timestamps[t] = start_time
            total_time[processor] = start_time + task.cost

        makespan = max(total_time)
        return ind._replace(makespan=makespan)

    def gantt(self, ind):
        timestamps = [0] * self.task_qty
        total_time = [0] * self.processor_qty

        for t in ind.sequence:
            task = self.graph[t]
            processor = ind.processors[t]
            start_time = total_time[processor]

            for e in task.predecessors:
                parent = e.vertex
                parent_proc = ind.processors[parent.id]
                if processor != parent_proc:
                    tim = timestamps[parent.id] + parent.cost + e.cost
                    start_time = max(tim, start_time)

            timestamps[t] = start_time
            total_time[processor] = start_time + task.cost

        with open("best.txt", "w+") as f:
            f.write("tid,start,duration,pid\n")
            for t in ind.sequence:
                f.write("{},{},{},{}\n".format(t, timestamps[t],
                        self.graph[t].cost, ind.processors[t]))
        call("python3 gantt.py best.txt", shell=True)

problem = "problems/morady/TG9.txt"
print(problem)
b = BB(problem, 16)
b.search()
print(b.best_solution, b.total_evaluations)
# b.gantt(b.best_solution)
