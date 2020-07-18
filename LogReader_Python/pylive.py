import matplotlib as mpl
import matplotlib.pyplot as plt
#import numpy as np

# use ggplot style for more sophisticated visuals
plt.style.use('ggplot')
mpl.rcParams['toolbar'] = 'None'

def live_plotter(x_vec,y1_data,line1,y1_data_avg,line1_avg,y2_data,line2,y2_data_avg,line2_avg,identifier='',pause_time=0.1):
   
    if line1==[]:
        
        # this is the call to matplotlib that allows dynamic plotting
        plt.ion()
#        fig = plt.figure(figsize=(15,8))
        fig, (ax, ax2) = plt.subplots(2)

        ax.set_title('Landing Page')
        ax.set_xticks([],[])
        ax.set_ylabel('Milliseconds', fontsize='large')
        ax.set_ylim([0, 1000])
#        ax.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)
        
        ax2.set_title('Personal Action Plan')
        ax2.set_xticks([],[])
        ax2.set_ylabel('Milliseconds', fontsize='large')        
        ax2.set_ylim([0, 1000])
        
        # create variables for the linse so we can later update them
        line1, = ax.plot(x_vec, y1_data, marker='o', color='blue', linewidth=1, markersize = 3)
        line1_avg, = ax.plot(x_vec, y1_data_avg, color='magenta', linewidth=0.5)        
        
        line2, = ax2.plot(x_vec, y2_data, marker='o', color='green', linewidth=1, markersize = 3)
        line2_avg, = ax2.plot(x_vec, y2_data_avg, color='tomato', linewidth=0.5)        
        
        plt.show()   
    
    # after the figure, axis, and line are created, we only need to update the y-data
    line1.set_ydata(y1_data)
    line1_avg.set_ydata(y1_data_avg)
    line2.set_ydata(y2_data)
    line2_avg.set_ydata(y2_data_avg)    
 
    #adjust limits if new data goes beyond bounds
#    if np.min(y1_data)<=line1.axes.get_ylim()[0] or np.max(y1_data)>=line1.axes.get_ylim()[1]:
#        plt.ylim([np.min(y1_data)-np.std(y1_data),np.max(y1_data)+np.std(y1_data)])
#        
#    if np.min(y2_data)<=line2.axes.get_ylim()[0] or np.max(y2_data)>=line2.axes.get_ylim()[1]:
#        plt.ylim([np.min(y2_data)-np.std(y2_data),np.max(y2_data)+np.std(y2_data)])        
    
    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
    plt.pause(pause_time)
    
    # return line so we can update it again in the next iteration
    return line1, line1_avg, line2, line2_avg