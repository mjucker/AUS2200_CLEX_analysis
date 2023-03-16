from numpy import array as np_array
from datetime import datetime as dt

from .defns import logger
from .dbg_parm import dbg_parm

def t_interp( ob_grid, gfile_info, grid_dt, o_df,
              time_wt=None, debug=None ) :
       """
       Time interpolation from grid to obs point
         (This allows for different formats for obs & grid date times)
         ob_grid   = grid field(lat, lon, time, level) interpolated to obs(lat,lon)
         grid_dt   = grid validity datetime object/string
         o_df      = obs dataframe
         time_wt   = gridpoint weights
 
         Assumes grid_dt and ob_dt are similar types of variables
       """
       nprt = dbg_parm.get_dbg_parm('np_dbg_len')

       lt = len(gfile_info.var_dict()['time']['attributes']['units'])
       ob_dt = [dt.strptime('{}{}'.format(od,str(ot).zfill(lt)), 
                 gfile_info.var_dict()['date']['attributes']['units']+
                 gfile_info.var_dict()['time']['attributes']['units'] ) \
                 for od,ot in zip(o_df['date'].values,o_df['time'].values) ]
       
       ind_time = grid_dt.searchsorted(ob_dt)
       logger.debug(f'ind_time: {ind_time}')

       return_wt = (time_wt == [])

       logger.debug(f'grid_dt: {grid_dt}')

       if len(grid_dt) == 1 :
          if return_wt:
             return ob_grid, [1.]*len(o_df)
          else: 
             return ob_grid

       logger.debug(f'ob_dt[:ndp]: {ob_dt[:nprt]}')

       if (time_wt is None) or return_wt :
          gdt  = list(grid_dt[ind_time])
          gdt1 = list(grid_dt[ind_time-1])
          
          time_wt = [  (g-o).total_seconds() \
                      /(g-g1).total_seconds() for g,g1,o in zip(gdt,gdt1,ob_dt) ]
   
          time_wt  = np_array(time_wt)

       logger.debug(f'time_wt: {time_wt.max()}, {time_wt.min()}')
       gti_max = np_array(ind_time).max()
       gti_min = np_array(ind_time).min()
       logger.debug(f'ind_time: {gti_max}, {gti_min}')
       logger.debug(f'grid_dt max: {grid_dt[gti_max]}, {grid_dt[gti_max-1]}')
       logger.debug(f'grid_dt min: {grid_dt[gti_min]}, {grid_dt[gti_min-1]}')

       logger.debug(f'time_wt (shape): {time_wt.shape}')
       logger.debug(f'time_wt: {time_wt}')
       logger.debug(f'obs date/time: {ob_dt}')
       logger.debug(f'grid date/time: {grid_dt[ind_time]}')
       logger.debug(f'grid date/time -1: {grid_dt[ind_time-1]}')

       iobs = list(range(len(ind_time)))
       grid0  = [ ob_grid[i,ind_time[i]  ] for i in iobs ]
       grid0  = np_array( grid0 )
       grid1  = [ ob_grid[i,ind_time[i]-1] for i in iobs ]
       grid1  = np_array( grid1 )

       logger.debug(f'grid shape: {grid0.shape}')

       # This is to catch 3d fields. It works, but not sure of its generality
       #   for 4d
       if ( grid0.shape != time_wt.shape ):
            time_wt = time_wt.repeat(grid0.shape[1]).reshape(grid0.shape)

       ob_val = (1-time_wt)*grid0 + time_wt*grid1

       logger.debug(f'grid0: {grid0}')
       logger.debug(f'grid1: {grid1}')
       logger.debug(f'ob_val: {ob_val}')

       if return_wt:
          return ob_val, time_wt
       else: 
          return ob_val


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
