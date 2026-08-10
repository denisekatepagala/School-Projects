def octal_to_decimal(octal_str):
    decimalValue = 0
    power = 0

    for digit in reversed(octal_str):
        decimalValue += int(digit) * (8 ** power)
        power += 1

    return decimalValue

def decimal_to_octal(decimal_num):
    if decimal_num == 0:
        return "0"
    
    octalValue = ""
    while decimal_num > 0:
        remainder = decimal_num % 8
        octalValue = str(remainder) + octalValue
        decimal_num //= 8

    return octalValue

def main():
    print("Choose conversion type:")
    print("1. Decimal to Octal")
    print("2. Octal to Decimal")
    choice = int(input("Enter 1 or 2: "))

    if choice == 1:
        decimalInput = int(input("Enter a decimal number: "))
        octalOutput = decimal_to_octal(decimalInput)
        print(f"The octal equivalent of decimal {decimalInput} is {octalOutput}")
    elif choice == 2:
        octalInput = input("Enter an octal number: ")
        decimalOutput = octal_to_decimal(octalInput)
        print(f"The decimal equivalent of octal {octalInput} is {decimalOutput}")
    else:
        print("Invalid choice. Please enter 1 or 2.")

main()
