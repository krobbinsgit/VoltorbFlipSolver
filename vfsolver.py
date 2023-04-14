from dimod import ConstrainedQuadraticModel
from dwave.system import LeapHybridCQMSampler
import numpy as np

# We'll define a problem instance as this:
# ([(row1 tot, row1 bombs),(row2 tot, row2 bombs)...], [(col1 tot, col1 bombs),(col2 tot, col2 bombs)...])
# Each grid square will have 4 binary variables which corresponding to ('bomb', 1, 2, 3) for a total of 4*5*5=100 variables
#x_{row}_{col}_{val}

def add_1_hot(cqm, vars, label): # Daniel Mahler wrote this one
    """Much faster than `CQM.add_discrete` for long `vars`"""
    return cqm.add_constraint_from_iterable(((v, 1) for v in vars), '==', 1, label=label)

cqm=ConstrainedQuadraticModel()
varlabels=[f'x_{row}_{col}_{val}' for row in range(5) for col in range(5) for val in ['b',1,2,3]]
for v in varlabels:
    cqm.add_variable('BINARY',v)
for row in range(5):
    for col in range(5):
        add_1_hot(cqm,(f'x_{row}_{col}_{val}' for val in ['b',1,2,3]),f'1_hot_for_{row}_{col}')
# This will make sure each grid can take at most one value
inst=([(4,1),(4,1),(6,1),(5,2),(6,1)],[(5,0),(1,4),(7,0),(6,1),(6,1)]) # taken from a real level 1 problem
#inst = ([(3,2),(5,2),(6,1),(7,0),(4,1)],[(5,0),(6,1),(3,2),(5,2),(6,1)]) # taken from a real level 1 problem

for row in range(5):
    l=[[(f'x_{row}_{col}_1',1),(f'x_{row}_{col}_2',2),(f'x_{row}_{col}_3',3)] for col in range(5)]
    l=[element for sublist in l for element in sublist]
    cqm.add_constraint_from_iterable(l,'==',rhs=inst[0][row][0],label=f'row_{row}_tot') # Should be row total constraints

for col in range(5):
    l=[[(f'x_{row}_{col}_1',1),(f'x_{row}_{col}_2',2),(f'x_{row}_{col}_3',3)] for row in range(5)]
    l=[element for sublist in l for element in sublist]
    cqm.add_constraint_from_iterable(l,'==',rhs=inst[1][col][0],label=f'col_{col}_tot') # Should be col total constraints

for row in range(5):
    cqm.add_constraint_from_iterable([(f'x_{row}_{col}_b',1) for col in range(5)],'==',rhs=inst[0][row][1],label=f'row_{row}_bomb')
    # Above should give row bomb constraints

for col in range(5):
    cqm.add_constraint_from_iterable([(f'x_{row}_{col}_b',1) for row in range(5)],'==',rhs=inst[1][col][1],label=f'col_{col}_bomb')
    # Above should give col bomb constraints

# need a visualizer function

def gridval(sol,row,col): # given a solution dictionary
    '''
    sol is a solution dictionary
    row and col are integers from 0 to 4
    '''
    if sol[f'x_{row}_{col}_b']==1:
        return('B')
    elif sol[f'x_{row}_{col}_1']==1:
        return('1')
    elif sol[f'x_{row}_{col}_2']==1:
        return('2')
    elif sol[f'x_{row}_{col}_3']==1:
        return('3')

solver=LeapHybridCQMSampler()
sample_set=solver.sample_cqm(cqm,time_limit=5)
feasible_samples= sample_set.filter(lambda d: d.is_feasible)
if len(feasible_samples)==0:
    print('No feasible solutions found.')
else:
    print (f'\nFound {len(feasible_samples)} solutions. One of them is \n ')
    sample=feasible_samples.first
    solution=sample.sample
    printable_sol=np.array([[gridval(solution,row,col) for col in range(5)] for row in range(5)])
    print(printable_sol)









