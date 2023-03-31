import time
import tracemalloc as tr

# Global variables for metrics
START_TIME = None
END_TIME = None
NUM_DATAFLY = 0
NUM_INCOGNITO = 0
NUM_MONDRIAN = 0


def monitor_time():
    """
    Prints the execution time of the function
    """
    if START_TIME is not None and END_TIME is not None:
        print(f"\nTotal execution time: {END_TIME - START_TIME}")
    else:
        print("\nTimes have not been collected")


def start_monitor_time():
    """
    Updates the global variable containing the starting time of the execution
    """
    global START_TIME
    START_TIME = time.time()


def end_monitor_time():
    """
    Updates the global variable containing the end time of the execution and
    prints the execution time
    """
    global END_TIME
    END_TIME = time.time()
    monitor_time()


# Metrics to monitor the execution time of the functions
def monitor_cost(type_of: str):
    """
    Prints the cost metric for the specified algorithm.

    :param type_of: Name of the algorithm you want to monitor.
    :type type_of: string
    """
    if type_of.lower() == "data_fly" or type_of.lower() == "datafly":
        global NUM_DATAFLY
        print("Number of generalization operations: ", NUM_DATAFLY)
    if type_of.lower() == "incognito":
        global NUM_INCOGNITO
        print(NUM_INCOGNITO)
    if type_of.lower() == "mondrian":
        global NUM_MONDRIAN
        print(NUM_MONDRIAN)


def monitor_cost_init(type_of: str):
    """
    Resets the cost metric for the specified algorithm.

    :param type_of: Name of the algorithm you want to monitor.
    :type type_of: string
    """

    if type_of.lower() == "data_fly" or type_of.lower() == "datafly":
        global NUM_DATAFLY
        NUM_DATAFLY = 0
    if type_of.lower() == "incognito":
        global NUM_INCOGNITO
        NUM_INCOGNITO = 0
    if type_of.lower() == "mondrian":
        global NUM_MONDRIAN
        NUM_MONDRIAN = 0


def monitor_cost_add(type_of: str):
    """
    Updates the cost metric for the specified algorithm.

    :param type_of: Name of the algorithm you want to monitor.
    :type type_of: string
    """
    if type_of.lower() == "data_fly" or type_of.lower() == "datafly":
        global NUM_DATAFLY
        NUM_DATAFLY = NUM_DATAFLY + 1
    if type_of.lower() == "incognito":
        global NUM_INCOGNITO
        NUM_INCOGNITO = NUM_INCOGNITO + 1
    if type_of.lower() == "mondrian":
        global NUM_MONDRIAN
        NUM_MONDRIAN = NUM_MONDRIAN + 1


def monitor_memory_consumption_start():
    """
    Starts monitoring the memory consumption of the function.
    """
    tr.start()


def monitor_memory_consumption_stop():
    """
    Finished monitoring the memory consumption of the function and prints it.
    """
    memory = tr.get_traced_memory()
    print("Peak memory use: ", memory[1])
    tr.stop()
