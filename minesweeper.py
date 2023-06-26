import random 
import networkx as nx 

class Minesweeper:
    def __init__(self, rows, cols, mines):
        self.rows = rows 
        self.cols = cols 
        self.mines = mines 

        self.grid = nx.grid_2d_graph(rows, cols) 
        self.grid.add_edges_from([
                                     ((x, y), (x + 1, y + 1))
                                     for x in range(rows - 1)
                                     for y in range(cols - 1)
                                 ] + [
                                     ((x + 1, y), (x, y + 1))
                                     for x in range(rows - 1)
                                     for y in range(cols - 1)
                                 ], weight=1.4)

        for n in self.grid.nodes:
            self.grid.nodes[n]['value'] = 0
            self.grid.nodes[n]['revealed'] = False

        mine_positions = [i for i in range(self.rows * self.cols) if i not in [0, 15, 464, 479]]
        random.shuffle(mine_positions)

        #tested_mines = [6, 7, 8, 11, 13, 16, 17, 18]
        #mine_positions = [i for i in range(self.rows * self.cols) if i not in tested_mines]
        #random.shuffle(mine_positions)
        #random.shuffle(tested_mines)
        #mine_positions.insert(0, tested_mines[0])
        #mine_positions.insert(0, tested_mines[1])

        for i in range(self.mines):
            x = mine_positions[i] % self.rows 
            y = int(mine_positions[i] / self.rows)
            self.grid.nodes[(x, y)]['value'] = -1
        
        for n in self.grid.nodes:
            if self.value_at(n) == -1:
                continue 
            n_adj_mines = sum(1 for m in nx.neighbors(self.grid, n) if self.value_at(m) == -1)
            self.grid.nodes[n]['value'] = n_adj_mines 

    def __str__(self):
        string = ''
        for r in range(self.rows):
            for c in range(self.cols):
                if self.value_at((r, c)) == -1:
                    string = string + ' M '
                else:
                    if self.value_at((r, c)) == 0:
                        string = string + ' 0 '
                    else:
                        string = string + ' ' + str(self.value_at((r, c))) + ' '
            string = string + '\n'
        return string 

    def reveal_node(self, node):
        if self.grid.nodes[node]['revealed']:
            return []
        self.grid.nodes[node]['revealed'] = True 
        revealed_nodes = []
        if self.value_at(node) == 0:
            revealed_nodes.append((node, self.value_at(node)))
            for n in self.grid.neighbors(node):
                revealed_nodes = revealed_nodes + self.reveal_node(n)
        else:
            revealed_nodes.append((node, self.value_at(node)))
        return revealed_nodes 

    def reveal_nodes(self, nodes):
        revealed_nodes = []
        for n in nodes:
            revealed_nodes += self.reveal_node(n)
        return revealed_nodes 
    
    def reset_reveals(self):
        for n in self.grid.nodes:
            self.grid.nodes[n]["revealed"] = False 
        
    def value_at(self, node):
        return self.grid.nodes[node]["value"]

    def safe_initial(self):
        return random.choice([n for n in self.grid.nodes if self.grid.nodes[n]["value"] != -1])

def generate_board(rows, cols, mines):
    return Minesweeper(rows, cols, mines)

