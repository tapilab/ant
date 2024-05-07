import time

def import_data():    
    for i in range(10):
        print(i)
        time.sleep(1)  # Simulate a task taking some time to complete
    return "Done"