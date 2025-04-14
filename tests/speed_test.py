import timeit

def sort_tasks():
    # Your sorting logic here (e.g., priority, category, date sorting)
    tasks = [{"priority": "High"}, {"priority": "Low"}, {"priority": "Medium"}]
    sorted_tasks = sorted(tasks, key=lambda x: x["priority"])
    return sorted_tasks

# Measure execution time
execution_time = timeit.timeit(sort_tasks, number=1000)
print(f"Sorting Execution Time: {execution_time} seconds")
