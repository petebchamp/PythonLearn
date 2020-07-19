import numpy as np

row_count = 9
col_count = 9
sudoku = np.zeros([row_count, col_count], dtype=int)    
template = np.arange(row_count * col_count)
row_vals = np.array(range(1, row_count + 1))

pod_dict = {
	0: (0,1,2,9,10,11,18,19,20),
	1: (3,4,5,12,13,14,21,22,23),	
	2: (6,7,8,15,16,17,24,25,26),
	3: (27,28,29,36,37,38,45,46,47),
	4: (30,31,32,39,40,41,48,49,50),	
	5: (33,34,35,42,43,44,51,52,53),
	6: (54,55,56,63,64,65,72,73,74),
	7: (57,58,59,66,67,68,75,76,77),	
	8: (60,61,62,69,70,71,78,79,80),
}

#########################################
def colUnique():
    sudoku_t = np.transpose(sudoku)
    for col_num in range(col_count):
        if np.unique(sudoku_t[col_num, :row + 1]).size < row + 1:
            return False
    return True
#########################################

#########################################        
def podUnique():        
    if row == 1:
        pods = (0, 1, 2)
        pod_size = 6
    elif row == 2:
        pods = (0, 1, 2)
        pod_size = 9    
    elif row == 4:
        pods = (3, 4, 5)
        pod_size = 6
    elif row == 5:
        pods = (3, 4, 5)
        pod_size = 9
    elif row == 7:
        pods = (6, 7, 8)
        pod_size = 6 
    else:
        pods = ()
        
    for pod in pods:
        pod_mask = np.in1d(template, pod_dict[pod]).reshape(row_count, col_count)
        pod_vals = sudoku[pod_mask]
        pod_vals = pod_vals[pod_vals > 0]
        if np.unique(pod_vals).size != pod_size:
            return False

    return True
#########################################
    
#########################################    
def rowOK():
    return_val = True
        
    return_val = colUnique()
    
    #Pod unique
    if return_val:
        return_val = podUnique()
        
    return return_val
#########################################
    
#########################################
def calcLastRow():
    sudoku_t = np.transpose(sudoku)
    for col in range(col_count):
        val = np.setdiff1d(row_vals, sudoku_t[col])
        sudoku[row, col] = val[0]
#########################################


#########################################    
for row in range(row_count):

    if row < 6:
    
        np.random.shuffle(row_vals)
        sudoku[row] = row_vals
            
        if row > 0:
            while not rowOK():
                np.random.shuffle(row_vals)
                sudoku[row] = row_vals
                print(sudoku)    
    
    elif row in (6, 7):
        row_vals_last = np.zeros([9, 9 - row], dtype=int)
        for col in range(col_count):
            vals = np.setdiff1d(row_vals, sudoku[:, col])
            row_vals_last[col] = vals
            
        for arr in row_vals_last:
            np.random.shuffle(arr)
            
        row_vals = row_vals_last[:, 0]
        sudoku[row] = row_vals

        while not rowOK() or np.unique(row_vals).size < 9:
            for arr in row_vals_last:
                np.random.shuffle(arr)
            
            row_vals = row_vals_last[:, 0]
        
            sudoku[row] = row_vals
            print(sudoku)

    elif row == 8:
        calcLastRow()

print(sudoku)
#########################################
        