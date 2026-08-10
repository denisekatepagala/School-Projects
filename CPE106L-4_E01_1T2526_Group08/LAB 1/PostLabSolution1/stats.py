def mean(data):
    return sum(data) / len(data)

def median(data):
    data.sort()
    length = len(data)
    mid_index = length // 2
    if length % 2 == 0:
        return (data[mid_index - 1] + data[mid_index]) / 2
    else:
        return data[mid_index]

def Mode(data):
    if not data:
        raise ValueError("List is empty.")
    
    count = {}
    for value in data:
        count[value] = count.get(value, 0) + 1

    highest_freq = max(count.values())
    modes = [value for value, freq in count.items() if freq == highest_freq]

    if len(modes) == len(set(data)):
        return None

    return modes if len(modes) > 1 else modes[0]

n_values = int(input("\nHow many numbers do you want to input? "))  

data_list = []
for i in range(1, n_values + 1):
    suffix = "th"
    if i == 1:
        suffix = "st"
    elif i == 2:
        suffix = "nd"
    elif i == 3:
        suffix = "rd"
    
    number = float(input(f"Enter the {i}{suffix} number: "))
    data_list.append(number)


print("\nAverage (Mean):", mean(data_list))
print("Median:", median(data_list))
print("Most frequent (Mode):", Mode(data_list))
