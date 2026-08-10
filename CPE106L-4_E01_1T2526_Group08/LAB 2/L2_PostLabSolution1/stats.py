def mean(values):
    if not values:
        return 0
    return sum(values) / len(values)

def median(values):
    if not values:
        return 0
    sorted_values = sorted(values)
    size = len(sorted_values)
    mid_index = size // 2
    if size % 2 == 0:
        return (sorted_values[mid_index - 1] + sorted_values[mid_index]) / 2
    else:
        return sorted_values[mid_index]

def mode(values):
    if not values:
        return 0
    freq = {}
    for v in values:
        freq[v] = freq.get(v, 0) + 1
    max_freq = max(freq.values())
    modes = [v for v, count in freq.items() if count == max_freq]
    return modes[0]

def main():
    file_name = input("Enter the file name containing numbers: ")
    numbers = []
    try:
        with open(file_name, 'r') as f:
            for line in f:
                for word in line.split():
                    numbers.append(float(word))
    except FileNotFoundError:
        print("File not found.")
        return
    except ValueError:
        print("File contains non-numeric values.")
        return

    print("\nNumbers from file:", numbers)
    print("Mean:", mean(numbers))
    print("Median:", median(numbers))
    print("Mode:", mode(numbers))

if __name__ == "__main__":
    main()
