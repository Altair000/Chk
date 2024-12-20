import random

def generate_credit_card_number(bin_format):
    out_cc = ""
    # Sustituir x por numeros
    for i in range(15):
        if bin_format[i] in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"):
            out_cc += bin_format[i]
        elif bin_format[i] in ("x"):
            out_cc += str(random.randint(0,9))
        else:
            raise ValueError(f"Caracter no válido en el formato: {bin_format}")
            
    for i in range(10):
        checksum_check = out_cc + str(i)
        if card_luhn_checksum_is_valid(checksum_check):
            out_cc += str(i)
            break

    if len(out_cc) != 16:
        raise ValueError(f"El formato del bin debe tener 16 digitos: 654321xxxxxxxxxx ")

    return out_cc

def card_luhn_checksum_is_valid(card_number):
    sum = 0
    num_digits = len(card_number)
    oddeven = num_digits & 1

    for count in range(num_digits):
        digit = int(card_number[count])
        if not (( count & 1 ) ^ oddeven ):
            digit *= 2
        if digit > 9:
            digit -= 9
        sum += digit

    return (sum % 10) == 0

def main(bin_format, month, year, n):
    with open('tarjetas.txt', 'w') as file:
        for i in range(n):
            cc_number = generate_credit_card_number(bin_format)
            cvv = str(random.randint(100, 999))
            amount = str(random.randint(1, 20000))
            date = f"0{month}|20{year % 100}"  
            file.write(f'{cc_number}|{date}|{cvv}\n')





