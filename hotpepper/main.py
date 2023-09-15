from getSalonList import main as getList_main
from getSalonDetail import main as getDetail_main
from toExcel import main as toExcel_main
import time

start_time = time.time()

getList_main()
processing_time = time.time() - start_time
print(f'経過時間(s）: {round(processing_time,1)}')

getDetail_main()
processing_time = time.time() - start_time
print(f'経過時間(s）: {round(processing_time,1)}')

toExcel_main()
processing_time = time.time() - start_time
print(f'経過時間(s）: {round(processing_time,1)}')

